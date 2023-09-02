from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignupForm

def signup_view(response):
    if response.method == "POST":
        form = SignupForm(response.POST)
        if form.is_valid():
            form.save()
        
        return redirect("/home")
    else:
        form = SignupForm()

    return render(response, "session/signup.html", {"form":form})


def login_view(response):
    if response.method == "POST":
        username = response.POST['username']
        password = response.POST['password']
        user = authenticate(response, username=username, password=password)
        if user is not None:
            login(response, user)
            return redirect("/home")
        else:
            #messages.success(response, ("There was an error login in, try again..."))
            return redirect("/login")

    return render(response, "session/login.html", {})

def logout_view(response):
    logout(response)
    return redirect('/home')