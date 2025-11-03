from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("vehicles/", views.vehicle_list, name="vehicle_list"),
    path("telemetry/", views.telemetry_list, name="telemetry_list"),
]
