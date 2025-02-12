from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from core.models import PatientModel, ServiceModel, Account, ServiceTypeModel, SessionModel, PaymentModel
from core.reception.forms.payments import SingularPaymentCreateSerializer, WholePaymentCreateSerializer
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


@login_required
def session_detailed_view(request, pk):
    session = get_object_or_404(SessionModel, pk=pk)
    payments = session.payments.all()
    methods = PaymentModel.method.field.choices

    context = {
        'session': session,
        'payments': payments,
        'methods': methods
    }
    return render(request, 'reception/session_detailed.html', context)


@login_required
def singular_payment_view(request, pk):
    session = get_object_or_404(SessionModel, pk=pk)

    if request.method == 'POST':
        form = SingularPaymentCreateSerializer(data=request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            payment.session = session
            payment.save()
            return redirect('reception_registration:session-detailed', pk=pk)
    return redirect('reception_registration:session-detailed', pk=pk)


@login_required
def whole_payment_view(request, pk):
    session = get_object_or_404(SessionModel, pk=pk)

    if request.method == 'POST':
        form = WholePaymentCreateSerializer(data=request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            payment.session = session
            payment.amount = session.remaining_payed_amount
            payment.save()
            return redirect('reception_auth:main_screen')
        print(form.errors)
    return redirect('reception_registration:session-detailed', pk=pk)


@csrf_exempt
def add_new_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_by = request.user
            patient.save()
            return redirect('reception_registration:register-booking')  # Replace with your success URL
    else:
        return redirect('reception_registration:register-booking')
    return render(request, 'reception/create_booking.html', {'form': form})

