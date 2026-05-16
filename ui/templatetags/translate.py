from __future__ import annotations

from django import template

register = template.Library()

_BOOKING_STATUS = {
    'pending': 'Ожидает',
    'confirmed': 'Подтверждено',
    'in_house': 'Заезд',
    'checkin': 'Заезд',
    'checkout': 'Выезд',
    'completed': 'Завершено',
    'cancelled': 'Отменено',
}

_TICKET_STATUS = {
    'open': 'Открыто',
    'in_progress': 'В работе',
    'pending': 'Ожидание',
    'resolved': 'Решено',
    'closed': 'Закрыто',
}

_TASK_STATUS = {
    'open': 'Новая',
    'in_progress': 'В работе',
    'done': 'Сделано',
    'failed': 'Отменено',
}

_PRIORITY = {
    'low': 'Низкий',
    'medium': 'Средний',
    'high': 'Высокий',
    'critical': 'Критический',
}

_SOURCE = {
    'website': 'Сайт',
    'corporate': 'Корп. договор',
    'ota': 'Онлайн-агентство',
    'loyalty': 'Программа лояльности',
    'phone': 'Телефон',
    'walk_in': 'Прямой обход',
}

_SEGMENT = {
    'VIP': 'ВИП',
    'Business': 'Бизнес',
    'Family': 'Семья',
    'Leisure': 'Отдых',
    'Loyalty': 'Лояльность',
    'New': 'Новый',
}

_CHANNEL = {
    'email': 'Эл. почта',
    'phone': 'Телефон',
    'whatsapp': 'WhatsApp',
    'telegram': 'Telegram',
    'portal': 'Портал',
    'sms': 'СМС',
}


@register.filter
def booking_status(value: str) -> str:
    return _BOOKING_STATUS.get(value, value)


@register.filter
def ticket_status(value: str) -> str:
    return _TICKET_STATUS.get(value, value)


@register.filter
def task_status(value: str) -> str:
    return _TASK_STATUS.get(value, value)


@register.filter
def priority(value: str) -> str:
    return _PRIORITY.get(value, value)


@register.filter
def source(value: str) -> str:
    return _SOURCE.get(value, value)


@register.filter
def segment(value: str) -> str:
    return _SEGMENT.get(value, value)


@register.filter
def channel(value: str) -> str:
    return _CHANNEL.get(value, value)
