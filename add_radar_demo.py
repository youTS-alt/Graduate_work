# -*- coding: utf-8 -*-
"""Добавляет интересные записи для демо Операционного радара."""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmate.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from ui import models

now   = timezone.now()
today = timezone.localdate()

smirnova = models.Client.objects.get(last_name='Смирнова')
petrov   = models.Client.objects.get(last_name='Петров')
orlova   = models.Client.objects.get(last_name='Орлова')
novikova = models.Client.objects.get(last_name='Новикова')
kim      = models.Client.objects.get(last_name='Ким')

emp_fo  = models.Employee.objects.get(user_id=1001)
emp_hk  = models.Employee.objects.get(user_id=1004)
emp_fin = models.Employee.objects.get(user_id=1003)
dept_fo = emp_fo.department
dept_hk = emp_hk.department
dept_fin = emp_fin.department

deluxe   = models.RoomCategory.objects.get(name='Deluxe Sea View')
family   = models.RoomCategory.objects.get(name='Family Suite')
flexible = models.Rate.objects.get(name='Flexible')

# ──────────────────────────────────────────────────────────
# 1. VIP-тикет — кондиционер сломан, SLA просрочен 3 часа
# ──────────────────────────────────────────────────────────
t1 = models.Ticket.objects.create(
    client=smirnova,
    subject='Кондиционер не работает третий час',
    priority_id='high',
    status_id='open',
    sla_due_at=now - timedelta(hours=3),
)
models.Message.objects.create(
    ticket=t1, channel_id='whatsapp', direction_id='inbound',
    text='Добрый день! Кондиционер в номере 305 сломан уже 3 часа. '
         'Я VIP-гость, это недопустимо. Прошу немедленно решить или переселить меня.',
)
models.Task.objects.create(
    ticket=t1, department=dept_hk, assignee=None,
    type_id='maintenance', status_id='open',
    description='Починить кондиционер номер 305. Гость VIP сегмент Gold.',
    due=now - timedelta(hours=2),
)
print('OK: тикет 1 — сломанный кондиционер VIP (SLA просрочен)')

# ──────────────────────────────────────────────────────────
# 2. Жалоба на шум — SLA истекает через 30 минут
# ──────────────────────────────────────────────────────────
t2 = models.Ticket.objects.create(
    client=petrov,
    subject='Шум из соседнего номера третью ночь подряд',
    priority_id='high',
    status_id='in_progress',
    sla_due_at=now + timedelta(minutes=30),
)
models.Message.objects.create(
    ticket=t2, channel_id='email', direction_id='inbound',
    text='Третью ночь подряд из номера 204 громкая музыка до 3 ночи. '
         'Приехал в командировку, не могу выспаться. '
         'Если сегодня не решите — требую компенсацию и рассмотрю отмену.',
)
models.Task.objects.create(
    ticket=t2, department=dept_fo, assignee=emp_fo,
    type_id='guest_support', status_id='in_progress',
    description='Урегулировать конфликт с шумом. Возможна компенсация > 5000 руб.',
    due=now + timedelta(minutes=30),
)
print('OK: тикет 2 — шум, SLA через 30 минут, возможная компенсация')

# ──────────────────────────────────────────────────────────
# 3. Заезд сегодня — Platinum гость с нестандартными пожеланиями
# ──────────────────────────────────────────────────────────
b_platinum = models.Booking.objects.create(
    client=orlova,
    category=deluxe,
    rate=flexible,
    check_in=today,
    check_out=today + timedelta(days=3),
    status_id='confirmed',
    source_id='loyalty',
    total_cost=Decimal('87600.00'),
)
t3 = models.Ticket.objects.create(
    client=orlova, booking=b_platinum,
    subject='Заезд сегодня в 23:00 — спецпожелания Platinum',
    priority_id='medium', status_id='open',
    sla_due_at=now + timedelta(hours=3),
)
models.Message.objects.create(
    ticket=t3, channel_id='email', direction_id='inbound',
    text='Заезжаю сегодня поздно около 23:00. '
         'Прошу подготовить: тихую подушку, белое сухое вино в номере. '
         'Также — я путешествую с котом, надеюсь это не проблема?',
)
models.Task.objects.create(
    ticket=t3, booking=b_platinum, department=dept_hk, assignee=emp_hk,
    type_id='room_setup', status_id='open',
    description='Заезд Platinum клиента в 23:00. Тихая подушка, вино. Уточнить политику по животным.',
    due=now + timedelta(hours=3),
)
print('OK: тикет 3 — заезд Platinum сегодня в 23:00')

