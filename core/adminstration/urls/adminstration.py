from django.urls import path

from core.reception.views import stats

app_name = 'administration'


urlpatterns = [

    path('therapist-statistics/', stats.therapist_statistics, name='therapist_statistics'),
    path('export-therapist-statistics/', stats.export_therapist_statistics, name='export_therapist_statistics'),
    path('export-therapist-statistics-word/', stats.export_therapist_statistics_word, name='export_therapist_statistics_word'),
]
