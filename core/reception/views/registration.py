from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from core.models import PatientModel, ServiceModel, Account, ServiceTypeModel
from core.reception.forms.registration import PatientRegistrationForm, SessionForm


def load_services(request):
    service_type_id = request.GET.get('service_type_id')
    services = ServiceModel.objects.filter(service_type_id=service_type_id).values('id', 'name')
    return JsonResponse(list(services), safe=False)


# @role_required(role='logus', login_url='logus_auth:logout')
def register_booking_view(request):

    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            booking = form.save()
            return redirect('reception_auth:main_screen', pk=booking.pk)
            # return redirect('logus_auth:main_screen')
    else:
        form = SessionForm()
    patients = PatientModel.objects.all()
    service_types = ServiceTypeModel.objects.all()
    massages = ServiceModel.objects.all()
    therapists = Account.objects.filter(is_therapist=True)
    return render(
        request, 'reception/create_booking.html',
        {
            'form': form,
            'patients': patients,
            'service_types': service_types,
            'massages': massages,
            'therapists': therapists,
        }
    )


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