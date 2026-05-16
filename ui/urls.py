from django.urls import path

from . import views
from . import crud

app_name = 'ui'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('system/save-page-screenshot/', views.save_page_screenshot, name='save_page_screenshot'),
    path('guests/', views.guests_list, name='guests_list'),
    path('guests/<int:id>/', views.guest_detail, name='guest_detail'),
    path('bookings/', views.bookings_list, name='bookings_list'),
    path('bookings/<int:id>/', views.booking_detail, name='booking_detail'),
    path('tickets/', views.tickets_list, name='tickets_list'),
    path('tickets/<int:id>/', views.ticket_detail, name='ticket_detail'),
    path('tasks/', views.tasks_board, name='tasks_board'),
    path('catalog/', views.catalog, name='catalog'),
    path('ai/', views.ai_console, name='ai_console'),
    path('ai/new-session/', views.ai_new_session, name='ai_new_session'),
    path('ai/chat/', views.ai_chat, name='ai_chat'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/data/', crud.crud_index, name='crud_index'),
    path('admin-panel/data/<slug:slug>/', crud.crud_list, name='crud_list'),
    path('admin-panel/data/<slug:slug>/create/', crud.crud_create, name='crud_create'),
    path('admin-panel/data/<slug:slug>/<path:pk>/edit/', crud.crud_update, name='crud_update'),
    path('admin-panel/data/<slug:slug>/<path:pk>/delete/', crud.crud_delete, name='crud_delete'),
    path('audit/', views.audit_log, name='audit_log'),
    path('ai/refresh-radar/', views.refresh_radar, name='refresh_radar'),
]
