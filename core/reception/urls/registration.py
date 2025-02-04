from django.urls import path

from core.reception.views.registration import register_booking_view

app_name = 'reception_registration'

urlpatterns = [
    path('register-booking/', register_booking_view, name='register-booking'),
]
