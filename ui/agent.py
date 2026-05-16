# -*- coding: utf-8 -*-
"""
ИИ-чат консьерж: контекст из БД + Ollama.
"""
from __future__ import annotations

import re
import logging

import httpx
from django.utils import timezone

from ui import models

logger = logging.getLogger(__name__)

OLLAMA_URL   = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.1:8b"
TIMEOUT      = 120

SYSTEM_PROMPT = """Ты — ИИ-ассистент отеля HotelMate. Помогаешь сотрудникам быстро получать информацию из CRM и принимать решения.

Правила:
- Отвечай по-русски, кратко и конкретно.
- Не выдумывай данные которых нет в контексте.
- Если данных нет — честно скажи "в системе этой информации нет".
- Для рискованных действий (компенсации > 5000 ₽, отмены бронирований) напоминай что требуется подтверждение менеджера.
- Когда предлагаешь шаблон ответа гостю — обозначай это явно.
"""


# ──────────────────────────────────────────────────────────
# Сборка контекста из БД
# ──────────────────────────────────────────────────────────

def _kpi_block() -> str:
    now   = timezone.now()
    today = timezone.localdate()
    open_t  = models.Ticket.objects.filter(status_id__in=['open', 'in_progress', 'pending']).count()
    high_t  = models.Ticket.objects.filter(status_id__in=['open', 'in_progress'], priority_id__in=['high', 'critical']).count()
    over_t  = models.Task.objects.filter(status_id__in=['open', 'in_progress'], due__lt=now).count()
    checkin = models.Booking.objects.filter(check_in=today).count()
    return (
        f"[KPI сейчас] Открытых тикетов: {open_t} ({high_t} высокого/критического приор.). "
        f"Просроченных задач: {over_t}. Заездов сегодня: {checkin}."
    )


def _ticket_block(ticket_id: int) -> str:
    try:
        t = models.Ticket.objects.select_related('client', 'booking').get(pk=ticket_id)
    except models.Ticket.DoesNotExist:
        return f"Тикет #{ticket_id} не найден."
    msgs = t.messages.order_by('-created_at')[:3]
    lines = [
        f"Тикет #{t.id}: «{t.subject}»",
        f"  Статус: {t.status_id} | Приоритет: {t.priority_id}",
        f"  Клиент: {t.client} (id={t.client_id})",
        f"  SLA: {t.sla_due_at.strftime('%d.%m %H:%M') if t.sla_due_at else '—'}",
    ]
    if t.booking:
        b = t.booking
        lines.append(f"  Бронирование #{b.id}: {b.check_in}–{b.check_out}, статус {b.status_id}")
    for m in reversed(list(msgs)):
        lines.append(f"  [{m.direction_id}] {m.content[:300]}")
    return "\n".join(lines)


def _client_block(name: str) -> str:
    qs = models.Client.objects.filter(last_name__icontains=name) | \
         models.Client.objects.filter(first_name__icontains=name)
    qs = qs.distinct()[:3]
    if not qs:
        return f"Клиент «{name}» не найден в базе."
    lines = []
    for c in qs:
        bookings = models.Booking.objects.filter(client=c).order_by('-check_in')[:3]
        tickets  = models.Ticket.objects.filter(client=c, status_id__in=['open','in_progress']).count()
        lines.append(
            f"Клиент: {c} (id={c.id}), сегмент={c.segment_id or '—'}, "
            f"лояльность={c.loyalty_level_id or '—'}, баллы={c.loyalty_points}"
        )
        for b in bookings:
            lines.append(f"  Бронирование #{b.id}: {b.check_in}–{b.check_out} [{b.status_id}]")
        lines.append(f"  Открытых тикетов: {tickets}")
    return "\n".join(lines)


def _booking_block(booking_id: int) -> str:
    try:
        b = models.Booking.objects.select_related('client', 'category', 'rate', 'room').get(pk=booking_id)
    except models.Booking.DoesNotExist:
        return f"Бронирование #{booking_id} не найдено."
    items = b.items.select_related('service').all()
    lines = [
        f"Бронирование #{b.id}:",
        f"  Клиент: {b.client} (id={b.client_id})",
        f"  Категория: {b.category} | Номер: {b.room or '—'}",
        f"  Тариф: {b.rate} | Питание: {b.rate.meal_plan_id if b.rate else '—'}",
        f"  Даты: {b.check_in} – {b.check_out}",
        f"  Статус: {b.status_id} | Источник: {b.source_id}",
        f"  Сумма: {b.total_cost} ₽",
    ]
    if b.cancel_reason:
        lines.append(f"  Отмена: {b.cancel_reason} (штраф {b.cancel_penalty} ₽)")
    for item in items:
        lines.append(f"  Позиция: {item.item_type} — {item.service or '—'} x{item.quantity} = {item.amount} ₽")
    return "\n".join(lines)


_RE_TICKET  = re.compile(r'тикет[а-я]*\s*[#№]?\s*(\d+)', re.IGNORECASE)
_RE_BOOKING = re.compile(r'бронирован[а-я]*\s*[#№]?\s*(\d+)', re.IGNORECASE)


def build_chat_context(question: str) -> str:
    """Собирает текстовый блок контекста из БД под конкретный вопрос."""
    parts = [_kpi_block()]

    # Упоминание тикета
    for m in _RE_TICKET.finditer(question):
        parts.append(_ticket_block(int(m.group(1))))

    # Упоминание бронирования
    for m in _RE_BOOKING.finditer(question):
        parts.append(_booking_block(int(m.group(1))))

    # Упоминание имени — ищем клиента
    # Простая эвристика: слова с заглавной буквы, не в начале предложения
    name_candidates = re.findall(r'(?<=[а-яё\s])([А-ЯЁ][а-яё]{2,})', question)
    for name in name_candidates[:2]:
        result = _client_block(name)
        if 'не найден' not in result:
            parts.append(result)

    return "\n\n".join(parts)


# ──────────────────────────────────────────────────────────
# Вызов Ollama
# ──────────────────────────────────────────────────────────

def chat(session: models.AgentSession, user_text: str) -> str:
    """
    Отправляет сообщение пользователя в Ollama с контекстом и историей.
    Сохраняет оба сообщения. Возвращает текст ответа.
    """
    # Сохраняем вопрос
    models.AgentMessage.objects.create(
        session=session,
        role=models.AgentMessage.ROLE_USER,
        content=user_text,
    )

    # История (последние 10 пар)
    history = list(session.messages.order_by('created_at')[:20])
    ollama_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Контекст из БД — добавляем к первому user-сообщению в этой цепочке
    context = build_chat_context(user_text)
    for i, msg in enumerate(history):
        content = msg.content
        if i == 0 and msg.role == models.AgentMessage.ROLE_USER:
            content = f"[Контекст из CRM]\n{context}\n\n[Вопрос]\n{content}"
        ollama_messages.append({"role": msg.role, "content": content})

    try:
        resp = httpx.post(
            OLLAMA_URL,
            json={
                "model":   OLLAMA_MODEL,
                "stream":  False,
                "options": {"temperature": 0.3, "num_predict": 800},
                "messages": ollama_messages,
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        reply = resp.json()["message"]["content"].strip()
    except Exception as exc:
        logger.exception("Ollama chat error: %s", exc)
        reply = f"Ошибка соединения с моделью: {exc}"

    # Сохраняем ответ
    models.AgentMessage.objects.create(
        session=session,
        role=models.AgentMessage.ROLE_ASSISTANT,
        content=reply,
    )

    # Обновляем заголовок сессии по первому вопросу
    if not session.title:
        session.title = user_text[:80]
        session.save(update_fields=['title'])

    return reply
