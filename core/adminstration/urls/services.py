from django.urls import path

from core.adminstration.views import services_crud_views

app_name = 'administration_services'

urlpatterns = [

    # Service Types
    path('service-types/', services_crud_views.service_type_list, name='service_type_list'),
    path('service-types/<int:pk>/', services_crud_views.service_type_detail, name='service_type_detail'),
    path('service-types/new/', services_crud_views.service_type_create, name='service_type_create'),
    path('service-types/<int:pk>/edit/', services_crud_views.service_type_update, name='service_type_update'),
    path('service-types/<int:pk>/delete/', services_crud_views.service_type_delete, name='service_type_delete'),

    # Services
    path('services/', services_crud_views.service_list, name='service_list'),
    path('services/<int:pk>/', services_crud_views.service_detail, name='service_detail'),
    path('services/new/', services_crud_views.service_create, name='service_create'),
    path('services/<int:pk>/edit/', services_crud_views.service_update, name='service_update'),
    path('services/<int:pk>/delete/', services_crud_views.service_delete, name='service_delete'),


]
