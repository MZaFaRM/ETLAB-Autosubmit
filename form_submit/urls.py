from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.survey_view, name="login"),
    path("etlab-status/", views.etlab_status, name="etlab-status"),
    path("progress/", views.progress, name="progress"),
]
