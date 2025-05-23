# urls.py
from django.urls import path
from core.reception.views import payments_dashboard_view as views

urlpatterns = [
    # Main dashboard
    path('', views.payment_dashboard, name='payment_dashboard'),
    path('dashboard/', views.payment_dashboard, name='payment_dashboard'),

    # Payment CRUD operations
    path('create/', views.create_payment, name='create_payment'),
    path('create/<int:session_id>/', views.create_payment, name='create_payment_for_session'),
    path('<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('<int:payment_id>/edit/', views.edit_payment, name='edit_payment'),

    # Analytics and reporting
    path('analytics/', views.payment_analytics, name='payment_analytics'),
    path('export/', views.payment_export, name='payment_export'),

    # API endpoints (optional)
    path('api/stats/', views.payment_stats_api, name='payment_stats_api'),
    path('api/chart-data/', views.payment_chart_data, name='payment_chart_data'),
]