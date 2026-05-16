
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from ui import models


class Command(BaseCommand):
    help = "Populate database with realistic operational data"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing rows before seeding")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self._reset()

        now = timezone.now()
        today = timezone.localdate()

        standard, superior, deluxe, family = self._room_categories()
        rooms = self._rooms(standard, superior, deluxe, family)
        flexible, nonref, corporate = self._rates()
        rules = self._cancellation_rules(flexible, nonref, corporate)
        transfer, late_checkout, breakfast, parking, spa = self._services()
        sea_weekend, family_comfort, business_express = self._offers(deluxe, family, superior, flexible, corporate)
        self._offer_services(sea_weekend, family_comfort, business_express, breakfast, parking, spa)

        front_office, concierge, finance, housekeeping, it_ops = self._departments()
        emp_fo, emp_conc, emp_fin, emp_hk, emp_it = self._employees(front_office, concierge, finance, housekeeping, it_ops)

        roles, perms = self._rbac()
        self._role_permissions(roles, perms)
        self._employee_roles(emp_fo, emp_conc, emp_fin, emp_hk, emp_it, roles)

        clients = self._clients(today)
        client_by_last = {c.last_name: c for c in clients}

        room_by_number = {r.room_number: r for r in rooms}
        bookings = self._bookings(
            today,
            client_by_last["Смирнова"],
            client_by_last["Петров"],
            client_by_last["Ким"],
            client_by_last["Васильев"],
            client_by_last["Орлова"],
            client_by_last["Новикова"],
            standard,
            superior,
            deluxe,
            family,
            flexible,
            nonref,
            corporate,
            room_by_number,
        )
        booking_by_client_id = {b.client_id: b for b in bookings}

        self._booking_guests(booking_by_client_id[client_by_last["Ким"].id])
        self._booking_items(
            booking_by_client_id[client_by_last["Смирнова"].id],
            booking_by_client_id[client_by_last["Петров"].id],
            booking_by_client_id[client_by_last["Ким"].id],
            booking_by_client_id[client_by_last["Орлова"].id],
            sea_weekend,
            family_comfort,
            business_express,
            transfer,
            late_checkout,
            breakfast,
            parking,
            spa,
        )
        self._booking_cancellation(booking_by_client_id[client_by_last["Васильев"].id], rules)

        payments = self._payments(bookings)
        self._payment_events(payments)

        tickets = self._tickets(now, booking_by_client_id, client_by_last)
        messages = self._messages(tickets)

        templates = self._templates()
        campaigns = self._campaigns(now)
        self._campaign_templates(campaigns, templates)
        self._wire_messages(messages, templates, campaigns)

        tasks = self._tasks(now, tickets, front_office, finance, housekeeping, emp_fo, emp_fin, emp_hk)
        self._audit(emp_it, bookings, tasks)

        self.stdout.write(self.style.SUCCESS("Seed completed"))

    def _reset(self) -> None:
        models_in_delete_order = [
            models.AuditLog,
            models.RolePermission,
            models.EmployeeRole,
            models.Permission,
            models.Role,
            models.Task,
            models.Campaign,
            models.Message,
            models.MessageTemplate,
            models.Ticket,
            models.PaymentEvent,
            models.Payment,
            models.BookingItem,
            models.BookingGuest,
            models.Booking,
            models.OfferService,
            models.Offer,
            models.Service,
            models.CancellationRule,
            models.Rate,
            models.Room,
            models.RoomCategory,
            models.Consent,
            models.ContactChannel,
            models.Client,
            models.Employee,
            models.Department,
        ]
        for model_cls in models_in_delete_order:
            model_cls.objects.all().delete()

    def _room_categories(self):
        def cat(name, capacity, description, options):
            return models.RoomCategory.objects.get_or_create(
                name=name,
                defaults={"capacity": capacity, "description": description, "options": options},
            )[0]

        return (
            cat("Standard", 2, "Уютный номер для коротких поездок.", {"beds": "queen", "view": "city", "area_m2": 18}),
            cat("Superior", 2, "Расширенный номер с рабочей зоной.", {"beds": "king", "workdesk": True, "area_m2": 24}),
            cat("Deluxe Sea View", 3, "Номер с видом на море и балконом.", {"beds": "king+sofa", "view": "sea", "balcony": True}),
            cat("Family Suite", 4, "Двухкомнатный номер для семьи.", {"beds": "2 queen", "kitchenette": True, "area_m2": 44}),
        )

    def _rooms(self, standard, superior, deluxe, family):
        specs = [
            ("101", standard, "available"),
            ("102", standard, "cleaning"),
            ("203", superior, "occupied"),
            ("204", superior, "maintenance"),
            ("305", deluxe, "available"),
            ("306", deluxe, "reserved"),
            ("401", family, "available"),
            ("402", family, "available"),
        ]
        result = []
        for number, category, state in specs:
            obj, _ = models.Room.objects.get_or_create(
                room_number=number,
                defaults={"category": category, "state_id": state},
            )
            result.append(obj)
        return result

    def _rates(self):
        def rate(name, meal_plan, rules, active=True):
            return models.Rate.objects.get_or_create(
                name=name,
                defaults={"meal_plan_id": meal_plan, "rules": rules, "active": active},
            )[0]

        return (
            rate("Flexible", "BB", {"check_in": "14:00", "check_out": "12:00", "currency": "RUB"}),
            rate("Non-Refundable", "BB", {"prepayment": 100, "change_allowed": False, "currency": "RUB"}),
            rate("Corporate", "RO", {"invoice": True, "guarantee": "company", "currency": "RUB"}),
        )

    def _cancellation_rules(self, flexible, nonref, corporate):
        specs = [
            (flexible, 24, {"type": "percent_first_night", "value": 0}),
            (flexible, 12, {"type": "percent_first_night", "value": 50}),
            (flexible, 6, {"type": "percent_first_night", "value": 100}),
            (corporate, 24, {"type": "flat", "value": 0}),
            (nonref, 0, {"type": "percent_total", "value": 100}),
        ]
        result = []
        for rate, deadline, penalty in specs:
            result.append(
                models.CancellationRule.objects.get_or_create(
                    rate=rate,
                    deadline_hours=deadline,
                    defaults={"penalty_rule": penalty},
                )[0]
            )
        return result

    def _services(self):
        def svc(name, price, description, active=True):
            return models.Service.objects.get_or_create(
                name=name,
                defaults={"price": price, "description": description, "active": active},
            )[0]

        return (
            svc("Airport transfer", Decimal("2500.00"), "Встреча и трансфер до отеля."),
            svc("Late checkout", Decimal("1800.00"), "Выезд до 18:00 при наличии возможности."),
            svc("Breakfast", Decimal("900.00"), "Завтрак шведский стол."),
            svc("Parking", Decimal("600.00"), "Охраняемая парковка на сутки."),
            svc("Spa access", Decimal("1500.00"), "Посещение спа-зоны на 2 часа."),
        )

    def _offers(self, deluxe, family, superior, flexible, corporate):
        sea_weekend = models.Offer.objects.get_or_create(
            name="Sea Weekend",
            category=deluxe,
            rate=flexible,
            defaults={
                "conditions": {"min_nights": 2, "discount_percent": 10, "includes": ["Breakfast", "Spa access"]},
                "start_date": date.today() - timedelta(days=45),
                "end_date": date.today() + timedelta(days=60),
            },
        )[0]
        family_comfort = models.Offer.objects.get_or_create(
            name="Family Comfort",
            category=family,
            rate=flexible,
            defaults={
                "conditions": {"min_nights": 3, "kids_stay_free": True, "includes": ["Breakfast"]},
                "start_date": date.today() - timedelta(days=30),
                "end_date": date.today() + timedelta(days=90),
            },
        )[0]
        business_express = models.Offer.objects.get_or_create(
            name="Business Express",
            category=superior,
            rate=corporate,
            defaults={"conditions": {"min_nights": 1, "early_check_in": True, "includes": ["Parking"]}},
        )[0]
        return sea_weekend, family_comfort, business_express

    def _offer_services(self, sea_weekend, family_comfort, business_express, breakfast, parking, spa):
        models.OfferService.objects.get_or_create(
            offer=sea_weekend,
            service=breakfast,
            defaults={"quantity": 2, "conditions": {"included": True}},
        )
        models.OfferService.objects.get_or_create(
            offer=sea_weekend,
            service=spa,
            defaults={"quantity": 1, "conditions": {"included": True}},
        )
        models.OfferService.objects.get_or_create(
            offer=family_comfort,
            service=breakfast,
            defaults={"quantity": 3, "conditions": {"included": True}},
        )
        models.OfferService.objects.get_or_create(
            offer=business_express,
            service=parking,
            defaults={"quantity": 1, "conditions": {"included": True}},
        )

    def _departments(self):
        def dep(name):
            return models.Department.objects.get_or_create(name=name)[0]

        return dep("Front Office"), dep("Concierge"), dep("Finance"), dep("Housekeeping"), dep("IT Operations")

    def _employees(self, front_office, concierge, finance, housekeeping, it_ops):
        def emp(user_id, dept, full_name, position):
            return models.Employee.objects.get_or_create(
                user_id=user_id,
                defaults={"department": dept, "full_name": full_name, "position": position, "status_id": "active"},
            )[0]

        return (
            emp(1001, front_office, "Мария Иванова", "Старший администратор"),
            emp(1002, concierge, "Алексей Морозов", "Консьерж"),
            emp(1003, finance, "Наталья Белова", "Финансовый контролёр"),
            emp(1004, housekeeping, "Ольга Соколова", "Супервайзер"),
            emp(1005, it_ops, "Денис Кравцов", "Системный администратор"),
        )

    def _rbac(self):
        roles = [
            models.Role.objects.get_or_create(code="admin", defaults={"description": "Полный доступ."})[0],
            models.Role.objects.get_or_create(code="front_office", defaults={"description": "Бронирования и обращения."})[0],
            models.Role.objects.get_or_create(code="finance", defaults={"description": "Платежи и сверки."})[0],
            models.Role.objects.get_or_create(code="ops", defaults={"description": "Операционные задачи."})[0],
            models.Role.objects.get_or_create(code="ai_agent", defaults={"description": "Агентные сценарии."})[0],
        ]
        perms = [
            models.Permission.objects.get_or_create(code="clients.read", defaults={"description": "Просмотр клиентов."})[0],
            models.Permission.objects.get_or_create(code="clients.write", defaults={"description": "Редактирование клиентов."})[0],
            models.Permission.objects.get_or_create(code="bookings.read", defaults={"description": "Просмотр бронирований."})[0],
            models.Permission.objects.get_or_create(code="bookings.write", defaults={"description": "Редактирование бронирований."})[0],
            models.Permission.objects.get_or_create(code="bookings.cancel", defaults={"description": "Отмена бронирований."})[0],
            models.Permission.objects.get_or_create(code="payments.read", defaults={"description": "Просмотр платежей."})[0],
            models.Permission.objects.get_or_create(code="payments.write", defaults={"description": "Проведение платежей."})[0],
            models.Permission.objects.get_or_create(code="tickets.read", defaults={"description": "Просмотр обращений."})[0],
            models.Permission.objects.get_or_create(code="tickets.write", defaults={"description": "Работа с обращениями."})[0],
            models.Permission.objects.get_or_create(code="tasks.manage", defaults={"description": "Управление задачами."})[0],
            models.Permission.objects.get_or_create(code="catalog.manage", defaults={"description": "Справочники."})[0],
            models.Permission.objects.get_or_create(code="ai.run", defaults={"description": "Запуск агентных сессий."})[0],
            models.Permission.objects.get_or_create(code="audit.read", defaults={"description": "Просмотр аудита."})[0],
        ]
        return roles, perms

    def _role_permissions(self, roles, perms):
        role = {r.code: r for r in roles}
        perm = {p.code: p for p in perms}
        mapping = {
            "admin": list(perm.values()),
            "front_office": [
                perm["clients.read"],
                perm["clients.write"],
                perm["bookings.read"],
                perm["bookings.write"],
                perm["bookings.cancel"],
                perm["tickets.read"],
                perm["tickets.write"],
                perm["tasks.manage"],
                perm["audit.read"],
            ],
            "finance": [perm["payments.read"], perm["payments.write"], perm["bookings.read"], perm["audit.read"]],
            "ops": [perm["tasks.manage"], perm["bookings.read"], perm["catalog.manage"], perm["audit.read"]],
            "ai_agent": [perm["ai.run"], perm["tickets.read"], perm["bookings.read"], perm["audit.read"]],
        }
        for role_code, perm_list in mapping.items():
            for p in perm_list:
                models.RolePermission.objects.get_or_create(role=role[role_code], permission=p)

    def _employee_roles(self, emp_fo, emp_conc, emp_fin, emp_hk, emp_it, roles):
        role = {r.code: r for r in roles}
        now = timezone.now()
        models.EmployeeRole.objects.get_or_create(
            employee=emp_fo,
            role=role["front_office"],
            defaults={"assigned_at": now, "source": "HR", "initiator": "system"},
        )
        models.EmployeeRole.objects.get_or_create(
            employee=emp_conc,
            role=role["front_office"],
            defaults={"assigned_at": now, "source": "HR", "initiator": "system"},
        )
        models.EmployeeRole.objects.get_or_create(
            employee=emp_fin,
            role=role["finance"],
            defaults={"assigned_at": now, "source": "HR", "initiator": "system"},
        )
        models.EmployeeRole.objects.get_or_create(
            employee=emp_hk,
            role=role["ops"],
            defaults={"assigned_at": now, "source": "HR", "initiator": "system"},
        )
        models.EmployeeRole.objects.get_or_create(
            employee=emp_it,
            role=role["admin"],
            defaults={"assigned_at": now, "source": "HR", "initiator": "system"},
        )

    def _clients(self, today):
        def mk(last, first, middle, bday, segment, prefs, notes):
            return models.Client.objects.get_or_create(
                last_name=last,
                first_name=first,
                middle_name=middle,
                defaults={"birth_date": bday, "segment_id": segment, "preferences": prefs, "notes": notes},
            )[0]

        clients = [
            mk(
                "Смирнова",
                "Анна",
                "Игоревна",
                date(1988, 11, 2),
                "VIP",
                {"pillow": "firm", "view": "sea", "late_checkout": True, "allergies": ["nuts"]},
                "Предпочитает верхние этажи; чувствительна к шуму.",
            ),
            mk(
                "Петров",
                "Илья",
                "Сергеевич",
                date(1991, 4, 15),
                "Business",
                {"quiet_room": True, "needs_invoice": True, "breakfast": True},
                "Частые командировки; нужны закрывающие документы.",
            ),
            mk(
                "Ким",
                "Мария",
                "Владимировна",
                date(1985, 7, 28),
                "Family",
                {"extra_bed": "crib", "room_near_elevator": False},
                "Путешествует с ребёнком; просит детскую кроватку.",
            ),
            mk(
                "Васильев",
                "Олег",
                "Павлович",
                date(1994, 2, 9),
                "Leisure",
                {"excursions": True, "seafood": True},
                "Интересуется экскурсиями и локальными ресторанами.",
            ),
            mk(
                "Орлова",
                "Елена",
                "Андреевна",
                date(1979, 12, 4),
                "Loyalty",
                {"view": "sea", "parking": True, "arrival_time": "late"},
                "Часто приезжает поздно вечером; предпочитает парковку.",
            ),
            mk(
                "Новикова",
                "Светлана",
                "Романовна",
                date(1996, 9, 17),
                "New",
                {"spa": True, "breakfast": True},
                "Новый клиент; интересуется спа-программами.",
            ),
        ]

        contacts = {
            "Смирнова": [("email", "anna.smirnova@example.com", True, 1), ("phone", "+7 900 100-22-33", False, 2), ("whatsapp", "+7 900 100-22-33", True, 1)],
            "Петров": [("email", "ilya.petrov@workmail.ru", True, 1), ("phone", "+7 900 200-33-44", True, 1), ("telegram", "@ilya_petrov", False, 3)],
            "Ким": [("email", "m.kim@travelbox.me", True, 1), ("phone", "+7 900 300-44-55", True, 1)],
            "Васильев": [("phone", "+7 900 400-55-66", True, 1), ("email", "oleg.vasiliev@sunroute.ru", False, 2)],
            "Орлова": [("email", "elena.orlova@stayclub.com", True, 1), ("phone", "+7 900 500-66-77", True, 1), ("whatsapp", "+7 900 500-66-77", False, 2)],
            "Новикова": [("email", "s.novikova@mail.ru", True, 1), ("phone", "+7 916 124-11-09", True, 1)],
        }
        for c in clients:
            for t, v, primary, prio in contacts[c.last_name]:
                channel, created = models.ContactChannel.objects.get_or_create(
                    type_id=t,
                    value=v,
                    defaults={
                        "client": c,
                        "is_primary": primary,
                        "priority": prio,
                        "verified_at": timezone.now() - timedelta(days=30) if t in {"email", "phone"} else None,
                    },
                )
                if not created and channel.client_id != c.id:
                    channel.client = c
                    channel.save(update_fields=["client", "updated_at"])

        consents = {
            "Смирнова": [("marketing", "granted", "check-in form"), ("sms", "granted", "front desk")],
            "Петров": [("marketing", "denied", "email")],
            "Ким": [("marketing", "granted", "website booking")],
            "Васильев": [("marketing", "granted", "front desk")],
            "Орлова": [("marketing", "granted", "loyalty program"), ("email", "granted", "loyalty program")],
            "Новикова": [("marketing", "granted", "website")],
        }
        for c in clients:
            for t, status, source in consents[c.last_name]:
                models.Consent.objects.get_or_create(
                    client=c,
                    type_id=t,
                    status_id=status,
                    source=source,
                    defaults={"obtained_at": timezone.now() - timedelta(days=180)},
                )

        def set_loyalty(last_name, level, points):
            client = next(x for x in clients if x.last_name == last_name)
            if not client.loyalty_level_id:
                client.loyalty_level_id = level
                client.loyalty_points = points
                client.save(update_fields=["loyalty_level", "loyalty_points"])

        set_loyalty("Смирнова", "Gold", 12450)
        set_loyalty("Петров", "Silver", 3420)
        set_loyalty("Ким", "Bronze", 980)
        set_loyalty("Орлова", "Platinum", 30210)

        return clients

    def _bookings(self, today, c1, c2, c3, c4, c5, c6, standard, superior, deluxe, family, flexible, nonref, corporate, room_by_number):
        specs = [
            (c1, deluxe, flexible, room_by_number["305"], today - timedelta(days=10), today - timedelta(days=7), "completed", "website", Decimal("84000.00")),
            (c2, superior, corporate, room_by_number["203"], today - timedelta(days=3), today + timedelta(days=1), "in_house", "corporate", Decimal("42500.00")),
            (c3, family, flexible, room_by_number["401"], today + timedelta(days=7), today + timedelta(days=12), "confirmed", "ota", Decimal("97200.00")),
            (c4, standard, flexible, None, today + timedelta(days=2), today + timedelta(days=4), "cancelled", "website", Decimal("36400.00")),
            (c5, deluxe, nonref, room_by_number["306"], today + timedelta(days=20), today + timedelta(days=22), "confirmed", "loyalty", Decimal("58900.00")),
            (c6, superior, flexible, None, today + timedelta(days=1), today + timedelta(days=3), "pending", "website", Decimal("31800.00")),
        ]
        result = []
        for client, category, rate, room, check_in, check_out, status, source, total in specs:
            result.append(
                models.Booking.objects.get_or_create(
                    client=client,
                    category=category,
                    rate=rate,
                    check_in=check_in,
                    check_out=check_out,
                    defaults={"room": room, "status_id": status, "source_id": source, "total_cost": total},
                )[0]
            )
        return result

    def _booking_guests(self, booking):
        if booking.guests.exists():
            return
        models.BookingGuest.objects.create(booking=booking, full_name=str(booking.client), role_id="primary", document="Паспорт РФ")
        models.BookingGuest.objects.create(booking=booking, full_name="Ким Артём", role_id="child", document="")

    def _booking_items(
        self,
        b1,
        b2,
        b3,
        b5,
        sea_weekend,
        family_comfort,
        business_express,
        transfer,
        late_checkout,
        breakfast,
        parking,
        spa,
    ):
        def service_item(booking, service, qty, amount, comment=""):
            models.BookingItem.objects.get_or_create(
                booking=booking,
                item_type=models.BookingItem.ITEM_TYPE_SERVICE,
                service=service,
                offer=None,
                defaults={"quantity": qty, "amount": amount, "comment": comment},
            )

        def offer_item(booking, offer, qty, amount, comment=""):
            models.BookingItem.objects.get_or_create(
                booking=booking,
                item_type=models.BookingItem.ITEM_TYPE_OFFER,
                offer=offer,
                service=None,
                defaults={"quantity": qty, "amount": amount, "comment": comment},
            )

        def fee_item(booking, qty, amount, comment):
            models.BookingItem.objects.get_or_create(
                booking=booking,
                item_type=models.BookingItem.ITEM_TYPE_FEE,
                service=None,
                offer=None,
                defaults={"quantity": qty, "amount": amount, "comment": comment},
            )

        offer_item(b1, sea_weekend, 1, Decimal("0.00"), "Пакет применён к тарифу.")
        service_item(b1, transfer, 1, Decimal("2500.00"))
        service_item(b1, spa, 1, Decimal("1500.00"))

        offer_item(b2, business_express, 1, Decimal("0.00"))
        fee_item(b2, 1, Decimal("500.00"), "Городской сбор")

        offer_item(b3, family_comfort, 1, Decimal("0.00"))
        service_item(b3, parking, 2, Decimal("1200.00"))

        service_item(b5, breakfast, 2, Decimal("1800.00"))
        service_item(b5, late_checkout, 1, Decimal("1800.00"))

    def _booking_cancellation(self, booking, cancellation_rules):
        if booking.cancelled_at:
            return
        booking.cancel_reason = "Изменились планы поездки."
        booking.cancel_penalty = Decimal("9100.00")
        booking.cancelled_at = timezone.now() - timedelta(days=1)
        booking.cancel_source = "website"
        booking.cancel_initiator = "guest"
        booking.save(update_fields=["cancel_reason", "cancel_penalty", "cancelled_at", "cancel_source", "cancel_initiator"])

    def _payments(self, bookings):
        payments = []
        for b in bookings:
            if b.payments.exists() or b.status_id == "pending":
                payments.extend(list(b.payments.all()))
                continue
            if b.status_id == "cancelled":
                payments.append(
                    models.Payment.objects.create(
                        booking=b,
                        amount=Decimal("0.00"),
                        method_id="card",
                        status_id="void",
                        provider_ref=f"pay_{b.id}_{b.client_id}",
                    )
                )
                continue
            method = "invoice" if b.source_id == "corporate" else "card"
            payments.append(
                models.Payment.objects.create(
                    booking=b,
                    amount=b.total_cost,
                    method_id=method,
                    status_id="paid",
                    provider_ref=f"pay_{b.id}_{b.client_id}",
                )
            )
        return payments

    def _payment_events(self, payments):
        for p in payments:
            if p.events.exists():
                continue
            models.PaymentEvent.objects.create(
                payment=p,
                status_id="created",
                payload={"ref": p.provider_ref},
                source="payments_service",
            )
            if p.status_id == "paid":
                models.PaymentEvent.objects.create(
                    payment=p,
                    status_id="captured",
                    payload={"amount": str(p.amount), "currency": "RUB"},
                    source="payments_service",
                )
            if p.status_id == "void":
                models.PaymentEvent.objects.create(
                    payment=p,
                    status_id="voided",
                    payload={"reason": "cancelled"},
                    source="payments_service",
                )

    def _tickets(self, now, booking_by_client_id, client_by_last):
        specs = [
            (client_by_last["Смирнова"], booking_by_client_id[client_by_last["Смирнова"].id], "Поздний выезд", "high", "open", now + timedelta(hours=6)),
            (client_by_last["Петров"], booking_by_client_id[client_by_last["Петров"].id], "Закрывающие документы", "medium", "in_progress", now + timedelta(days=1)),
            (client_by_last["Ким"], booking_by_client_id[client_by_last["Ким"].id], "Детская кроватка", "medium", "open", now + timedelta(hours=12)),
            (client_by_last["Васильев"], booking_by_client_id[client_by_last["Васильев"].id], "Отмена бронирования", "high", "resolved", None),
            (client_by_last["Орлова"], booking_by_client_id[client_by_last["Орлова"].id], "Парковка и поздний заезд", "low", "open", now + timedelta(days=2)),
        ]
        result = []
        for c, b, subject, priority, status, sla in specs:
            result.append(
                models.Ticket.objects.get_or_create(
                    client=c,
                    booking=b,
                    subject=subject,
                    defaults={"priority_id": priority, "status_id": status, "sla_due_at": sla},
                )[0]
            )
        return result

    def _messages(self, tickets):
        result = []
        for t in tickets:
            if t.messages.exists():
                result.extend(list(t.messages.all()))
                continue
            cc = t.client.contact_channels.order_by("-is_primary", "priority").first()
            channel = cc.type_id if cc else "email"
            result.append(
                models.Message.objects.create(
                    ticket=t,
                    contact_channel=cc,
                    channel_id=channel,
                    direction_id="inbound",
                    text=f"Здравствуйте! Вопрос по теме: {t.subject}.",
                )
            )
            result.append(
                models.Message.objects.create(
                    ticket=t,
                    contact_channel=cc,
                    channel_id=channel,
                    direction_id="outbound",
                    text="Приняли запрос, уточняем детали и вернёмся с ответом в ближайшее время.",
                )
            )
        return result

    def _templates(self):
        specs = [
            (
                "ticket_ack_email",
                "email",
                "Мы получили ваше обращение",
                "Здравствуйте!\n\nМы получили обращение и уже начали работу.\n\nС уважением,\nСлужба поддержки",
            ),
            ("late_checkout_offer", "whatsapp", "", "Можем предложить поздний выезд до 18:00 при наличии возможности. Подтвердить?"),
            (
                "invoice_ready",
                "email",
                "Документы готовы",
                "Добрый день!\n\nЗакрывающие документы подготовлены. При необходимости отправим оригиналы курьером.",
            ),
            ("spa_offer", "telegram", "", "Доступна запись в спа-зону на удобное время. Хотите подобрать слот?"),
        ]
        result = []
        for code, channel, subject, body in specs:
            result.append(
                models.MessageTemplate.objects.get_or_create(
                    code=code,
                    defaults={"channel_id": channel, "subject": subject, "body": body, "active": True},
                )[0]
            )
        return result

    def _campaigns(self, now):
        specs = [
            (
                "Весенние выходные у моря",
                {"segment": ["VIP", "Loyalty"], "interests": ["spa", "sea_view"]},
                now - timedelta(days=14),
                None,
                {"sent": 480, "opened": 212, "clicked": 58},
                "running",
            ),
            (
                "Бизнес-обновления",
                {"segment": ["Business"], "channels": ["email"]},
                now - timedelta(days=30),
                now - timedelta(days=7),
                {"sent": 320, "opened": 180, "clicked": 41},
                "finished",
            ),
        ]
        result = []
        for name, segment, started, finished, metrics, status in specs:
            result.append(
                models.Campaign.objects.get_or_create(
                    name=name,
                    defaults={
                        "segment": segment,
                        "started_at": started,
                        "finished_at": finished,
                        "metrics": metrics,
                        "status_id": status,
                    },
                )[0]
            )
        return result

    def _campaign_templates(self, campaigns, templates):
        c = {x.name: x for x in campaigns}
        t = {x.code: x for x in templates}
        pairs = [
            ("Весенние выходные у моря", "late_checkout_offer"),
            ("Весенние выходные у моря", "spa_offer"),
            ("Бизнес-обновления", "invoice_ready"),
            ("Бизнес-обновления", "ticket_ack_email"),
        ]
        for cname, tcode in pairs:
            c[cname].message_templates.add(t[tcode])

    def _wire_messages(self, messages, templates, campaigns):
        t = {x.code: x for x in templates}
        c = {x.name: x for x in campaigns}
        for m in messages:
            if m.direction_id != "outbound" or m.template_id or m.campaign_id:
                continue
            if "Поздний выезд" in m.ticket.subject and m.channel_id in {"whatsapp", "phone"}:
                m.template = t["late_checkout_offer"]
                m.campaign = c.get("Весенние выходные у моря")
            elif "Документы" in m.ticket.subject:
                m.template = t["invoice_ready"]
                m.campaign = c.get("Бизнес-обновления")
            elif m.channel_id == "telegram":
                m.template = t["spa_offer"]
            else:
                m.template = t["ticket_ack_email"]
            m.save(update_fields=["template", "campaign"])

    def _tasks(self, now, tickets, front_office, finance, housekeeping, emp_fo, emp_fin, emp_hk):
        tasks = []
        for t in tickets:
            if t.tasks.exists():
                tasks.extend(list(t.tasks.all()))
                continue
            if "Документы" in t.subject:
                tasks.append(
                    models.Task.objects.create(
                        ticket=t,
                        booking=t.booking,
                        department=finance,
                        assignee=emp_fin,
                        type_id="documents",
                        status_id="in_progress",
                        description="Подготовить счёт и закрывающие документы, отправить клиенту.",
                        due=now + timedelta(hours=8),
                    )
                )
            elif "Детская" in t.subject:
                tasks.append(
                    models.Task.objects.create(
                        ticket=t,
                        booking=t.booking,
                        department=housekeeping,
                        assignee=emp_hk,
                        type_id="room_setup",
                        status_id="open",
                        description="Подготовить детскую кроватку и комплект белья.",
                        due=now + timedelta(days=1),
                    )
                )
            else:
                tasks.append(
                    models.Task.objects.create(
                        ticket=t,
                        booking=t.booking,
                        department=front_office,
                        assignee=emp_fo,
                        type_id="guest_support",
                        status_id="open",
                        description="Связаться с гостем, уточнить детали запроса и предложить варианты.",
                        due=t.sla_due_at or (now + timedelta(hours=12)),
                    )
                )
        return tasks

    def _audit(self, emp_it, bookings, tasks):
        if bookings:
            models.AuditLog.objects.get_or_create(
                actor_employee=emp_it,
                entity="Room",
                entity_id=1,
                action="update",
                defaults={"details": {"field": "state", "from": "cleaning", "to": "available"}, "risk": "low"},
            )
        if tasks:
            models.AuditLog.objects.get_or_create(
                actor_employee=emp_it,
                entity="Task",
                entity_id=tasks[0].id,
                action="create",
                defaults={"details": {"department": tasks[0].department.name}, "risk": "low"},
            )
