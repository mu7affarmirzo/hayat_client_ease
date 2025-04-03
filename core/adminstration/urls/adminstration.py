from django.urls import path

from core.adminstration.views import stats, referral_docs_stats, doctors_crud_views, therapist_crud_views

app_name = 'administration'

urlpatterns = [
    # Therapist URLs
    path('therapists/', therapist_crud_views.TherapistListView.as_view(), name='therapist_list'),
    path('therapists/<int:pk>/', therapist_crud_views.TherapistDetailView.as_view(), name='therapist_detail'),
    path('therapists/add/', therapist_crud_views.TherapistCreateView.as_view(), name='therapist_create'),
    path('therapists/<int:pk>/edit/', therapist_crud_views.TherapistUpdateView.as_view(), name='therapist_update'),
    path('therapists/<int:pk>/delete/', therapist_crud_views.TherapistDeleteView.as_view(), name='therapist_delete'),

    # Referral Doctor URLs
    path('doctors/', doctors_crud_views.ReferralDoctorListView.as_view(), name='doctor_list'),
    path('doctors/<int:pk>/', doctors_crud_views.ReferralDoctorDetailView.as_view(), name='doctor_detail'),
    path('doctors/add/', doctors_crud_views.ReferralDoctorCreateView.as_view(), name='doctor_create'),
    path('doctors/<int:pk>/edit/', doctors_crud_views.ReferralDoctorUpdateView.as_view(), name='doctor_update'),
    path('doctors/<int:pk>/delete/', doctors_crud_views.ReferralDoctorDeleteView.as_view(), name='doctor_delete'),


    path('therapist-statistics/', stats.therapist_statistics, name='therapist_statistics'),
    path('export-therapist-statistics/', stats.export_therapist_statistics, name='export_therapist_statistics'),
    path('export-therapist-statistics-word/', stats.export_therapist_statistics_word,
         name='export_therapist_statistics_word'),

    # Add these URL patterns to your urls.py file

    path('referral-doctor-statistics/', referral_docs_stats.referral_doctor_statistics,
         name='referral_doctor_statistics'),
    path('referral-doctor-statistics/export/', referral_docs_stats.export_referral_doctor_statistics,
         name='export_referral_doctor_statistics'),
    path('referral-doctor-statistics/export/word/', referral_docs_stats.export_referral_doctor_statistics_word,
         name='export_referral_doctor_statistics_word'),


]
