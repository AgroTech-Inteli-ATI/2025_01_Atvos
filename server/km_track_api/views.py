from django.shortcuts import render, HttpResponse
from .models import Vehicle

def home(request) -> HttpResponse:
  vehicles = Vehicle.objects.all()
  vehicle_list = ", ".join([v.type for v in vehicles])
  return HttpResponse(f"Hello, World! Vehicles: {vehicle_list}")