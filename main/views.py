from django.shortcuts import render
from django.http import HttpResponse

def index(response):
    return render(response, "main/base.html", {})

def home(response):
    return render(response, "main/home.html", {})