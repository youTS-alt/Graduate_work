from django.contrib import admin

from . import models


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'middle_name', 'segment', 'created_at', 'updated_at')
    search_fields = ('last_name', 'first_name', 'middle_name')


@admin.register(models.ContactChannel)
class ContactChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'type', 'value', 'is_primary', 'verified_at', 'priority')
    search_fields = ('value',)
    list_filter = ('type', 'is_primary')


@admin.register(models.Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'category', 'rate', 'room', 'check_in', 'check_out', 'status', 'total_cost')
    list_filter = ('status', 'source')
    search_fields = ('client__last_name', 'client__first_name')


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'booking', 'subject', 'priority', 'status', 'sla_due_at', 'created_at')
    list_filter = ('priority', 'status')
    search_fields = ('subject', 'client__last_name', 'client__first_name')


admin.site.register(models.Consent)
admin.site.register(models.RoomCategory)
admin.site.register(models.Room)
admin.site.register(models.Rate)
admin.site.register(models.CancellationRule)
admin.site.register(models.Service)
admin.site.register(models.Offer)
admin.site.register(models.OfferService)
admin.site.register(models.BookingGuest)
admin.site.register(models.BookingItem)
admin.site.register(models.Payment)
admin.site.register(models.PaymentEvent)
admin.site.register(models.Message)
admin.site.register(models.MessageTemplate)
admin.site.register(models.Campaign)
admin.site.register(models.Department)
admin.site.register(models.Employee)
admin.site.register(models.Task)
admin.site.register(models.Role)
admin.site.register(models.Permission)
admin.site.register(models.EmployeeRole)
admin.site.register(models.RolePermission)
admin.site.register(models.AuditLog)

# FK lookup tables
admin.site.register(models.BookingStatus)
admin.site.register(models.BookingSource)
admin.site.register(models.TicketStatus)
admin.site.register(models.TicketPriority)
admin.site.register(models.TaskStatus)
admin.site.register(models.TaskType)
admin.site.register(models.RoomState)
admin.site.register(models.PaymentMethod)
admin.site.register(models.PaymentStatus)
admin.site.register(models.PaymentEventStatus)
admin.site.register(models.ClientSegment)
admin.site.register(models.LoyaltyLevel)
admin.site.register(models.ContactChannelType)
admin.site.register(models.ConsentType)
admin.site.register(models.ConsentStatus)
admin.site.register(models.MealPlan)
admin.site.register(models.BookingGuestRole)
admin.site.register(models.MessageChannel)
admin.site.register(models.MessageDirection)
admin.site.register(models.CampaignStatus)
admin.site.register(models.EmployeeStatus)

