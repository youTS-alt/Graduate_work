from __future__ import annotations

from dataclasses import dataclass
from typing import Type

from django import forms
from django.forms import modelform_factory
from django.db import models as dj_models
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from ui import models


@dataclass(frozen=True)
class CrudModelSpec:
    slug: str
    model: Type[dj_models.Model]
    title: str
    list_fields: tuple[str, ...]


# Маппинг: имя модели → {имя_поля: домен_в_LookupValue}
# Оставлены только поля которые остались обычными CharField (не FK)
LOOKUP_FIELD_DOMAINS: dict[str, dict[str, str]] = {
    'AuditLog': {'action': 'audit_action', 'risk': 'risk_level'},
}

CRUD_MODELS: dict[str, CrudModelSpec] = {
    'clients': CrudModelSpec('clients', models.Client, 'Клиенты', ('id', 'last_name', 'first_name', 'segment', 'created_at')),
    'contact-channels': CrudModelSpec('contact-channels', models.ContactChannel, 'Контактные каналы', ('id', 'client', 'type', 'value', 'is_primary')),
    'consents': CrudModelSpec('consents', models.Consent, 'Согласия', ('id', 'client', 'type', 'status', 'obtained_at')),
    'room-categories': CrudModelSpec('room-categories', models.RoomCategory, 'Категории номеров', ('id', 'name', 'capacity', 'updated_at')),
    'rooms': CrudModelSpec('rooms', models.Room, 'Номера', ('id', 'room_number', 'category', 'state', 'updated_at')),
    'rates': CrudModelSpec('rates', models.Rate, 'Тарифы', ('id', 'name', 'meal_plan', 'active', 'updated_at')),
    'cancellation-rules': CrudModelSpec('cancellation-rules', models.CancellationRule, 'Правила отмены', ('id', 'rate', 'deadline_hours', 'updated_at')),
    'services': CrudModelSpec('services', models.Service, 'Услуги', ('id', 'name', 'price', 'active', 'updated_at')),
    'offers': CrudModelSpec('offers', models.Offer, 'Предложения', ('id', 'name', 'category', 'rate', 'start_date', 'end_date')),
    'offer-services': CrudModelSpec('offer-services', models.OfferService, 'Состав предложений', ('id', 'offer', 'service', 'quantity', 'created_at')),
    'bookings': CrudModelSpec('bookings', models.Booking, 'Бронирования', ('id', 'client', 'category', 'rate', 'check_in', 'check_out', 'status')),
    'booking-guests': CrudModelSpec('booking-guests', models.BookingGuest, 'Гости в бронированиях', ('id', 'booking', 'full_name', 'role', 'created_at')),
    'booking-items': CrudModelSpec('booking-items', models.BookingItem, 'Позиции бронирований', ('id', 'booking', 'item_type', 'quantity', 'amount', 'created_at')),
    'payments': CrudModelSpec('payments', models.Payment, 'Платежи', ('id', 'booking', 'amount', 'method', 'status', 'created_at')),
    'payment-events': CrudModelSpec('payment-events', models.PaymentEvent, 'События платежей', ('id', 'payment', 'status', 'created_at', 'source')),
    'tickets': CrudModelSpec('tickets', models.Ticket, 'Обращения', ('id', 'client', 'booking', 'subject', 'priority', 'status')),
    'messages': CrudModelSpec('messages', models.Message, 'Сообщения', ('id', 'ticket', 'channel', 'direction', 'created_at')),
    'message-templates': CrudModelSpec('message-templates', models.MessageTemplate, 'Шаблоны сообщений', ('id', 'code', 'channel', 'active', 'updated_at')),
    'campaigns': CrudModelSpec('campaigns', models.Campaign, 'Кампании', ('id', 'name', 'status', 'started_at', 'finished_at')),
    'departments': CrudModelSpec('departments', models.Department, 'Подразделения', ('id', 'name', 'updated_at')),
    'employees': CrudModelSpec('employees', models.Employee, 'Сотрудники', ('id', 'user_id', 'department', 'full_name', 'position', 'status')),
    'tasks': CrudModelSpec('tasks', models.Task, 'Задачи', ('id', 'type', 'status', 'department', 'assignee', 'due')),
    'roles': CrudModelSpec('roles', models.Role, 'Роли', ('id', 'code', 'updated_at')),
    'permissions': CrudModelSpec('permissions', models.Permission, 'Разрешения', ('id', 'code', 'updated_at')),
    'employee-roles': CrudModelSpec('employee-roles', models.EmployeeRole, 'Назначения ролей', ('id', 'employee', 'role', 'assigned_at', 'expires_at')),
    'role-permissions': CrudModelSpec('role-permissions', models.RolePermission, 'Роли — разрешения', ('id', 'role', 'permission', 'granted_at')),
    'audit-log': CrudModelSpec('audit-log', models.AuditLog, 'Журнал аудита', ('id', 'entity', 'entity_id', 'action', 'risk', 'created_at')),
    'lookup-values': CrudModelSpec('lookup-values', models.LookupValue, 'Справочники (значения)', ('id', 'domain', 'code', 'label', 'order', 'active')),
    # Таблицы статусов/типов (FK-справочники)
    'booking-statuses': CrudModelSpec('booking-statuses', models.BookingStatus, 'Статусы бронирования', ('code', 'label', 'order')),
    'booking-sources': CrudModelSpec('booking-sources', models.BookingSource, 'Источники бронирования', ('code', 'label', 'order')),
    'ticket-statuses': CrudModelSpec('ticket-statuses', models.TicketStatus, 'Статусы обращений', ('code', 'label', 'order')),
    'ticket-priorities': CrudModelSpec('ticket-priorities', models.TicketPriority, 'Приоритеты обращений', ('code', 'label', 'order')),
    'task-statuses': CrudModelSpec('task-statuses', models.TaskStatus, 'Статусы задач', ('code', 'label', 'order')),
    'task-types': CrudModelSpec('task-types', models.TaskType, 'Типы задач', ('code', 'label', 'order')),
    'room-states': CrudModelSpec('room-states', models.RoomState, 'Состояния номеров', ('code', 'label', 'order')),
    'payment-methods': CrudModelSpec('payment-methods', models.PaymentMethod, 'Методы оплаты', ('code', 'label', 'order')),
    'payment-statuses': CrudModelSpec('payment-statuses', models.PaymentStatus, 'Статусы платежей', ('code', 'label', 'order')),
    'payment-event-statuses': CrudModelSpec('payment-event-statuses', models.PaymentEventStatus, 'Статусы событий платежей', ('code', 'label', 'order')),
    'client-segments': CrudModelSpec('client-segments', models.ClientSegment, 'Сегменты клиентов', ('code', 'label', 'order')),
    'loyalty-levels': CrudModelSpec('loyalty-levels', models.LoyaltyLevel, 'Уровни лояльности', ('code', 'label', 'order')),
    'contact-channel-types': CrudModelSpec('contact-channel-types', models.ContactChannelType, 'Типы каналов', ('code', 'label', 'order')),
    'consent-types': CrudModelSpec('consent-types', models.ConsentType, 'Типы согласий', ('code', 'label', 'order')),
    'consent-statuses': CrudModelSpec('consent-statuses', models.ConsentStatus, 'Статусы согласий', ('code', 'label', 'order')),
    'meal-plans': CrudModelSpec('meal-plans', models.MealPlan, 'Типы питания', ('code', 'label', 'order')),
    'booking-guest-roles': CrudModelSpec('booking-guest-roles', models.BookingGuestRole, 'Роли гостей', ('code', 'label', 'order')),
    'message-channels': CrudModelSpec('message-channels', models.MessageChannel, 'Каналы сообщений', ('code', 'label', 'order')),
    'message-directions': CrudModelSpec('message-directions', models.MessageDirection, 'Направления сообщений', ('code', 'label', 'order')),
    'campaign-statuses': CrudModelSpec('campaign-statuses', models.CampaignStatus, 'Статусы кампаний', ('code', 'label', 'order')),
    'employee-statuses': CrudModelSpec('employee-statuses', models.EmployeeStatus, 'Статусы сотрудников', ('code', 'label', 'order')),
}


