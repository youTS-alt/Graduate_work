import datetime as dt
import re
from pathlib import Path

from django.conf import settings
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from ui import models as db
from ui import radar as ai_radar
from ui import agent as ai_agent

NAV_ITEMS = [
    {'label': 'Главная', 'url_name': 'ui:dashboard', 'icon': '⌂'},
    {'label': 'Гости', 'url_name': 'ui:guests_list', 'icon': '👥'},
    {'label': 'Бронирования', 'url_name': 'ui:bookings_list', 'icon': '🛏'},
    {'label': 'Обращения', 'url_name': 'ui:tickets_list', 'icon': '✉'},
    {'label': 'Задачи', 'url_name': 'ui:tasks_board', 'icon': '✓'},
    {'label': 'Справочники', 'url_name': 'ui:catalog', 'icon': '☰'},
    {'label': 'ИИ-Консьерж', 'url_name': 'ui:ai_console', 'icon': '✦'},
    {'label': 'Администрирование', 'url_name': 'ui:admin_panel', 'icon': '⚙'},
    {'label': 'Журнал аудита', 'url_name': 'ui:audit_log', 'icon': '⎙'},
]

GUESTS = [
    {'id': 1, 'name': 'Анна Смирнова', 'segment': 'ВИП', 'email': 'anna@guestmail.com', 'phone': '+7 900 100-22-33', 'city': 'Москва', 'status': 'Активен', 'preference': 'Поздний выезд'},
    {'id': 2, 'name': 'Илья Петров', 'segment': 'Бизнес', 'email': 'ilya@worktrip.io', 'phone': '+7 900 200-33-44', 'city': 'Санкт-Петербург', 'status': 'Ожидает', 'preference': 'Трансфер в аэропорт'},
    {'id': 3, 'name': 'Мария Ким', 'segment': 'Семья', 'email': 'maria@travelbox.me', 'phone': '+7 900 300-44-55', 'city': 'Казань', 'status': 'Активен', 'preference': 'Детская кроватка'},
    {'id': 4, 'name': 'Олег Васильев', 'segment': 'Отдых', 'email': 'oleg@sunroute.ru', 'phone': '+7 900 400-55-66', 'city': 'Екатеринбург', 'status': 'Новый', 'preference': 'Экскурсии'},
    {'id': 5, 'name': 'Елена Орлова', 'segment': 'Лояльность (золото)', 'email': 'elena@stayclub.com', 'phone': '+7 900 500-66-77', 'city': 'Сочи', 'status': 'Активен', 'preference': 'Вид на море'},
]

BOOKINGS = [
    {'id': 101, 'code': 'HM-101', 'guest': 'Анна Смирнова', 'dates': '12 апр — 16 апр', 'room': 'Делюкс (море)', 'status': 'Подтверждено', 'amount': '84 000 ₽', 'source': 'Сайт'},
    {'id': 102, 'code': 'HM-102', 'guest': 'Илья Петров', 'dates': '18 апр — 20 апр', 'room': 'Бизнес-люкс', 'status': 'Черновик', 'amount': '42 500 ₽', 'source': 'Телефон'},
    {'id': 103, 'code': 'HM-103', 'guest': 'Мария Ким', 'dates': '22 апр — 27 апр', 'room': 'Семейный номер', 'status': 'Заезд', 'amount': '97 200 ₽', 'source': 'Онлайн-агентство'},
    {'id': 104, 'code': 'HM-104', 'guest': 'Олег Васильев', 'dates': '01 мая — 05 мая', 'room': 'Стандарт (сад)', 'status': 'Отменено', 'amount': '36 400 ₽', 'source': 'Сайт'},
    {'id': 105, 'code': 'HM-105', 'guest': 'Елена Орлова', 'dates': '08 мая — 10 мая', 'room': 'Премиум (море)', 'status': 'Завершено', 'amount': '58 900 ₽', 'source': 'Корпоративный договор'},
]

