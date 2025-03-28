from django.urls import path

from core.reception.views.registration import (
    register_booking_view, add_new_patient, load_services,
    session_detailed_view, singular_payment_view, whole_payment_view, update_proceeded_sessions,
)

from core.reception.views import stats

app_name = 'reception_registration'


urlpatterns = [
    path('register-session/', register_booking_view, name='register-booking'),
    path('session-detailed/<int:pk>', session_detailed_view, name='session-detailed'),
    path('session/<int:pk>/update-sessions/', update_proceeded_sessions, name='update_proceeded_sessions'),
    path('add-new-patient/', add_new_patient, name='add-new-patient'),
    path('load-services/', load_services, name='load_services'),
    path('make-singular-payment/<int:pk>', singular_payment_view, name='singular_payment'),
    path('make-whole-payment/<int:pk>', whole_payment_view, name='whole_payment'),

    # Therapist statistics
    path('therapist-statistics/', stats.therapist_statistics, name='therapist_statistics'),
    path('export-therapist-statistics/', stats.export_therapist_statistics, name='export_therapist_statistics'),
]
