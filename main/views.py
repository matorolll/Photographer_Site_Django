from django.shortcuts import render
from django.http import HttpResponse

def index(response):
    return HttpResponse("aa")

def home(response):
    return HttpResponse("home")