TICKETS = [
    {'id': 201, 'subject': 'Поздний выезд', 'guest': 'Анна Смирнова', 'channel': 'Ватсап', 'status': 'Открыто', 'priority': 'Высокий', 'updated': '5 минут назад'},
    {'id': 202, 'subject': 'Трансфер в аэропорт', 'guest': 'Илья Петров', 'channel': 'Эл. почта', 'status': 'В работе', 'priority': 'Средний', 'updated': '20 минут назад'},
    {'id': 203, 'subject': 'Детская кроватка', 'guest': 'Мария Ким', 'channel': 'Телеграм', 'status': 'Ожидание', 'priority': 'Средний', 'updated': '1 час назад'},
    {'id': 204, 'subject': 'Счёт для компании', 'guest': 'Олег Васильев', 'channel': 'Портал', 'status': 'Решено', 'priority': 'Низкий', 'updated': 'Сегодня'},
    {'id': 205, 'subject': 'Апгрейд номера', 'guest': 'Елена Орлова', 'channel': 'Телефон', 'status': 'Закрыто', 'priority': 'Средний', 'updated': 'Вчера'},
]

TASK_COLUMNS = {
    'Новые': [
        {'title': 'Подтвердить поздний выезд', 'owner': 'Служба приёма', 'due': 'Сегодня, 16:00', 'ticket': '#201'},
        {'title': 'Проверить статус оплаты HM-102', 'owner': 'Финансы', 'due': 'Сегодня, 18:00', 'ticket': '#102'},
    ],
    'В работе': [
        {'title': 'Организовать трансфер', 'owner': 'Консьерж', 'due': 'Завтра, 07:30', 'ticket': '#202'},
        {'title': 'Подготовить семейный приветственный набор', 'owner': 'Служба уборки', 'due': 'Завтра, 12:00', 'ticket': '#203'},
    ],
    'Сделано': [
        {'title': 'Отправить закрывающие документы', 'owner': 'Финансы', 'due': 'Готово', 'ticket': '#204'},
    ],
    'Отменено': [
        {'title': 'Отменить бронирование HM-104', 'owner': 'Служба приёма', 'due': 'Отменено', 'ticket': '#104'},
    ],
}

CATALOG_SECTIONS = [
    {'name': 'Категории номеров', 'count': 8, 'description': 'Список тарифных категорий и вместимости.'},
    {'name': 'Номера', 'count': 42, 'description': 'Карточки номеров, этажи и статусы готовности.'},
    {'name': 'Тарифы', 'count': 12, 'description': 'Базовые и сезонные тарифы для каналов продаж.'},
    {'name': 'Правила отмены', 'count': 5, 'description': 'Шаблоны штрафов и дедлайнов отмены.'},
    {'name': 'Услуги и предложения', 'count': 16, 'description': 'Пакеты, спа, трансферы и допродажи.'},
]

AUDIT_ROWS = [
    {'time': '23.03.2026 09:10', 'entity': 'Обращение #201', 'action': 'ИИ предложил ответ гостю', 'actor': 'ХотелМейт ИИ', 'risk': 'Предупреждение'},
    {'time': '23.03.2026 08:45', 'entity': 'Бронирование HM-102', 'action': 'Изменение статуса', 'actor': 'Мария И.', 'risk': 'Низкий'},
    {'time': '23.03.2026 08:02', 'entity': 'Гость #5', 'action': 'Обновлены предпочтения', 'actor': 'Елена С.', 'risk': 'Низкий'},
    {'time': '22.03.2026 21:30', 'entity': 'Политика агента', 'action': 'Действие требует подтверждения', 'actor': 'Администратор', 'risk': 'Высокий'},
    {'time': '22.03.2026 18:14', 'entity': 'Задача #88', 'action': 'Задача закрыта', 'actor': 'Служба приёма', 'risk': 'Низкий'},
]


def base_context(active_page: str, title: str, breadcrumbs: list[dict]) -> dict:
    return {
        'nav_items': NAV_ITEMS,
        'active_page': active_page,
        'page_title': title,
        'breadcrumbs': breadcrumbs,
        'notice': 'Запись добавлена в журнал аудита',
    }


