from django.urls import path

from core.reception.views.auth import close_session
from core.reception.views.registration import (
    register_booking_view, add_new_patient, load_services,
    session_detailed_view, singular_payment_view, whole_payment_view, update_proceeded_sessions,
    confirm_individual_session, cancel_individual_session, update_session_notes,
)

from core.reception.views import stats

app_name = 'reception_registration'

urlpatterns = [
    path('close-session/<int:session_id>/', close_session, name='close-session'),

    path('register-session/', register_booking_view, name='register-booking'),

    path('session-detailed/<int:pk>', session_detailed_view, name='session-detailed'),
    # Individual session management
    path('session/<int:booking_pk>/confirm/<int:session_number>/',
         confirm_individual_session, name='confirm_individual_session'),

    path('session/<int:booking_pk>/cancel/<int:session_number>/',
         cancel_individual_session, name='cancel_individual_session'),

    path('session/<int:booking_pk>/notes/<int:session_number>/',
         update_session_notes, name='update_session_notes'),

    path('session/<int:pk>/update-sessions/', update_proceeded_sessions, name='update_proceeded_sessions'),
    path('add-new-patient/', add_new_patient, name='add-new-patient'),
    path('load-services/', load_services, name='load_services'),
    path('make-singular-payment/<int:pk>', singular_payment_view, name='singular_payment'),
    path('make-whole-payment/<int:pk>', whole_payment_view, name='whole_payment'),

    # Therapist statistics
    path('therapist-statistics/', stats.therapist_statistics, name='therapist_statistics'),
    path('export-therapist-statistics/', stats.export_therapist_statistics, name='export_therapist_statistics'),
]
