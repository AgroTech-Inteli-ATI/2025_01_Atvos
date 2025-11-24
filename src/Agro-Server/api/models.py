from django.db import models

class Viagem(models.Model):
    veiculo_id = models.CharField(max_length=255)
    odometro_inicio = models.IntegerField()
    odometro_fim = models.IntegerField()
    ts_inicio = models.DateTimeField()
    ts_fim = models.DateTimeField()
    gps_path = models.CharField(max_length=255, blank=True, null=True)
    custos_fixos = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    custos_variaveis = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Viagem {self.id} - Veículo {self.veiculo_id}"