def dashboard(request: HttpRequest) -> HttpResponse:
    context = base_context('Главная', 'Главная', [{'label': 'Главная'}])

    report = ai_radar.last_valid_report()
    radar_items   = report.recommendations.get('items', [])   if report else []
    radar_summary = report.recommendations.get('summary', '') if report else ''

    open_tickets  = db.Ticket.objects.filter(status_id__in=['open', 'in_progress', 'pending']).count()
    high_tickets  = db.Ticket.objects.filter(status_id__in=['open', 'in_progress'], priority_id='high').count()
    active_guests = db.Client.objects.count()
    tasks_wip     = db.Task.objects.filter(status_id='in_progress').count()
    today         = timezone.localdate()
    today_checkins = db.Booking.objects.filter(check_in=today).count()

    context.update({
        'metrics': [
            {'label': 'Гостей в базе',        'value': active_guests,  'delta': ''},
            {'label': 'Заезды сегодня',        'value': today_checkins, 'delta': ''},
            {'label': 'Открытые обращения',    'value': open_tickets,   'delta': f'{high_tickets} высокого приоритета'},
            {'label': 'Задачи в работе',       'value': tasks_wip,      'delta': ''},
        ],
        'radar_items':   radar_items,
        'radar_summary': radar_summary,
        'radar_report':  report,
        'recent_bookings': db.Booking.objects.select_related('client').order_by('-created_at', '-id')[:3],
        'recent_tickets':  db.Ticket.objects.select_related('client', 'booking').order_by('-updated_at', '-id')[:3],
    })
    return render(request, 'ui/dashboard.html', context)


@require_POST
def refresh_radar(request: HttpRequest) -> HttpResponse:
    ai_radar.generate_radar(force=True)
    return redirect('ui:dashboard')


def guests_list(request: HttpRequest) -> HttpResponse:
    context = base_context('Гости', 'Гости', [{'label': 'Главная', 'url_name': 'ui:dashboard'}, {'label': 'Гости'}])
    qs = db.Client.objects.all().prefetch_related('contact_channels').order_by('-id')
    q = request.GET.get('q', '').strip()
    segment = request.GET.get('segment', '').strip()
    if q:
        qs = qs.filter(
            Q(last_name__icontains=q) | Q(first_name__icontains=q) |
            Q(contact_channels__value__icontains=q)
        ).distinct()
    if segment:
        qs = qs.filter(segment_id=segment)
    segments = db.Client.objects.exclude(segment__isnull=True).values_list('segment_id', flat=True).distinct().order_by('segment_id')
    context.update({'guests': qs, 'q': q, 'selected_segment': segment, 'segments': segments})
    return render(request, 'ui/guests_list.html', context)


def guest_detail(request: HttpRequest, id: int) -> HttpResponse:
    guest = get_object_or_404(
        db.Client.objects.prefetch_related('contact_channels', 'consents'),
        pk=id,
    )
    context = base_context('Гости', str(guest), [
        {'label': 'Главная', 'url_name': 'ui:dashboard'},
        {'label': 'Гости', 'url_name': 'ui:guests_list'},
        {'label': str(guest)},
    ])
    booking_ids = list(
        db.Booking.objects.filter(client=guest).order_by('-created_at', '-id').values_list('id', flat=True)[:50]
    )
    ticket_ids = list(
        db.Ticket.objects.filter(client=guest).order_by('-updated_at', '-id').values_list('id', flat=True)[:50]
    )

    activity_filter = Q(entity='Client', entity_id=guest.id)
    if booking_ids:
        activity_filter |= Q(entity='Booking', entity_id__in=booking_ids)
    if ticket_ids:
        activity_filter |= Q(entity='Ticket', entity_id__in=ticket_ids)

    context.update(
        {
            'guest': guest,
            'contact_channels': guest.contact_channels.all().order_by('-is_primary', 'priority', 'id'),
            'consents': guest.consents.all().order_by('-obtained_at', '-id'),
            'loyalty_level': guest.loyalty_level,
            'loyalty_points': guest.loyalty_points,
            'guest_bookings': (
                db.Booking.objects.filter(client=guest)
                .select_related('category')
                .order_by('-created_at', '-id')[:20]
            ),
            'guest_tickets': (
                db.Ticket.objects.filter(client=guest)
                .select_related('booking')
                .order_by('-updated_at', '-id')[:20]
            ),
            'activity_history': (
                db.AuditLog.objects.filter(activity_filter)
                .select_related('actor_employee')
                .order_by('-created_at', '-id')[:30]
            ),
        }
    )
    return render(request, 'ui/guest_detail.html', context)


