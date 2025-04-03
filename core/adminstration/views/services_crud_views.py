from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse

from core.models import ServiceModel, ServiceTypeModel
from core.adminstration.forms.service_crud_forms import ServiceForm, ServiceTypeForm


# Service Type Views
@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_type_list(request):
    service_types = ServiceTypeModel.objects.all().order_by('type')
    return render(request, 'adminstration/services/service_type_list.html', {
        'service_types': service_types
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_type_detail(request, pk):
    service_type = get_object_or_404(ServiceTypeModel, pk=pk)
    services = service_type.services.all()
    return render(request, 'adminstration/services/service_type_detail.html', {
        'service_type': service_type,
        'services': services
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_type_create(request):
    if request.method == "POST":
        form = ServiceTypeForm(request.POST)
        if form.is_valid():
            service_type = form.save(commit=False)
            service_type.created_by = request.user
            service_type.save()
            messages.success(request, 'Тип услуги успешно создан')
            return redirect('administration_services:service_type_list')
    else:
        form = ServiceTypeForm()

    return render(request, 'adminstration/services/service_type_form.html', {
        'form': form,
        'title': 'Добавить тип услуги'
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_type_update(request, pk):
    service_type = get_object_or_404(ServiceTypeModel, pk=pk)
    if request.method == "POST":
        form = ServiceTypeForm(request.POST, instance=service_type)
        if form.is_valid():
            service_type = form.save(commit=False)
            service_type.modified_by = request.user
            service_type.save()
            messages.success(request, 'Тип услуги успешно обновлен')
            return redirect('administration_services:service_type_list')
    else:
        form = ServiceTypeForm(instance=service_type)

    return render(request, 'adminstration/services/service_type_form.html', {
        'form': form,
        'title': 'Редактировать тип услуги'
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_type_delete(request, pk):
    service_type = get_object_or_404(ServiceTypeModel, pk=pk)
    if request.method == "POST":
        service_type.delete()
        messages.success(request, 'Тип услуги успешно удален')
        return redirect('administration_services:service_type_list')

    return render(request, 'adminstration/services/service_type_confirm_delete.html', {
        'service_type': service_type
    })


# Service Views
@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_list(request):
    services = ServiceModel.objects.all().order_by('type', 'name')
    return render(request, 'adminstration/services/service_list.html', {
        'services': services
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_detail(request, pk):
    service = get_object_or_404(ServiceModel, pk=pk)
    return render(request, 'adminstration/services/service_detail.html', {
        'service': service
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_create(request):
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.created_by = request.user
            service.save()
            messages.success(request, 'Услуга успешно создана')
            return redirect('administration_services:service_list')
    else:
        form = ServiceForm()

    return render(request, 'adminstration/services/service_form.html', {
        'form': form,
        'title': 'Добавить услугу'
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_update(request, pk):
    service = get_object_or_404(ServiceModel, pk=pk)
    if request.method == "POST":
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save(commit=False)
            service.modified_by = request.user
            service.save()
            messages.success(request, 'Услуга успешно обновлена')
            return redirect('administration_services:service_list')
    else:
        form = ServiceForm(instance=service)

    return render(request, 'adminstration/services/service_form.html', {
        'form': form,
        'title': 'Редактировать услугу'
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def service_delete(request, pk):
    service = get_object_or_404(ServiceModel, pk=pk)
    if request.method == "POST":
        service.delete()
        messages.success(request, 'Услуга успешно удалена')
        return redirect('administration_services:service_list')

    return render(request, 'adminstration/services/service_confirm_delete.html', {
        'service': service
    })