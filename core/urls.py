from django.urls import path, include


urlpatterns = [
    path('', include('core.reception.urls.auth')),
    path('booking/', include('core.reception.urls.registration')),
    path('adminstration/', include('core.adminstration.urls.adminstration')),
]
