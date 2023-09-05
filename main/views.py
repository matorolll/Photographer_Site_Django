from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from .forms import SignupForm
def index(request):
    return render(request, 'main/base.html', {})

def home(request):
    return render(request, 'main/home.html', {})

def portfolio(request):
    return render(request, 'main/portfolio.html', {})

def pricing(request):
    return render(request, 'main/pricing.html', {})


def weddingSession(request):
    return render(request, 'main/session/wedding.html', {})
def newbornSession(request):
    return render(request, 'main/session/newborn.html', {})
def familySession(request):
    return render(request, 'main/session/family.html', {})

def profile(request):
    return render(request, 'main/profile.html', {})


def sign_up(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else:
        form = SignupForm()

    return render(request, 'registration/sign_up.html', {'form':form})


def log_out(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/home')
    
    return render(request, 'registration/logout.html', {})

@user_passes_test(lambda user: user.is_superuser)
def control_panel(request):
    return render(request, 'main/control_panel.html', {})