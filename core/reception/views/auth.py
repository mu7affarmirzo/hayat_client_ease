from http.client import HTTPResponse

from django.contrib.auth import authenticate, logout, login
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect

from core.adminstration.forms.auth import AccountAuthenticationForm
from core.models import PaymentModel, SessionBookingModel


BOOKINGS_PER_PAGE = 30


def paginate_page(request, queries):
    page = request.GET.get('page', 1)
    sessions_paginator = Paginator(queries, BOOKINGS_PER_PAGE)

    try:
        sessions = sessions_paginator.page(page)
    except PageNotAnInteger:
        sessions = sessions_paginator.page(BOOKINGS_PER_PAGE)
    except EmptyPage:
        sessions = sessions_paginator.page(sessions_paginator.num_pages)
    return sessions

def login_view(request):
    context = {}
    user = request.user

    if user.is_authenticated:
        return redirect("reception_auth:main_screen")

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():

            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                return redirect("reception_auth:main_screen")

    form = AccountAuthenticationForm()

    context['login_form'] = form
    return render(request, 'reception/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')


# @role_required(role='sanatorium', login_url='sanatorium_auth:logout')
def main_screen_view(request):

    # Get query parameters
    query = request.GET.get('table_search', '')
    sort_param = request.GET.get('sort', '')

    # Start with all sessions or filter by your business logic
    sessions = SessionBookingModel.objects.all()

    # Apply search if provided
    if query:
        sessions = sessions.filter(
            Q(patient__f_name__icontains=query) |
            Q(patient__created_at__icontains=query) |
            Q(patient__mobile_phone_number__icontains=query) |
            Q(massage__name__icontains=query)
        )

    # Apply sorting if provided
    if sort_param:
        sessions = sessions.order_by(sort_param)
    else:
        # Default sort order (e.g., newest first)
        sessions = sessions.order_by('-created_at')

    # Pagination if you're using it
    sessions = paginate_page(request, sessions)

    context = {
        'sessions': sessions,
        'query': query,
        'sort': sort_param,
    }

    return render(request, 'reception/main_screen.html', context)


def not_paid_list_view(request):

    sessions = SessionBookingModel.objects.filter(is_paid=False)
    sessions = paginate_page(request, sessions)

    context = {'sessions': sessions}
    return render(request, 'reception/main_screen.html', context)


def get_booking_queryset(query=None, stage=None):
    queryset = []
    queries = query.split(" ")

    for q in queries:
        if stage:
            sessions = (SessionBookingModel.objects.filter(
                Q(series__icontains=q) |
                Q(patient__f_name__icontains=q) |
                Q(patient__mid_name__icontains=q) |
                Q(patient__mobile_phone_number__icontains=q)
            ).distinct())
        else:
            sessions = (SessionBookingModel.objects.filter(
                Q(series__icontains=q) |
                Q(patient__f_name__icontains=q) |
                Q(patient__mid_name__icontains=q) |
                Q(patient__mobile_phone_number__icontains=q)
            ).distinct())
        for new in sessions:
            queryset.append(new)

    return list(set(queryset))