"""
Операционный радар — сбор снапшота из БД и генерация рекомендаций через Ollama.
"""
from __future__ import annotations

import hashlib
import json
import re
import logging
from datetime import date, timedelta

import httpx
from django.utils import timezone

from ui import models

logger = logging.getLogger(__name__)

OLLAMA_URL   = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.1:8b"
TIMEOUT      = 120  # секунд

SYSTEM_PROMPT = """Ты — операционный ассистент отеля. Анализируешь текущее состояние CRM и выдаёшь конкретные приоритетные действия для команды.

Правила:
- Отвечай ТОЛЬКО валидным JSON без markdown-обёрток и пояснений.
- Не выдумывай факты которых нет в данных.
- Язык ответа: русский.
- Количество рекомендаций: от 3 до 7, сортировка по важности (сначала самое срочное).

Схема ответа (строго):
{
  "items": [
    {
      "title": "Краткий заголовок действия",
      "why": "Почему это важно прямо сейчас",
      "action": "Что именно сделать",
      "entity": {"type": "ticket|booking|task|null", "id": 123},
      "risk": "low|medium|high",
      "needs_approval": false,
      "tags": ["SLA", "VIP"]
    }
  ],
  "summary": "Одна фраза — главный фокус на ближайший час"
}"""

# Регулярки для маскирования ПДн
_RE_EMAIL  = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
_RE_PHONE  = re.compile(r'(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}')
_RE_CARD   = re.compile(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b')


def _mask(text: str) -> str:
    text = _RE_EMAIL.sub('[email]', text)
    text = _RE_PHONE.sub('[phone]', text)
    text = _RE_CARD.sub('[card]', text)
    return text[:400]


def _short_name(client) -> str:
    """Анна Смирнова → 'Анна С.'"""
    if not client:
        return '—'
    first = client.first_name or ''
    last  = client.last_name  or ''
    return f"{first} {last[0]}." if last else first


def build_snapshot() -> dict:
    today = timezone.localdate()
    now   = timezone.now()

    # KPI
    open_tickets     = models.Ticket.objects.filter(status_id__in=['open', 'in_progress', 'pending']).count()
    high_tickets     = models.Ticket.objects.filter(status_id__in=['open', 'in_progress'], priority_id='high').count()
    overdue_tasks    = models.Task.objects.filter(status_id__in=['open', 'in_progress'], due__lt=now).count()
    failed_tasks     = models.Task.objects.filter(status_id='failed').count()
    today_checkins   = models.Booking.objects.filter(check_in=today).count()
    today_checkouts  = models.Booking.objects.filter(check_out=today).count()
    pending_bookings = models.Booking.objects.filter(status_id='pending').count()

    # Топ тикеты — открытые, сортировка: приоритет high → SLA
    top_tickets = []
    qs_tickets = (
        models.Ticket.objects
        .filter(status_id__in=['open', 'in_progress', 'pending'])
        .select_related('client', 'booking')
        .order_by('-priority__order', 'sla_due_at')[:7]
    )
    for t in qs_tickets:
        last_msg = t.messages.filter(direction_id='inbound').order_by('-created_at').first()
        sla_overdue = bool(t.sla_due_at and t.sla_due_at < now)
        top_tickets.append({
            'id':                t.id,
            'status':            t.status_id,
            'priority':          t.priority_id,
            'subject':           _mask(t.subject),
            'client_id':         t.client_id,
            'client_name':       _short_name(t.client),
            'booking_id':        t.booking_id,
            'updated_at':        t.updated_at.isoformat() if t.updated_at else None,
            'sla_due_at':        t.sla_due_at.isoformat() if t.sla_due_at else None,
            'sla_overdue':       sla_overdue,
            'last_inbound':      _mask(last_msg.text[:240]) if last_msg else None,
        })

    # Проблемные задачи
    top_tasks = []
    qs_tasks = (
        models.Task.objects
        .filter(status_id__in=['open', 'in_progress', 'failed'])
        .select_related('assignee', 'department')
        .order_by('due')[:7]
    )
    for t in qs_tasks:
        top_tasks.append({
            'id':         t.id,
            'type':       t.type_id,
            'status':     t.status_id,
            'due':        t.due.isoformat() if t.due else None,
            'overdue':    bool(t.due and t.due < now),
            'no_assignee': t.assignee_id is None,
            'dept':       t.department.name if t.department else None,
            'ticket_id':  t.ticket_id,
            'booking_id': t.booking_id,
        })

    # Бронирования сегодня/завтра
    top_bookings = []
    qs_bookings = (
        models.Booking.objects
        .filter(
            status_id__in=['confirmed', 'in_house', 'pending'],
            check_in__lte=today + timedelta(days=1),
            check_out__gte=today,
        )
        .select_related('client', 'category')
        .order_by('check_in')[:7]
    )
    for b in qs_bookings:
        top_bookings.append({
            'id':          b.id,
            'status':      b.status_id,
            'check_in':    b.check_in.isoformat(),
            'check_out':   b.check_out.isoformat(),
            'client_id':   b.client_id,
            'client_name': _short_name(b.client),
            'category':    b.category.name if b.category else None,
            'segment':     b.client.segment_id if b.client else None,
        })

    snapshot = {
        'generated_at': now.isoformat(),
        'kpis': {
            'open_tickets':     open_tickets,
            'high_tickets':     high_tickets,
            'overdue_tasks':    overdue_tasks,
            'failed_tasks':     failed_tasks,
            'today_checkins':   today_checkins,
            'today_checkouts':  today_checkouts,
            'pending_bookings': pending_bookings,
        },
        'top_tickets':  top_tickets,
        'top_tasks':    top_tasks,
        'top_bookings': top_bookings,
        'policies': [
            {'key': 'compensation_limit', 'rule': 'Компенсации > 5000 ₽ требуют подтверждения менеджера'},
            {'key': 'late_checkout',      'rule': 'Поздний выезд после 16:00 — подтверждение дежурного'},
        ],
    }
    return snapshot


def _snapshot_hash(snapshot: dict) -> str:
    raw = json.dumps(snapshot, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def _validate(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    items = data.get('items')
    if not isinstance(items, list) or not items:
        return False
    for item in items:
        if not isinstance(item, dict):
            return False
        for field in ('title', 'why', 'action', 'risk'):
            if not item.get(field):
                return False
    return True


def call_ollama(snapshot: dict) -> dict:
    user_prompt = (
        "Вот текущий снапшот состояния CRM отеля. "
        "Сформируй рекомендации строго по заданной JSON-схеме.\n\n"
        + json.dumps(snapshot, ensure_ascii=False, indent=2)
    )
    response = httpx.post(
        OLLAMA_URL,
        json={
            "model":   OLLAMA_MODEL,
            "stream":  False,
            "options": {"temperature": 0.2, "num_predict": 1200},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
        },
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    content = response.json()["message"]["content"].strip()
    # Убрать возможную markdown-обёртку ```json ... ```
    content = re.sub(r'^```(?:json)?\s*', '', content)
    content = re.sub(r'\s*```$', '', content)
    return json.loads(content)


def generate_radar(force: bool = False) -> models.OperationalRadarReport:
    """
    Основная точка входа. Возвращает новый или последний валидный отчёт.
    force=True — игнорировать кэш по хэшу.
    """
    snapshot = build_snapshot()
    s_hash   = _snapshot_hash(snapshot)

    if not force:
        last = models.OperationalRadarReport.objects.filter(
            snapshot_hash=s_hash, is_valid=True
        ).first()
        if last:
            return last

    try:
        recommendations = call_ollama(snapshot)
        is_valid = _validate(recommendations)
        error    = '' if is_valid else 'Ответ LLM не прошёл валидацию схемы'
    except Exception as exc:
        logger.exception("Ollama error: %s", exc)
        recommendations = {}
        is_valid = False
        error    = str(exc)[:500]

    return models.OperationalRadarReport.objects.create(
        snapshot_hash=s_hash,
        snapshot=snapshot,
        recommendations=recommendations,
        ollama_model=OLLAMA_MODEL,
        is_valid=is_valid,
        error=error,
    )


def last_valid_report() -> models.OperationalRadarReport | None:
    return models.OperationalRadarReport.objects.filter(is_valid=True).first()