def bookings_list(request: HttpRequest) -> HttpResponse:
    context = base_context('Бронирования', 'Бронирования', [{'label': 'Главная', 'url_name': 'ui:dashboard'}, {'label': 'Бронирования'}])
    qs = db.Booking.objects.all().select_related('client', 'category', 'rate', 'room').order_by('-id')
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    source = request.GET.get('source', '').strip()
    if q:
        qs = qs.filter(
            Q(client__last_name__icontains=q) | Q(client__first_name__icontains=q) |
            Q(room__room_number__icontains=q)
        ).distinct()
    if status:
        qs = qs.filter(status_id=status)
    if source:
        qs = qs.filter(source_id=source)
    statuses = db.Booking.objects.values_list('status_id', flat=True).distinct().order_by('status_id')
    sources = db.Booking.objects.values_list('source_id', flat=True).distinct().order_by('source_id')
    context.update({
        'bookings': qs, 'q': q,
        'selected_status': status, 'selected_source': source,
        'statuses': statuses, 'sources': sources,
    })
    return render(request, 'ui/bookings_list.html', context)


def booking_detail(request: HttpRequest, id: int) -> HttpResponse:
    booking = get_object_or_404(
        db.Booking.objects.select_related('client', 'category', 'rate', 'room').prefetch_related('guests', 'items', 'payments'),
        pk=id,
    )
    context = base_context('Бронирования', f'#{booking.id}', [
        {'label': 'Главная', 'url_name': 'ui:dashboard'},
        {'label': 'Бронирования', 'url_name': 'ui:bookings_list'},
        {'label': f'#{booking.id}'},
    ])
    context.update(
        {
            'booking': booking,
            'booking_guests': booking.guests.all().order_by('id'),
            'booking_items': booking.items.select_related('service', 'offer').all().order_by('id'),
            'payments': booking.payments.all().order_by('-id'),
            'status_history': db.AuditLog.objects.filter(entity='Booking', entity_id=booking.id).order_by('-created_at')[:20],
        }
    )
    return render(request, 'ui/booking_detail.html', context)


def tickets_list(request: HttpRequest) -> HttpResponse:
    context = base_context('Обращения', 'Обращения', [{'label': 'Главная', 'url_name': 'ui:dashboard'}, {'label': 'Обращения'}])
    qs = db.Ticket.objects.all().select_related('client', 'booking').order_by('-updated_at', '-id')
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    priority = request.GET.get('priority', '').strip()
    if q:
        qs = qs.filter(
            Q(subject__icontains=q) | Q(client__last_name__icontains=q) | Q(client__first_name__icontains=q)
        ).distinct()
    if status:
        qs = qs.filter(status_id=status)
    if priority:
        qs = qs.filter(priority_id=priority)
    statuses = db.Ticket.objects.values_list('status_id', flat=True).distinct().order_by('status_id')
    priorities = db.Ticket.objects.values_list('priority_id', flat=True).distinct().order_by('priority_id')
    context.update({
        'tickets': qs, 'q': q,
        'selected_status': status, 'selected_priority': priority,
        'statuses': statuses, 'priorities': priorities,
    })
    return render(request, 'ui/tickets_list.html', context)


def ticket_detail(request: HttpRequest, id: int) -> HttpResponse:
    ticket = get_object_or_404(
        db.Ticket.objects.select_related('client', 'booking').prefetch_related('messages', 'tasks'),
        pk=id,
    )
    context = base_context('Обращения', ticket.subject, [
        {'label': 'Главная', 'url_name': 'ui:dashboard'},
        {'label': 'Обращения', 'url_name': 'ui:tickets_list'},
        {'label': ticket.subject},
    ])

    context.update(
        {
            'ticket': ticket,
            'messages': ticket.messages.select_related('contact_channel', 'template', 'campaign').all().order_by('created_at', 'id'),
            'ticket_tasks': ticket.tasks.select_related('department', 'assignee').all().order_by('-created_at', '-id'),
            'concierge_panels': {'summary': '', 'reply': '', 'services': [], 'actions': []},
        }
    )
    return render(request, 'ui/ticket_detail.html', context)

def tasks_board(request: HttpRequest) -> HttpResponse:
    context = base_context('Задачи', 'Задачи', [{'label': 'Главная', 'url_name': 'ui:dashboard'}, {'label': 'Задачи'}])
    tasks = (
        db.Task.objects.all()
        .select_related('department', 'assignee', 'ticket', 'booking')
        .order_by('-created_at', '-id')
    )
    task_columns: dict[str, list[db.Task]] = {'open': [], 'in_progress': [], 'done': [], 'failed': []}
    for task in tasks:
        task_columns.setdefault(task.status_id or 'open', []).append(task)

    context['task_columns'] = task_columns
    return render(request, 'ui/tasks_board.html', context)