def _get_spec_or_404(slug: str) -> CrudModelSpec:
    try:
        return CRUD_MODELS[slug]
    except KeyError as exc:
        raise Http404('Unknown model') from exc


def _lookup_choices(domain: str) -> list[tuple[str, str]]:
    """Загружает варианты из таблицы LookupValue по домену."""
    qs = models.LookupValue.objects.filter(domain=domain, active=True).order_by('order', 'label')
    return [('', '---------')] + [(lv.code, lv.label) for lv in qs]


def _build_modelform(model: Type[dj_models.Model]) -> Type[forms.ModelForm]:
    domain_map = LOOKUP_FIELD_DOMAINS.get(model.__name__, {})

    def formfield_callback(db_field: dj_models.Field, **kwargs):
        if isinstance(db_field, dj_models.JSONField):
            kwargs.setdefault('required', not db_field.blank and db_field.null is False)
            kwargs.setdefault('widget', forms.Textarea(attrs={'rows': 6}))
            return forms.JSONField(**kwargs)
        if db_field.name in domain_map:
            domain = domain_map[db_field.name]
            return forms.ChoiceField(
                choices=_lookup_choices(domain),
                required=not db_field.blank,
                label=db_field.verbose_name,
            )
        return db_field.formfield(**kwargs)

    return modelform_factory(model, fields='__all__', formfield_callback=formfield_callback)


def crud_index(request: HttpRequest):
    items = sorted(CRUD_MODELS.values(), key=lambda s: s.title)
    return render(request, 'ui/crud/index.html', {'items': items})


def crud_list(request: HttpRequest, slug: str):
    spec = _get_spec_or_404(slug)
    qs = spec.model.objects.all().order_by('pk')[:500]
    return render(
        request,
        'ui/crud/list.html',
        {
            'spec': spec,
            'rows': qs,
            'fields': spec.list_fields,
        },
    )


def crud_create(request: HttpRequest, slug: str):
    spec = _get_spec_or_404(slug)
    Form = _build_modelform(spec.model)
    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ui:crud_list', slug=slug)
    else:
        form = Form()
    return render(request, 'ui/crud/form.html', {'spec': spec, 'form': form, 'mode': 'create'})


def crud_update(request: HttpRequest, slug: str, pk: str):
    spec = _get_spec_or_404(slug)
    obj = get_object_or_404(spec.model, pk=pk)
    Form = _build_modelform(spec.model)
    if request.method == 'POST':
        form = Form(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('ui:crud_list', slug=slug)
    else:
        form = Form(instance=obj)
    return render(request, 'ui/crud/form.html', {'spec': spec, 'form': form, 'mode': 'update', 'object': obj})


def crud_delete(request: HttpRequest, slug: str, pk: str):
    spec = _get_spec_or_404(slug)
    obj = get_object_or_404(spec.model, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('ui:crud_list', slug=slug)
    return render(request, 'ui/crud/confirm_delete.html', {'spec': spec, 'object': obj})
