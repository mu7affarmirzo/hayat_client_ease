from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from core.models import PatientModel, ServiceModel, Account, ServiceTypeModel
from core.reception.forms.registration import PatientRegistrationForm, SessionForm


def load_services(request):
    service_type_id = request.GET.get('service_type_id')
    services = ServiceModel.objects.filter(type__id=service_type_id)
    return render(request, 'reception/services_dropdown_list_options.html', {'services': services})


# @role_required(role='logus', login_url='logus_auth:logout')
def register_booking_view(request):

    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.created_by = request.user
            session.save()
            return redirect('reception_auth:main_screen')
    else:
        form = SessionForm()
    patients = PatientModel.objects.all()
    service_types = ServiceTypeModel.objects.all()
    therapists = Account.objects.filter(is_therapist=True)
    return render(
        request, 'reception/create_booking.html',
        {
            'form': form,
            'patients': patients,
            'service_types': service_types,
            'therapists': therapists,
        }
    )


def session_detailed_view(request, pk):
    return render(request, 'reception/session_detailed.html', {})


@csrf_exempt
def add_new_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_by = request.user
            patient.modified_by = request.user
            patient.save()
            return redirect('reception_registration:register-booking')  # Replace with your success URL
    else:
        return redirect('logus_registration:register-booking')
    return render(request, 'reception/create_booking.html', {'form': form})