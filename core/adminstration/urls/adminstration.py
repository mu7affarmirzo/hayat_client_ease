from django.urls import path

from core.adminstration.views import stats, referral_docs_stats

app_name = 'administration'

urlpatterns = [

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
