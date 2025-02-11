from django.urls import path

from core.reception.views.registration import register_booking_view, add_new_patient, load_services, \
    session_detailed_view

app_name = 'reception_registration'


urlpatterns = [
    path('register-session/', register_booking_view, name='register-booking'),
    path('session-detailed/<int:pk>', session_detailed_view, name='session-detailed'),
    path('add-new-patient/', add_new_patient, name='add-new-patient'),
    path('load-services/', load_services, name='load_services'),
]
