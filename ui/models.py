from __future__ import annotations

from django.db import models


class LookupValue(models.Model):
    """Универсальный справочник. Хранит варианты выбора для всех полей системы."""
    domain = models.CharField('домен', max_length=80, db_index=True)
    code = models.CharField('код', max_length=80)
    label = models.CharField('отображаемое название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    active = models.BooleanField('активен', default=True)

    class Meta:
        verbose_name = 'Значение справочника'
        verbose_name_plural = 'Значения справочников'
        unique_together = [('domain', 'code')]
        ordering = ['domain', 'order', 'label']

    def __str__(self) -> str:
        return f'[{self.domain}] {self.label}'


# ── Справочные таблицы статусов и типов ──────────────────────────────────────

class BookingStatus(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Статус бронирования'
        verbose_name_plural = 'Статусы бронирования'
        ordering = ['order']
    def __str__(self): return self.label

class BookingSource(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Источник бронирования'
        verbose_name_plural = 'Источники бронирования'
        ordering = ['order']
    def __str__(self): return self.label

class TicketStatus(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Статус обращения'
        verbose_name_plural = 'Статусы обращений'
        ordering = ['order']
    def __str__(self): return self.label

class TicketPriority(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Приоритет обращения'
        verbose_name_plural = 'Приоритеты обращений'
        ordering = ['order']
    def __str__(self): return self.label

class TaskStatus(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Статус задачи'
        verbose_name_plural = 'Статусы задач'
        ordering = ['order']
    def __str__(self): return self.label

class TaskType(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Тип задачи'
        verbose_name_plural = 'Типы задач'
        ordering = ['order']
    def __str__(self): return self.label

class RoomState(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Состояние номера'
        verbose_name_plural = 'Состояния номеров'
        ordering = ['order']
    def __str__(self): return self.label

class PaymentMethod(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Метод оплаты'
        verbose_name_plural = 'Методы оплаты'
        ordering = ['order']
    def __str__(self): return self.label

class PaymentStatus(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Статус платежа'
        verbose_name_plural = 'Статусы платежей'
        ordering = ['order']
    def __str__(self): return self.label

class PaymentEventStatus(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Статус события платежа'
        verbose_name_plural = 'Статусы событий платежей'
        ordering = ['order']
    def __str__(self): return self.label

class ClientSegment(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Сегмент клиента'
        verbose_name_plural = 'Сегменты клиентов'
        ordering = ['order']
    def __str__(self): return self.label

class LoyaltyLevel(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Уровень лояльности'
        verbose_name_plural = 'Уровни лояльности'
        ordering = ['order']
    def __str__(self): return self.label

class ContactChannelType(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Тип контактного канала'
        verbose_name_plural = 'Типы контактных каналов'
        ordering = ['order']
    def __str__(self): return self.label

class ConsentType(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Тип согласия'
        verbose_name_plural = 'Типы согласий'
        ordering = ['order']
    def __str__(self): return self.label

class ConsentStatus(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Статус согласия'
        verbose_name_plural = 'Статусы согласий'
        ordering = ['order']
    def __str__(self): return self.label

class MealPlan(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Тип питания'
        verbose_name_plural = 'Типы питания'
        ordering = ['order']
    def __str__(self): return self.label

class BookingGuestRole(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Роль гостя в бронировании'
        verbose_name_plural = 'Роли гостей в бронировании'
        ordering = ['order']
    def __str__(self): return self.label

class MessageChannel(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Канал сообщения'
        verbose_name_plural = 'Каналы сообщений'
        ordering = ['order']
    def __str__(self): return self.label

class MessageDirection(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Направление сообщения'
        verbose_name_plural = 'Направления сообщений'
        ordering = ['order']
    def __str__(self): return self.label

class CampaignStatus(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Статус кампании'
        verbose_name_plural = 'Статусы кампаний'
        ordering = ['order']
    def __str__(self): return self.label

class EmployeeStatus(models.Model):
    code = models.CharField('код', max_length=80, primary_key=True)
    label = models.CharField('название', max_length=200)
    order = models.PositiveIntegerField('порядок', default=0)
    class Meta:
        verbose_name = 'Статус сотрудника'
        verbose_name_plural = 'Статусы сотрудников'
        ordering = ['order']
    def __str__(self): return self.label


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Client(TimestampedModel):
    last_name = models.CharField('фамилия', max_length=150)
    first_name = models.CharField('имя', max_length=150)
    middle_name = models.CharField('отчество', max_length=150, blank=True, default='')
    birth_date = models.DateField('дата_рождения', blank=True, null=True)
    segment = models.ForeignKey('ClientSegment', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='сегмент', db_column='segment', to_field='code')
    preferences = models.JSONField('предпочтения_json', blank=True, null=True)
    notes = models.TextField('примечания', blank=True, default='')
    loyalty_level = models.ForeignKey('LoyaltyLevel', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='уровень лояльности', db_column='loyalty_level', to_field='code')
    loyalty_points = models.IntegerField('баллы лояльности', default=0)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self) -> str:
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)


class ContactChannel(TimestampedModel):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='contact_channels',
        verbose_name='клиент',
    )
    type = models.ForeignKey('ContactChannelType', on_delete=models.PROTECT, verbose_name='тип', db_column='type', to_field='code')
    value = models.CharField('значение', max_length=255)
    is_primary = models.BooleanField('is_primary', default=False)
    verified_at = models.DateTimeField('verified_at', blank=True, null=True)
    priority = models.PositiveIntegerField('priority', default=0)

    class Meta:
        verbose_name = 'Контактный канал'
        verbose_name_plural = 'Контактные каналы'
        constraints = [
            models.UniqueConstraint(fields=['type_id', 'value'], name='uq_contactchannel_type_value'),
        ]

    def __str__(self) -> str:
        return f'{self.type}: {self.value}'


class Consent(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='consents', verbose_name='клиент')
    type = models.ForeignKey('ConsentType', on_delete=models.PROTECT, verbose_name='тип', db_column='type', to_field='code')
    status = models.ForeignKey('ConsentStatus', on_delete=models.PROTECT, verbose_name='статус', db_column='status', to_field='code')
    source = models.CharField('источник', max_length=80)
    obtained_at = models.DateTimeField('obtained_at')
    revoked_at = models.DateTimeField('revoked_at', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Согласие'
        verbose_name_plural = 'Согласия'

    def __str__(self) -> str:
        return f'{self.type} — {self.status}'



class RoomCategory(TimestampedModel):
    name = models.CharField('название', max_length=120, unique=True)
    capacity = models.PositiveIntegerField('вместимость')
    description = models.TextField('описание', blank=True, default='')
    options = models.JSONField('опции_json', blank=True, null=True)

    class Meta:
        verbose_name = 'Категория номера'
        verbose_name_plural = 'Категории номеров'

    def __str__(self) -> str:
        return self.name


class Room(TimestampedModel):
    category = models.ForeignKey(RoomCategory, on_delete=models.PROTECT, related_name='rooms', verbose_name='категория')
    room_number = models.CharField('номер_комнаты', max_length=20, unique=True)
    state = models.ForeignKey('RoomState', on_delete=models.PROTECT, verbose_name='состояние', db_column='state', to_field='code')

    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'

    def __str__(self) -> str:
        return self.room_number


class Rate(TimestampedModel):
    name = models.CharField('название', max_length=120)
    meal_plan = models.ForeignKey('MealPlan', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='питание', db_column='meal_plan', to_field='code')
    rules = models.JSONField('правила_json', default=dict)
    active = models.BooleanField('активен', default=True)

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'

    def __str__(self) -> str:
        return self.name


class CancellationRule(TimestampedModel):
    rate = models.ForeignKey(Rate, on_delete=models.CASCADE, related_name='cancellation_rules', verbose_name='тариф')
    deadline_hours = models.PositiveIntegerField('дедлайн_часы')
    penalty_rule = models.JSONField('штраф_правило_json', default=dict)

    class Meta:
        verbose_name = 'Правило отмены'
        verbose_name_plural = 'Правила отмены'

    def __str__(self) -> str:
        return f'{self.rate} — {self.deadline_hours}ч'


class Service(TimestampedModel):
    name = models.CharField('название', max_length=160)
    price = models.DecimalField('цена', max_digits=12, decimal_places=2)
    description = models.TextField('описание', blank=True, default='')
    active = models.BooleanField('активна', default=True)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self) -> str:
        return self.name


class Offer(TimestampedModel):
    category = models.ForeignKey(RoomCategory, on_delete=models.PROTECT, related_name='offers', verbose_name='категория')
    rate = models.ForeignKey(Rate, on_delete=models.PROTECT, related_name='offers', verbose_name='тариф')
    name = models.CharField('название', max_length=160)
    conditions = models.JSONField('условия_json', default=dict)
    start_date = models.DateField('дата_начала', blank=True, null=True)
    end_date = models.DateField('дата_окончания', blank=True, null=True)

    class Meta:
        verbose_name = 'Предложение'
        verbose_name_plural = 'Предложения'

    def __str__(self) -> str:
        return self.name


class OfferService(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='offer_services', verbose_name='предложение')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='offer_services', verbose_name='услуга')
    quantity = models.PositiveIntegerField('количество', default=1)
    conditions = models.JSONField('условия_json', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Состав предложения'
        verbose_name_plural = 'Состав предложений'

    def __str__(self) -> str:
        return f'{self.offer} — {self.service} x{self.quantity}'


class Booking(TimestampedModel):
    # status codes for reference
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_IN_HOUSE = 'in_house'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='bookings', verbose_name='клиент')
    category = models.ForeignKey(RoomCategory, on_delete=models.PROTECT, related_name='bookings', verbose_name='категория')
    rate = models.ForeignKey(Rate, on_delete=models.PROTECT, related_name='bookings', verbose_name='тариф')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, related_name='bookings', verbose_name='номер', blank=True, null=True)
    check_in = models.DateField('дата_заезда')
    check_out = models.DateField('дата_выезда')
    status = models.ForeignKey('BookingStatus', on_delete=models.PROTECT, verbose_name='статус', db_column='status', to_field='code')
    source = models.ForeignKey('BookingSource', on_delete=models.PROTECT, verbose_name='источник', db_column='source', to_field='code')
    total_cost = models.DecimalField('итоговая_стоимость', max_digits=12, decimal_places=2)
    cancel_reason = models.TextField('причина отмены', blank=True, default='')
    cancel_penalty = models.DecimalField('штраф за отмену', max_digits=12, decimal_places=2, default=0)
    cancelled_at = models.DateTimeField('дата отмены', blank=True, null=True)
    cancel_source = models.CharField('источник отмены', max_length=80, blank=True, default='')
    cancel_initiator = models.CharField('инициатор отмены', max_length=80, blank=True, default='')

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'

    def __str__(self) -> str:
        return f'#{self.id} — {self.client}'


class BookingGuest(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='guests', verbose_name='бронирование')
    full_name = models.CharField('фио', max_length=200)
    role = models.ForeignKey('BookingGuestRole', on_delete=models.PROTECT, verbose_name='роль', db_column='role', to_field='code')
    document = models.CharField('документ', max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Гость в бронировании'
        verbose_name_plural = 'Гости в бронированиях'

    def __str__(self) -> str:
        return f'{self.full_name} ({self.role})'


class BookingItem(models.Model):
    ITEM_TYPE_SERVICE = 'service'
    ITEM_TYPE_OFFER = 'offer'
    ITEM_TYPE_FEE = 'fee'
    ITEM_TYPE_CHOICES = (
        (ITEM_TYPE_SERVICE, 'service'),
        (ITEM_TYPE_OFFER, 'offer'),
        (ITEM_TYPE_FEE, 'fee'),
    )

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items', verbose_name='бронирование')
    item_type = models.CharField('тип_позиции', max_length=20, choices=ITEM_TYPE_CHOICES)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='booking_items', blank=True, null=True)
    offer = models.ForeignKey(Offer, on_delete=models.PROTECT, related_name='booking_items', blank=True, null=True)
    quantity = models.PositiveIntegerField('количество', default=1)
    amount = models.DecimalField('сумма', max_digits=12, decimal_places=2)
    comment = models.TextField('комментарий', blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Позиция бронирования'
        verbose_name_plural = 'Позиции бронирований'
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(item_type='service', service__isnull=False, offer__isnull=True)
                    | models.Q(item_type='offer', service__isnull=True, offer__isnull=False)
                    | models.Q(item_type='fee', service__isnull=True, offer__isnull=True)
                ),
                name='ck_bookingitem_type_refs',
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.item_type == self.ITEM_TYPE_SERVICE:
            if not self.service_id:
                raise ValidationError({'service': 'Для типа «service» поле «Услуга» обязательно.'})
            if self.offer_id:
                raise ValidationError({'offer': 'Для типа «service» поле «Предложение» должно быть пустым.'})
        elif self.item_type == self.ITEM_TYPE_OFFER:
            if not self.offer_id:
                raise ValidationError({'offer': 'Для типа «offer» поле «Предложение» обязательно.'})
            if self.service_id:
                raise ValidationError({'service': 'Для типа «offer» поле «Услуга» должно быть пустым.'})
        elif self.item_type == self.ITEM_TYPE_FEE:
            if self.service_id:
                raise ValidationError({'service': 'Для типа «fee» поле «Услуга» должно быть пустым.'})
            if self.offer_id:
                raise ValidationError({'offer': 'Для типа «fee» поле «Предложение» должно быть пустым.'})

    def __str__(self) -> str:
        return f'{self.booking} — {self.item_type} ({self.amount})'



class Payment(TimestampedModel):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments', verbose_name='бронирование')
    amount = models.DecimalField('сумма', max_digits=12, decimal_places=2)
    method = models.ForeignKey('PaymentMethod', on_delete=models.PROTECT, verbose_name='метод', db_column='method', to_field='code')
    status = models.ForeignKey('PaymentStatus', on_delete=models.PROTECT, verbose_name='статус', db_column='status', to_field='code')
    provider_ref = models.CharField('provider_ref', max_length=120, blank=True, default='')

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'

    def __str__(self) -> str:
        return f'{self.booking} — {self.amount} ({self.status})'


class PaymentEvent(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='events', verbose_name='платёж')
    status = models.ForeignKey('PaymentEventStatus', on_delete=models.PROTECT, verbose_name='статус', db_column='status', to_field='code')
    payload = models.JSONField('payload_json', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField('источник', max_length=80, blank=True, default='')

    class Meta:
        verbose_name = 'Событие платежа'
        verbose_name_plural = 'События платежей'

    def __str__(self) -> str:
        return f'{self.payment} — {self.status}'


class Ticket(TimestampedModel):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='tickets', verbose_name='клиент')
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, related_name='tickets', verbose_name='бронирование', blank=True, null=True)
    subject = models.CharField('тема', max_length=200)
    priority = models.ForeignKey('TicketPriority', on_delete=models.PROTECT, verbose_name='приоритет', db_column='priority', to_field='code')
    status = models.ForeignKey('TicketStatus', on_delete=models.PROTECT, verbose_name='статус', db_column='status', to_field='code')
    sla_due_at = models.DateTimeField('sla_due_at', blank=True, null=True)

    class Meta:
        verbose_name = 'Обращение'
        verbose_name_plural = 'Обращения'

    def __str__(self) -> str:
        return self.subject


class Message(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages', verbose_name='обращение')
    contact_channel = models.ForeignKey(
        ContactChannel,
        on_delete=models.SET_NULL,
        related_name='messages',
        verbose_name='контактный_канал',
        blank=True,
        null=True,
    )
    template = models.ForeignKey(
        'MessageTemplate',
        on_delete=models.SET_NULL,
        related_name='messages',
        verbose_name='шаблон',
        blank=True,
        null=True,
    )
    campaign = models.ForeignKey(
        'Campaign',
        on_delete=models.SET_NULL,
        related_name='messages',
        verbose_name='кампания',
        blank=True,
        null=True,
    )
    channel = models.ForeignKey('MessageChannel', on_delete=models.PROTECT, verbose_name='канал', db_column='channel', to_field='code')
    direction = models.ForeignKey('MessageDirection', on_delete=models.PROTECT, verbose_name='направление', db_column='direction', to_field='code')
    text = models.TextField('текст')
    attachments = models.JSONField('вложения_json', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self) -> str:
        return f'{self.channel} — {self.direction}'


class MessageTemplate(models.Model):
    code = models.CharField('код', max_length=80, unique=True)
    channel = models.ForeignKey('MessageChannel', on_delete=models.PROTECT, verbose_name='канал', db_column='channel', to_field='code')
    subject = models.CharField('тема', max_length=200, blank=True, default='')
    body = models.TextField('тело')
    active = models.BooleanField('активен', default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Шаблон сообщения'
        verbose_name_plural = 'Шаблоны сообщений'

    def __str__(self) -> str:
        return self.code


class Campaign(TimestampedModel):
    name = models.CharField('название', max_length=160)
    segment = models.JSONField('сегмент_json', default=dict)
    started_at = models.DateTimeField('started_at', blank=True, null=True)
    finished_at = models.DateTimeField('finished_at', blank=True, null=True)
    metrics = models.JSONField('метрики_json', blank=True, null=True)
    status = models.ForeignKey('CampaignStatus', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='статус', db_column='status', to_field='code')
    message_templates = models.ManyToManyField(
        'MessageTemplate',
        related_name='campaigns',
        verbose_name='шаблоны сообщений',
        blank=True,
    )

    class Meta:
        verbose_name = 'Кампания'
        verbose_name_plural = 'Кампании'

    def __str__(self) -> str:
        return self.name


class Department(TimestampedModel):
    name = models.CharField('название', max_length=120, unique=True)

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'

    def __str__(self) -> str:
        return self.name


class Employee(TimestampedModel):
    user_id = models.PositiveBigIntegerField('user_id', unique=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees', verbose_name='подразделение')
    full_name = models.CharField('фио', max_length=200, blank=True, default='')
    position = models.CharField('должность', max_length=120, blank=True, default='')
    status = models.ForeignKey('EmployeeStatus', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='статус', db_column='status', to_field='code')

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self) -> str:
        return self.full_name or f'Employee #{self.id}'


class Task(TimestampedModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, related_name='tasks', verbose_name='обращение', blank=True, null=True)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, related_name='tasks', verbose_name='бронирование', blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='tasks', verbose_name='подразделение')
    assignee = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='tasks', verbose_name='исполнитель', blank=True, null=True)
    type = models.ForeignKey('TaskType', on_delete=models.PROTECT, verbose_name='тип', db_column='type', to_field='code')
    status = models.ForeignKey('TaskStatus', on_delete=models.PROTECT, verbose_name='статус', db_column='status', to_field='code')
    description = models.TextField('описание', blank=True, default='')
    due = models.DateTimeField('срок', blank=True, null=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self) -> str:
        return f'{self.type} — {self.status}'



class Role(TimestampedModel):
    code = models.CharField('код', max_length=80, unique=True)
    description = models.TextField('описание', blank=True, default='')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self) -> str:
        return self.code


class Permission(TimestampedModel):
    code = models.CharField('код', max_length=120, unique=True)
    description = models.TextField('описание', blank=True, default='')

    class Meta:
        verbose_name = 'Разрешение'
        verbose_name_plural = 'Разрешения'

    def __str__(self) -> str:
        return self.code


class EmployeeRole(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='role_assignments', verbose_name='сотрудник')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='employee_assignments', verbose_name='роль')
    assigned_at = models.DateTimeField('назначено_в')
    expires_at = models.DateTimeField('expires_at', blank=True, null=True)
    source = models.CharField('источник', max_length=80, blank=True, default='')
    initiator = models.CharField('инициатор', max_length=80, blank=True, default='')

    class Meta:
        verbose_name = 'Назначение роли'
        verbose_name_plural = 'Назначения ролей'

    def __str__(self) -> str:
        return f'{self.employee} — {self.role}'


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions', verbose_name='роль')
    permission = models.ForeignKey(Permission, on_delete=models.PROTECT, related_name='role_bindings', verbose_name='разрешение')
    granted_at = models.DateTimeField('granted_at', blank=True, null=True)
    source = models.CharField('источник', max_length=80, blank=True, default='')

    class Meta:
        verbose_name = 'Роль — разрешение'
        verbose_name_plural = 'Роли — разрешения'

    def __str__(self) -> str:
        return f'{self.role} — {self.permission}'


class AuditLog(models.Model):
    actor_employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
        verbose_name='actor_employee_id',
        blank=True,
        null=True,
    )
    entity = models.CharField('сущность', max_length=80)
    entity_id = models.PositiveBigIntegerField('entity_id')
    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'
    ACTION_CHOICES = [
        (ACTION_CREATE, 'Создание'),
        (ACTION_UPDATE, 'Изменение'),
        (ACTION_DELETE, 'Удаление'),
    ]
    RISK_LOW = 'low'
    RISK_MEDIUM = 'medium'
    RISK_HIGH = 'high'
    RISK_CHOICES = [
        (RISK_LOW, 'Низкий'),
        (RISK_MEDIUM, 'Средний'),
        (RISK_HIGH, 'Высокий'),
    ]
    action = models.CharField('действие', max_length=40, choices=ACTION_CHOICES)
    details = models.JSONField('детали_json', blank=True, null=True)
    risk = models.CharField('риск', max_length=40, blank=True, default='', choices=RISK_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Журнал аудита'
        verbose_name_plural = 'Журналы аудита'

    def __str__(self) -> str:
        return f'{self.entity}#{self.entity_id} — {self.action}'


class OperationalRadarReport(models.Model):
    snapshot_hash   = models.CharField('хэш снапшота', max_length=64, db_index=True)
    snapshot        = models.JSONField('снапшот')
    recommendations = models.JSONField('рекомендации')   # {items: [...], summary: ""}
    ollama_model    = models.CharField('модель', max_length=80, default='llama3.1:8b')
    generated_at    = models.DateTimeField('сгенерировано', auto_now_add=True)
    is_valid        = models.BooleanField('валидный', default=True)
    error           = models.TextField('ошибка', blank=True, default='')

    class Meta:
        verbose_name = 'Отчёт радара'
        verbose_name_plural = 'Отчёты радара'
        ordering = ['-generated_at']

    def __str__(self) -> str:
        status = 'OK' if self.is_valid else 'ERR'
        return f'Radar {self.generated_at:%Y-%m-%d %H:%M} [{status}]'


class AgentSession(TimestampedModel):
    title = models.CharField('заголовок', max_length=200, blank=True, default='')

    class Meta:
        verbose_name = 'Сессия ИИ'
        verbose_name_plural = 'Сессии ИИ'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.title or f'Сессия #{self.pk}'


class AgentMessage(models.Model):
    ROLE_USER      = 'user'
    ROLE_ASSISTANT = 'assistant'

    session    = models.ForeignKey(AgentSession, on_delete=models.CASCADE, related_name='messages')
    role       = models.CharField('роль', max_length=20)
    content    = models.TextField('текст')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщение ИИ'
        verbose_name_plural = 'Сообщения ИИ'
        ordering = ['created_at']

    def __str__(self) -> str:
        return f'{self.role}: {self.content[:60]}'
