from django.urls import path

from core.reception.views.registration import register_booking_view, add_new_patient

app_name = 'reception_registration'


urlpatterns = [
    path('register-booking/', register_booking_view, name='register-booking'),
    path('add-new-patient/', add_new_patient, name='add-new-patient'),
]
