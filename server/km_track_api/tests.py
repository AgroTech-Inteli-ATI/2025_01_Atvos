from django.test import TestCase
from .models import Vehicle

class VehicleModelTest(TestCase):
    def test_create_vehicle(self):
        v = Vehicle.objects.create(identifier="Truck 01")
        self.assertEqual(str(v), "Truck 01")
