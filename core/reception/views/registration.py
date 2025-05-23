from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from core.models import PatientModel, ServiceModel, Account, ServiceTypeModel, SessionBookingModel, PaymentModel, \
    ReferralDoctorModel, TherapistModel, IndividualSessionModel
from core.reception.forms.payments import SingularPaymentCreateSerializer, WholePaymentCreateSerializer, \
    WithdrawalPaymentForm
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
    therapists = TherapistModel.objects.all()
    referral_doctors = ReferralDoctorModel.objects.all()

    return render(
        request, 'reception/create_booking.html',
        {
            'form': form,
            'patients': patients,
            'service_types': service_types,
            'therapists': therapists,
            'referral_doctors': referral_doctors,
        }
    )


@login_required
def session_detailed_view(request, pk):
    """View for detailed session information with individual sessions"""
    booking = get_object_or_404(SessionBookingModel, pk=pk)
    payments = booking.payments.all()
    methods = PaymentModel.method.field.choices

    # Get individual sessions
    individual_sessions = booking.individual_sessions.all().order_by('session_number')

    is_editable = booking.status in ['active']

    context = {
        'session': booking,  # Keep the same variable name for backward compatibility
        'individual_sessions': individual_sessions,
        'payments': payments,
        'methods': methods,
        'is_editable': is_editable,
    }
    return render(request, 'reception/session_detailed.html', context)


@login_required
def confirm_individual_session(request, booking_pk, session_number):
    """Mark an individual session as completed"""
    booking = get_object_or_404(SessionBookingModel, pk=booking_pk)

    try:
        # Get the individual session
        session = booking.individual_sessions.get(session_number=session_number)

        # Check if previous sessions are completed
        previous_sessions = booking.individual_sessions.filter(
            session_number__lt=session_number
        )

        if previous_sessions.exists() and previous_sessions.filter(status='pending').exists():
            messages.error(request, 'Нельзя отметить этот сеанс - предыдущие сеансы еще не проведены.')
            return redirect('reception_registration:session-detailed', pk=booking_pk)

        # Mark as completed
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.save()

        # Manually update the proceeded_sessions count
        completed_count = booking.individual_sessions.filter(status='completed').count()
        booking.proceeded_sessions = completed_count
        booking.save(update_fields=['proceeded_sessions'])

        messages.success(request, f'Сеанс #{session_number} успешно отмечен как проведенный')
    except IndividualSessionModel.DoesNotExist:
        messages.error(request, f'Сеанс #{session_number} не найден')

    return redirect('reception_registration:session-detailed', pk=booking_pk)


@login_required
def cancel_individual_session(request, booking_pk, session_number):
    """Mark an individual session as canceled"""
    booking = get_object_or_404(SessionBookingModel, pk=booking_pk)

    try:
        # Get the individual session
        session = booking.individual_sessions.get(session_number=session_number)

        # Only completed sessions can be canceled
        # if session.status != 'completed':
        #     messages.error(request, f'Сеанс #{session_number} не является проведенным и не может быть отменен')
        #     return redirect('reception_registration:session-detailed', pk=booking_pk)

        # Check if this is the last completed session
        last_completed = booking.individual_sessions.filter(
            status='completed'
        ).order_by('-session_number').first()

        # if last_completed.session_number != session.session_number:
        #     messages.error(request, 'Можно отменить только последний проведенный сеанс')
        #     return redirect('reception_registration:session-detailed', pk=booking_pk)

        # Mark as pending again
        session.status = 'cancelled'
        session.completed_at = timezone.now()
        session.save()

        # Manually update the proceeded_sessions count
        completed_count = booking.individual_sessions.filter(status='completed').count()
        booking.proceeded_sessions = completed_count
        booking.save(update_fields=['proceeded_sessions'])

        messages.success(request, f'Сеанс #{session_number} отменен')
    except IndividualSessionModel.DoesNotExist:
        messages.error(request, f'Сеанс #{session_number} не найден')

    return redirect('reception_registration:session-detailed', pk=booking_pk)


@login_required
def update_session_notes(request, booking_pk, session_number):
    """Update notes for an individual session"""
    booking = get_object_or_404(SessionBookingModel, pk=booking_pk)

    if request.method == 'POST':
        notes = request.POST.get('notes', '')

        try:
            # Get the individual session
            session = booking.individual_sessions.get(session_number=session_number)

            # Update notes
            session.notes = notes
            session.save()

            messages.success(request, f'Примечания для сеанса #{session_number} обновлены')
        except IndividualSessionModel.DoesNotExist:
            messages.error(request, f'Сеанс #{session_number} не найден')

    return redirect('reception_registration:session-detailed', pk=booking_pk)


@login_required
def update_proceeded_sessions(request, pk):
    session = get_object_or_404(SessionBookingModel, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'increment' and session.proceeded_sessions < session.quantity:
            session.proceeded_sessions += 1
            session.save()
            messages.success(request, 'Сеанс успешно отмечен как проведенный.')

        elif action == 'decrement' and session.proceeded_sessions > 0:
            session.proceeded_sessions -= 1
            session.save()
            messages.success(request, 'Количество проведенных сеансов уменьшено.')

        elif action == 'set':
            try:
                new_value = int(request.POST.get('proceeded_sessions', 0))
                if 0 <= new_value <= session.quantity:
                    session.proceeded_sessions = new_value
                    session.save()
                    messages.success(request, f'Количество проведенных сеансов обновлено до {new_value}.')
                else:
                    messages.error(request,
                                   'Введенное значение должно быть между 0 и максимальным количеством сеансов.')
            except ValueError:
                messages.error(request, 'Введите корректное число.')

    return redirect('reception_registration:session-detailed', pk=pk)


@login_required
def singular_payment_view(request, pk):
    session = get_object_or_404(SessionBookingModel, pk=pk)

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
    session = get_object_or_404(SessionBookingModel, pk=pk)

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


@login_required
def withdrawal_payment_view(request, pk):
    """Process a withdrawal/refund for a client who paid for more sessions than used"""
    session = get_object_or_404(SessionBookingModel, pk=pk)

    # Calculate the maximum refundable amount
    # This is based on remaining sessions that won't be used
    if session.proceeded_sessions < session.quantity:
        unused_sessions = session.quantity - session.proceeded_sessions
        session_price = session.total_price / session.quantity
        max_refundable = unused_sessions * session_price
    else:
        # If all sessions are used, don't allow withdrawal
        max_refundable = 0

    if request.method == 'POST':
        form = WithdrawalPaymentForm(request.POST)
        if form.is_valid():
            # Get the withdrawal amount (user enters positive value)
            withdrawal_amount = form.cleaned_data['amount']

            # Verify withdrawal amount doesn't exceed what's refundable
            if withdrawal_amount > max_refundable:
                messages.error(request, f"Сумма возврата не может превышать {max_refundable:,.0f} сум")
                return redirect('reception_registration:session-detailed', pk=pk)

            # Save withdrawal (form's save method will convert to negative)
            payment = form.save(commit=False)
            payment.created_by = request.user
            payment.session = session
            payment.save()

            # You might want to update session quantity to match used sessions
            # Uncomment if you want this behavior
            # if session.proceeded_sessions < session.quantity:
            #     session.quantity = session.proceeded_sessions
            #     session.save(update_fields=['quantity'])

            messages.success(request, f"Возврат на сумму {withdrawal_amount:,.0f} сум успешно произведен")
            return redirect('reception_registration:session-detailed', pk=pk)
        else:
            print(form.errors)
            # If the form has errors, display them
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    # For GET requests or invalid forms, redirect back to the session detail
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

