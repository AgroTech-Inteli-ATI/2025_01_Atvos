from django.core.management.base import BaseCommand
from km_track_api.services import ingest_csv

class Command(BaseCommand):
    help = "Ingest telemetry data from CSV"

    def add_arguments(self, parser):
        parser.add_argument("filepath", type=str, help="Path to the telemetry CSV")

    def handle(self, *args, **kwargs):
        filepath = kwargs["filepath"]
        ingest_csv(filepath)
        self.stdout.write(self.style.SUCCESS(f"CSV {filepath} ingerido com sucesso!"))
