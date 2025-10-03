from django.shortcuts import render, HttpResponse
from .models import Vehicle, TelemetryRecord

def home(request):
    vehicles = Vehicle.objects.all()
    if vehicles.exists():
        vehicle_list = ", ".join([v.identifier for v in vehicles])
        return HttpResponse(f"Hello, World! Vehicles: {vehicle_list}")
    else:
        return HttpResponse("Nenhum veículo encontrado.")

def vehicle_list(request) -> HttpResponse:
    vehicles = Vehicle.objects.all()
    html = "<br>".join([f"{v.id} - {v.identifier}" for v in vehicles])
    return HttpResponse(html)

def telemetry_list(request) -> HttpResponse:
    records = TelemetryRecord.objects.select_related("vehicle").all()[:50]
    html = "<br>".join([
        f"{r.vehicle.identifier} - {r.date} - {r.distance} km - {r.duration} running - {r.idle_time} idle"
        for r in records
    ])
    return HttpResponse(html)
