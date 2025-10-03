from django.db import models

class Vehicle(models.Model):
    identifier = models.CharField(max_length=100, default='---')  # placa, frota, etc.

    def __str__(self):
        return self.identifier


class TelemetryRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="records")
    driver = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField()

    odometer = models.FloatField()
    distance = models.FloatField()
    duration = models.DurationField()
    idle_time = models.DurationField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle} - {self.date.date()} - {self.distance} km"
