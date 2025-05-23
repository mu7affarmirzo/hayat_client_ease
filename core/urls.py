from django.urls import path, include


urlpatterns = [
    path('', include('core.reception.urls.auth')),
    path('booking/', include('core.reception.urls.registration')),
    path('payments/', include('core.reception.urls.payments')),
    path('adminstration/', include('core.adminstration.urls.adminstration')),
    path('adminstration/services/', include('core.adminstration.urls.services')),
]
