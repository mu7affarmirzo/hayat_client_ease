from http.client import HTTPResponse

from django.contrib.auth import authenticate, logout, login
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect

from core.adminstration.forms.auth import AccountAuthenticationForm
from core.models import PaymentModel, SessionModel


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

    sessions = SessionModel.objects.all()
    print(sessions)

    sessions = paginate_page(request, sessions)

    # target_role = AccountRolesModel.objects.filter(user=request.user)
    # target_role = target_role.first()
    # if target_role:
    #     target_role = target_role.role.name
    #
    # user_role_based_redirect = {
    #     'warehouse': 'warehouse_v2:main_screen',
    #     'sanatorium.staff': 'sanatorium_staff:main_screen',
    #     'sanatorium.nurse': 'sanatorium_nurse:main_screen',
    #     'sanatorium.admin': 'sanatorium_admin:main_screen',
    #     'sanatorium.doctor': 'sanatorium_doctors:main_screen',
    # }
    #
    # if target_role in user_role_based_redirect:
    #     print(user_role_based_redirect[target_role])
    #     return redirect(user_role_based_redirect[target_role])
    # return redirect('sanatorium_auth:logout')
    context = {'sessions': sessions}
    return render(request, 'reception/main_screen.html', context)


def get_booking_queryset(query=None, stage=None):
    queryset = []
    queries = query.split(" ")

    for q in queries:
        if stage:
            sessions = (SessionModel.objects.filter(
                Q(series__icontains=q) |
                Q(patient__f_name__icontains=q) |
                Q(patient__mid_name__icontains=q) |
                Q(patient__mobile_phone_number__icontains=q)
            ).distinct())
        else:
            sessions = (SessionModel.objects.filter(
                Q(series__icontains=q) |
                Q(patient__f_name__icontains=q) |
                Q(patient__mid_name__icontains=q) |
                Q(patient__mobile_phone_number__icontains=q)
            ).distinct())
        for new in sessions:
            queryset.append(new)

    return list(set(queryset))