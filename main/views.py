from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from .forms import SignupForm
from .forms import SessionForm
from .models import Session
from .forms import PrivateSessionForm
from .forms import PhotoForm


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
    return render(request, 'main/control_panel/control_panel.html', {})

@user_passes_test(lambda user: user.is_superuser)
def create_session(request):
    if request.method == 'POST':
        name = request.POST['name']
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save()
            return redirect('view_session', name=name)

    else:
        form = SessionForm()
    return render(request, 'main/control_panel/create_session.html', {'form': form})




@user_passes_test(lambda user: user.is_superuser)
def delete_sessions(request):
    sessions = Session.objects.all()
    return render(request, 'main/control_panel/delete_sessions.html', {'sessions': sessions})

@user_passes_test(lambda user: user.is_superuser)
def delete_session(request,name):
    session = Session.objects.filter(name=name).delete()
    return render(request, 'main/session/session_template.html', {'session': session})


@user_passes_test(lambda user: user.is_superuser)
def view_sessions(request):
    sessions = Session.objects.all()
    return render(request, 'main/control_panel/view_sessions.html', {'sessions': sessions})


def view_session(request, name):
    session = get_object_or_404(Session, name=name)
    if request.user.is_superuser:
        return render(request, 'main/session/private_session.html', {'session': session})

    if request.method == 'POST':
        form = PrivateSessionForm(request.POST)
        if form.is_valid():
            entered_password = form.cleaned_data['password']
            if entered_password == session.password:
                return render(request, 'main/session/private_session.html', {'session': session})
    
    else:
        form = PrivateSessionForm()
    
    return render(request, 'main/session/private_session_form.html', {'form': form})


def add_picture(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/main/add_picture.html')
    else:
        form = PhotoForm()
    return render(request, 'main/add_picture.html', {'form': form})