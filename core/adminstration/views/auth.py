from django.contrib.auth import authenticate, logout, login
from django.shortcuts import render, redirect

from core.adminstration.forms.auth import AccountAuthenticationForm


def login_view(request):
    context = {}
    user = request.user

    if user.is_authenticated:
        return redirect("sanatorium_auth:main_screen")

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():

            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                return redirect("sanatorium_auth:main_screen")

    form = AccountAuthenticationForm()

    context['login_form'] = form
    return render(request, 'reception/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')