def catalog(request: HttpRequest) -> HttpResponse:
    context = base_context('Справочники', 'Справочники', [{'label': 'Главная', 'url_name': 'ui:dashboard'}, {'label': 'Справочники'}])
    context['catalog_sections'] = CATALOG_SECTIONS
    return render(request, 'ui/catalog.html', context)


def ai_console(request: HttpRequest) -> HttpResponse:
    context = base_context('ИИ-Консьерж', 'ИИ-Консьерж', [
        {'label': 'Главная', 'url_name': 'ui:dashboard'}, {'label': 'ИИ-Консьерж'},
    ])
    sessions = db.AgentSession.objects.order_by('-created_at')[:30]

    # Открытая сессия из GET-параметра
    session_id = request.GET.get('session')
    active_session = None
    messages = []
    if session_id:
        active_session = db.AgentSession.objects.filter(pk=session_id).first()
        if active_session:
            messages = list(active_session.messages.order_by('created_at'))

    context.update({
        'sessions': sessions,
        'active_session': active_session,
        'messages': messages,
    })
    return render(request, 'ui/ai_console.html', context)


@require_POST
def ai_new_session(request: HttpRequest) -> HttpResponse:
    session = db.AgentSession.objects.create()
    return redirect(f"{request.build_absolute_uri('/ai/')}?session={session.pk}")


@require_POST
def ai_chat(request: HttpRequest) -> JsonResponse:
    session_id = request.POST.get('session_id')
    user_text  = (request.POST.get('message') or '').strip()
    if not user_text:
        return JsonResponse({'error': 'empty'}, status=400)

    session = db.AgentSession.objects.filter(pk=session_id).first()
    if not session:
        return JsonResponse({'error': 'session not found'}, status=404)

    reply = ai_agent.chat(session, user_text)
    return JsonResponse({'reply': reply, 'session_title': session.title})


def admin_panel(request: HttpRequest) -> HttpResponse:
    context = base_context('Администрирование', 'Администрирование', [{'label': 'Главная', 'url_name': 'ui:dashboard'}, {'label': 'Администрирование'}])
    context.update({
        'departments': db.Department.objects.order_by('name'),
        'employees': db.Employee.objects.select_related('department').order_by('full_name'),
        'roles': db.Role.objects.order_by('code'),
    })
    return render(request, 'ui/admin_panel.html', context)


def audit_log(request: HttpRequest) -> HttpResponse:
    context = base_context('Журнал аудита', 'Журнал аудита', [{'label': 'Главная', 'url_name': 'ui:dashboard'}, {'label': 'Журнал аудита'}])
    context['audit_rows'] = (
        db.AuditLog.objects.all()
        .select_related('actor_employee')
        .order_by('-created_at', '-id')[:200]
    )
    return render(request, 'ui/audit_log.html', context)


def _normalize_url_path_to_filename_prefix(url_path: str) -> str:
    path = (url_path or '').strip()
    path = path.split('?', 1)[0].split('#', 1)[0]
    path = path.strip('/')
    if not path:
        path = 'home'
    path = path.replace('/', '__')
    path = re.sub(r'[^0-9A-Za-zА-Яа-я_\\-]+', '_', path)
    path = re.sub(r'_+', '_', path).strip('_')
    return path or 'home'


@require_POST
def save_page_screenshot(request: HttpRequest) -> JsonResponse:
    image = request.FILES.get('image')
    url_path = request.POST.get('url_path', '') or ''
    if not image:
        return JsonResponse({'ok': False, 'error': 'missing image'}, status=400)

    prefix = _normalize_url_path_to_filename_prefix(url_path)
    timestamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{prefix}_{timestamp}.png'

    target_dir = Path(settings.MEDIA_ROOT) / 'auto_screenshots'
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename

    with target_path.open('wb') as f:
        for chunk in image.chunks():
            f.write(chunk)

    return JsonResponse({'ok': True, 'filename': filename, 'url_path': url_path})



