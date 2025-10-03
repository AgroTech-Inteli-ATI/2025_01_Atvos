from django.contrib import admin
from .models import Vehicle, TelemetryRecord

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("id", "identifier")

@admin.register(TelemetryRecord)
class TelemetryRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "driver", "date", "distance", "duration", "idle_time")
    list_filter = ("vehicle", "driver")
    search_fields = ("vehicle__identifier", "driver")
