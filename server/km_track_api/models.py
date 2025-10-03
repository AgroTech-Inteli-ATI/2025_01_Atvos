from django.db import models

class Vehicle(models.Model):
    plate = models.CharField(max_length=6, unique=True)
    identifier = models.IntegerField(unique=True)
    bus_type = models.CharField(max_length=50, null=True, blank=True, help_text="Type of bus (Ativo/Reserva)")

    def __str__(self):
        return str(self.identifier)


class TelemetryRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="records")
    driver = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField()

    # departure_place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, related_name="departures")
    departure_km = models.FloatField()
    departure_time = models.DateTimeField()
    # arrival_place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, related_name="arrivals")
    arrival_km = models.FloatField()
    arrival_time = models.DateTimeField()
    total_time = models.DurationField()
    total_km_traveled = models.FloatField()
    max_speed_reached = models.FloatField()
    people_transported = models.IntegerField()
    occupancy_rate = models.FloatField(null=True, blank=True, help_text="Occupancy rate (percentage)")
    duration = models.DurationField()
    idle_time = models.DurationField()

    SHIFT_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('night', 'Night'),
    ]
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle} - {self.date.date()} - {self.total_km_traveled} km"

class Operation(models.Model):
    telemetry_record = models.ForeignKey(TelemetryRecord, on_delete=models.CASCADE, related_name="operations")
    unity = models.CharField(max_length=3) # UAT, UCR, UMV, UAE, URC, UAL, UCP, UEL, USL
    area = models.TextField(max_length=2)
    operation_type = models.TextField(max_length=20)
    shifts_accounted = models.IntegerField()
    fix_cost = models.FloatField()
    variable_cost = models.FloatField()
    average_monthly_km = models.FloatField()
    monthly_cost = models.FloatField()
    cost_per_safra = models.FloatField(help_text="monthly_cost * 12")
    average_occupancy = models.FloatField(help_text="Average occupancy rate (percentage)")
    observations = models.TextField(blank=True, null=True)