# ──────────────────────────────────────────────────────────
# 4. Провальная задача — номер не убрали к заезду
# ──────────────────────────────────────────────────────────
b_kim = models.Booking.objects.filter(client=kim).first()
models.Task.objects.create(
    booking=b_kim, department=dept_hk, assignee=emp_hk,
    type_id='room_setup', status_id='failed',
    description='Подготовить номер 401 к заезду семьи Ким: детская кроватка, гипоаллергенное постельное. '
                'Задача провалена — горничная заболела, замены нет.',
    due=now - timedelta(hours=5),
)
print('OK: задача failed — номер не убран к заезду (горничная заболела)')

# ──────────────────────────────────────────────────────────
# 5. Зависший платёж 3 дня, карта отклонена
# ──────────────────────────────────────────────────────────
b_stuck = models.Booking.objects.create(
    client=novikova,
    category=family,
    rate=flexible,
    check_in=today + timedelta(days=2),
    check_out=today + timedelta(days=5),
    status_id='pending',
    source_id='website',
    total_cost=Decimal('54000.00'),
)
stuck_pay = models.Payment.objects.create(
    booking=b_stuck,
    amount=Decimal('54000.00'),
    method_id='card', status_id='pending',
    provider_ref='pay_stuck_novikova',
)
models.PaymentEvent.objects.create(
    payment=stuck_pay, status_id='created',
    payload={'ref': 'pay_stuck_novikova', 'attempts': 3, 'last_error': 'insufficient_funds'},
    source='payments_service',
)
t5 = models.Ticket.objects.create(
    client=novikova, booking=b_stuck,
    subject='Оплата не проходит — карта отклонена трижды',
    priority_id='medium', status_id='open',
    sla_due_at=now + timedelta(hours=6),
)
models.Message.objects.create(
    ticket=t5, channel_id='phone', direction_id='inbound',
    text='Три раза пыталась оплатить, карта не проходит. '
         'Заезд послезавтра, очень переживаю. Можно оплатить по QR или на сайте другой картой?',
)
print('OK: тикет 5 — зависший платёж, заезд послезавтра')

# ──────────────────────────────────────────────────────────
# 6. Эскалация — гость угрожает написать отзыв на Booking.com
# ──────────────────────────────────────────────────────────
t6 = models.Ticket.objects.create(
    client=kim,
    subject='Угроза негативного отзыва — несоответствие номера фото',
    priority_id='critical', status_id='open',
    sla_due_at=now + timedelta(hours=1),
)
models.Message.objects.create(
    ticket=t6, channel_id='telegram', direction_id='inbound',
    text='Номер совсем не соответствует фотографиям на сайте! '
         'На фото вид на море, а у нас окна на парковку. '
         'Ребёнок расстроен. Либо переселяете нас, либо я прямо сейчас пишу отзыв на Booking.com.',
)
models.Task.objects.create(
    ticket=t6, department=dept_fo, assignee=emp_fo,
    type_id='guest_support', status_id='open',
    description='Срочно! Гость Ким угрожает отзывом. Проверить доступность номера с видом на море, предложить апгрейд.',
    due=now + timedelta(hours=1),
)
print('OK: тикет 6 — угроза отзывом на Booking.com, critical')

print('\nВсе записи добавлены. Нажми «Обновить» на дашборде.')
