from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("portfolio/", views.portfolio, name="portfolio"),

    path("session/wedding", views.weddingSession, name="weddingSession"),
    path("session/newborn", views.newbornSession, name="newbornSession"),
    path("session/family", views.familySession, name="familySession"),


    #path("sessions/", views.sessions, name="sessions"),


    path("pricing/", views.pricing, name="pricing"),
    path("profile/", views.profile, name="profile"),


    path("sign_up/", views.sign_up, name="sign_up"),
    path("logout/", views.log_out, name="logout"),


    path("control_panel/", views.control_panel, name="control_panel"),
    path("control_panel/create_session/", views.create_session, name="create_session"),


    path('', include("django.contrib.auth.urls")),
]