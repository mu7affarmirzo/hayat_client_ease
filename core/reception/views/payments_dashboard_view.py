# views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone

from core.reception.forms.payments_form import PaymentFilterForm, PaymentCreateForm, PaymentEditForm
from core.models import PaymentModel, SessionBookingModel


@login_required
def payment_dashboard(request):
    """Main payment dashboard with filtering and statistics"""

    # Get all payments initially
    payments = PaymentModel.objects.select_related(
        'session', 'session__patient', 'created_by'
    ).all()

    # Initialize filter form
    filter_form = PaymentFilterForm(request.GET or None)

    # Apply filters
    if filter_form.is_valid():
        # Date range filter
        if filter_form.cleaned_data.get('start_date'):
            payments = payments.filter(created_at__date__gte=filter_form.cleaned_data['start_date'])
        if filter_form.cleaned_data.get('end_date'):
            payments = payments.filter(created_at__date__lte=filter_form.cleaned_data['end_date'])

        # Payment method filter
        if filter_form.cleaned_data.get('method'):
            payments = payments.filter(method=filter_form.cleaned_data['method'])

        # Amount range filter
        if filter_form.cleaned_data.get('min_amount'):
            payments = payments.filter(amount__gte=filter_form.cleaned_data['min_amount'])
        if filter_form.cleaned_data.get('max_amount'):
            payments = payments.filter(amount__lte=filter_form.cleaned_data['max_amount'])

        # Payment type filter (payment vs withdrawal)
        payment_type = filter_form.cleaned_data.get('payment_type')
        if payment_type == 'payment':
            payments = payments.filter(amount__gt=0)
        elif payment_type == 'withdrawal':
            payments = payments.filter(amount__lt=0)

        # Patient search
        if filter_form.cleaned_data.get('patient_search'):
            search_term = filter_form.cleaned_data['patient_search']
            payments = payments.filter(
                Q(session__patient__f_name__icontains=search_term) |
                Q(session__patient__mid_name__icontains=search_term) |
                Q(session__patient__l_name__icontains=search_term) |
                Q(session__patient__home_phone_number__icontains=search_term) |
                Q(session__patient__mobile_phone_number__icontains=search_term)
            )

        # Created by filter
        if filter_form.cleaned_data.get('created_by'):
            payments = payments.filter(created_by=filter_form.cleaned_data['created_by'])

    # Calculate statistics
    stats = calculate_payment_stats(payments)

    # Pagination
    paginator = Paginator(payments, 25)  # 25 payments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'payments': page_obj,
        'filter_form': filter_form,
        'stats': stats,
        'total_count': payments.count(),
    }

    return render(request, 'reception/payments/dashboard.html', context)


@login_required
def payment_detail(request, payment_id):
    """Detailed view of a single payment"""
    payment = get_object_or_404(PaymentModel, id=payment_id)

    # Get related payments for the same session
    related_payments = PaymentModel.objects.filter(
        session=payment.session
    ).exclude(id=payment.id).order_by('-created_at')

    context = {
        'payment': payment,
        'related_payments': related_payments,
        'session': payment.session,
    }

    return render(request, 'reception/payments/details.html', context)


@login_required
def create_payment(request, session_id=None):
    """Create a new payment"""
    session = None
    if session_id:
        session = get_object_or_404(SessionBookingModel, id=session_id)

    if request.method == 'POST':
        form = PaymentCreateForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            payment.updated_by = request.user
            if session:
                payment.session = session
            payment.save()

            messages.success(request, 'Payment created successfully!')
            return redirect('payment_detail', payment_id=payment.id)
    else:
        initial_data = {}
        if session:
            initial_data['session'] = session
        form = PaymentCreateForm(initial=initial_data)

    context = {
        'form': form,
        'session': session,
    }

    return render(request, 'reception/payments/create.html', context)


@login_required
def payment_analytics(request):
    """Payment analytics and reporting dashboard"""

    # Get date range (default to last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()

    # Analytics data
    payments_in_period = PaymentModel.objects.filter(
        created_at__date__range=[start_date, end_date]
    )

    analytics = {
        'total_payments': payments_in_period.filter(amount__gt=0).aggregate(
            total=Sum('amount'), count=Count('id')
        ),
        'total_withdrawals': payments_in_period.filter(amount__lt=0).aggregate(
            total=Sum('amount'), count=Count('id')
        ),
        'by_method': {},
        'daily_stats': [],
        'top_patients': [],
    }

    # Payment methods breakdown
    for method_code, method_name in PaymentModel.method.field.choices:
        method_stats = payments_in_period.filter(method=method_code).aggregate(
            total=Sum('amount'), count=Count('id')
        )
        analytics['by_method'][method_name] = method_stats

    # Daily statistics for chart
    current_date = start_date
    while current_date <= end_date:
        daily_payments = payments_in_period.filter(created_at__date=current_date)
        daily_stats = {
            'date': current_date.strftime('%Y-%m-%d'),
            'total': daily_payments.aggregate(Sum('amount'))['amount__sum'] or 0,
            'count': daily_payments.count(),
        }
        analytics['daily_stats'].append(daily_stats)
        current_date += timedelta(days=1)

    context = {
        'analytics': analytics,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'reception/payments/analytics.html', context)


@login_required
def payment_export(request):
    """Export payments to CSV"""
    import csv
    from django.http import HttpResponse

    # Apply same filters as dashboard
    payments = PaymentModel.objects.select_related('session', 'session__patient').all()

    # Apply filters from GET parameters (reuse filter logic)
    filter_form = PaymentFilterForm(request.GET or None)
    if filter_form.is_valid():
        # Apply same filtering logic as dashboard
        if filter_form.cleaned_data.get('start_date'):
            payments = payments.filter(created_at__date__gte=filter_form.cleaned_data['start_date'])
        if filter_form.cleaned_data.get('end_date'):
            payments = payments.filter(created_at__date__lte=filter_form.cleaned_data['end_date'])
        if filter_form.cleaned_data.get('method'):
            payments = payments.filter(method=filter_form.cleaned_data['method'])
        # ... other filters

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Patient', 'Amount', 'Method', 'Type', 'Session ID',
        'Created At', 'Created By'
    ])

    for payment in payments:
        writer.writerow([
            payment.id,
            payment.session.patient.full_name if payment.session and payment.session.patient else 'N/A',
            payment.amount,
            payment.get_method_display(),
            'Withdrawal' if payment.is_withdrawal else 'Payment',
            payment.session.id if payment.session else 'N/A',
            payment.created_at.strftime('%Y-%m-%d %H:%M:%S') if payment.created_at else 'N/A',
            payment.created_by.username if payment.created_by else 'N/A',
        ])

    return response


def calculate_payment_stats(queryset):
    """Calculate statistics for a payment queryset"""
    stats = {
        'total_payments': queryset.filter(amount__gt=0).aggregate(
            total=Sum('amount'), count=Count('id')
        ),
        'total_withdrawals': queryset.filter(amount__lt=0).aggregate(
            total=Sum('amount'), count=Count('id')
        ),
        'by_method': {},
        'net_total': queryset.aggregate(Sum('amount'))['amount__sum'] or 0,
    }

    # Ensure we have default values
    stats['total_payments']['total'] = stats['total_payments']['total'] or 0
    stats['total_payments']['count'] = stats['total_payments']['count'] or 0
    stats['total_withdrawals']['total'] = stats['total_withdrawals']['total'] or 0
    stats['total_withdrawals']['count'] = stats['total_withdrawals']['count'] or 0

    # Method breakdown
    for method_code, method_name in PaymentModel.method.field.choices:
        method_stats = queryset.filter(method=method_code).aggregate(
            total=Sum('amount'), count=Count('id')
        )
        stats['by_method'][method_name] = {
            'total': method_stats['total'] or 0,
            'count': method_stats['count'] or 0,
        }

    return stats


@login_required
def edit_payment(request, payment_id):
    """Edit an existing payment"""
    payment = get_object_or_404(PaymentModel, id=payment_id)

    if request.method == 'POST':
        form = PaymentEditForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.updated_by = request.user
            payment.save()

            messages.success(request, 'Payment updated successfully!')
            return redirect('payment_detail', payment_id=payment.id)
    else:
        form = PaymentEditForm(instance=payment)

    context = {
        'form': form,
        'payment': payment,
    }

    return render(request, 'reception/payments/edit.html', context)


@login_required
def payment_stats_api(request):
    """API endpoint for payment statistics"""
    payments = PaymentModel.objects.all()

    # Apply basic filters if provided
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        payments = payments.filter(created_at__date__gte=start_date)

    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        payments = payments.filter(created_at__date__lte=end_date)

    stats = calculate_payment_stats(payments)

    return JsonResponse({
        'success': True,
        'stats': stats,
        'total_count': payments.count(),
    })


@login_required
def payment_chart_data(request):
    """API endpoint for chart data"""
    # Get date range (default to last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()

    payments = PaymentModel.objects.filter(
        created_at__date__range=[start_date, end_date]
    )

    # Daily data
    daily_stats = []
    current_date = start_date
    while current_date <= end_date:
        daily_payments = payments.filter(created_at__date=current_date)
        daily_stats.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'total': daily_payments.aggregate(Sum('amount'))['amount__sum'] or 0,
            'count': daily_payments.count(),
        })
        current_date += timedelta(days=1)

    # Method breakdown
    method_stats = {}
    for method_code, method_name in PaymentModel.method.field.choices:
        method_payments = payments.filter(method=method_code)
        method_stats[method_name] = {
            'total': method_payments.aggregate(Sum('amount'))['amount__sum'] or 0,
            'count': method_payments.count(),
        }

    return JsonResponse({
        'success': True,
        'daily_stats': daily_stats,
        'method_stats': method_stats,
    })


