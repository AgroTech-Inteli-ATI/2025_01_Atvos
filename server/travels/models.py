from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from km_track_api.models import Vehicle 


class Travel(models.Model):
    """
    Modelo que representa uma viagem completa de um veículo.
    """

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name='travels',
        verbose_name='Veículo',
        null=True,
        blank=True
    )
    
    asset_description = models.CharField(
        max_length=255,
        verbose_name='Descrição do Ativo',
        help_text='Descrição completa do veículo'
    )
    register_number = models.CharField(
        max_length=50,
        verbose_name='Número de Registro',
        help_text='Número de registro do ativo'
    )
    asset_id = models.IntegerField(
        verbose_name='ID do Ativo',
        help_text='Identificação interna do ativo'
    )
    garage_name = models.CharField(
        max_length=100,
        verbose_name='Nome da Garagem',
        help_text='Garagem de origem do veículo'
    )
    full_distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Distância Total (km)',
        help_text='Distância total percorrida na viagem'
    )
    datetime = models.DateTimeField(
        verbose_name='Data/Hora da Viagem',
        help_text='Data e hora de registro da viagem'
    )
    
    unit_id = models.IntegerField(
        verbose_name='ID da Unidade',
        help_text='Referência para a unidade operacional',
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'travel'
        ordering = ['-datetime']
        verbose_name = 'Viagem'
        verbose_name_plural = 'Viagens'
        indexes = [
            models.Index(fields=['-datetime']),
            models.Index(fields=['unit_id']),
        ]

    def __str__(self):
        plate = self.license_plate or "SEM PLACA"
        return f"Viagem {self.id} - {plate} ({self.datetime.strftime('%d/%m/%Y')})"

    @property
    def license_plate(self):
        """Retorna a placa do veículo associado"""
        return self.vehicle.plate if self.vehicle else None

    def clean(self):
        """Validações customizadas"""
        if self.datetime and self.datetime > timezone.now():
            raise ValidationError({
                'datetime': 'A data da viagem não pode ser no futuro.'
            })
        
        if self.full_distance and self.full_distance < 0:
            raise ValidationError({
                'full_distance': 'A distância não pode ser negativa.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Stop(models.Model):
    """
    Modelo que representa uma parada durante uma viagem.
    """
    travel = models.ForeignKey(
        Travel,
        on_delete=models.CASCADE,
        related_name='stops',
        verbose_name='Viagem'
    )
    departure_datetime = models.DateTimeField(
        verbose_name='Data/Hora de Saída'
    )
    driver = models.CharField(
        max_length=255,
        verbose_name='Motorista',
        help_text='Nome completo do motorista'
    )
    departure_site = models.TextField(
        verbose_name='Local de Saída',
        help_text='Endereço completo de partida'
    )
    trip_time = models.TimeField(
        verbose_name='Tempo de Viagem',
        help_text='Duração da condução (HH:MM:SS)'
    )
    trip_distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Distância da Parada (km)'
    )
    arrival_datetime = models.DateTimeField(
        verbose_name='Data/Hora de Chegada'
    )
    arrival_site = models.TextField(
        verbose_name='Local de Chegada',
        help_text='Endereço completo de destino'
    )
    
    class Meta:
        db_table = 'stop'
        ordering = ['departure_datetime']
        verbose_name = 'Parada'
        verbose_name_plural = 'Paradas'
        indexes = [
            models.Index(fields=['travel', 'departure_datetime']),
        ]

    def __str__(self):
        return f"Parada {self.id} - {self.driver} ({self.departure_datetime.strftime('%d/%m/%Y %H:%M')})"

    def clean(self):
        """Validações customizadas"""
        if self.arrival_datetime and self.departure_datetime:
            if self.arrival_datetime < self.departure_datetime:
                raise ValidationError({
                    'arrival_datetime': 'A data de chegada deve ser posterior à data de saída.'
                })
        
        if self.trip_distance and self.trip_distance < 0:
            raise ValidationError({
                'trip_distance': 'A distância não pode ser negativa.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Bill(models.Model):
    """
    Modelo que representa os custos associados a uma viagem.
    """
    travel = models.OneToOneField(
        Travel,
        on_delete=models.CASCADE,
        related_name='bill',
        verbose_name='Viagem'
    )
    fix_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Custo Fixo',
        help_text='Custo fixo da viagem'
    )
    variable_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Custo Variável por KM',
        help_text='Custo por quilômetro rodado'
    )
    datetime = models.DateTimeField(
        verbose_name='Data/Hora de Geração',
        help_text='Data de geração da medição de custos'
    )
    
    class Meta:
        db_table = 'bill'
        ordering = ['-datetime']
        verbose_name = 'Custo'
        verbose_name_plural = 'Custos'

    def __str__(self):
        return f"Custo - Viagem {self.travel_id} (R$ {self.total_cost:.2f})"

    @property
    def total_cost(self):
        """Calcula o custo total (fixo + variável × distância)"""
        if self.travel and self.travel.full_distance:
            return float(self.fix_cost) + (float(self.variable_km) * float(self.travel.full_distance))
        return float(self.fix_cost)

    def clean(self):
        """Validações customizadas"""
        if self.fix_cost and self.fix_cost < 0:
            raise ValidationError({
                'fix_cost': 'O custo fixo não pode ser negativo.'
            })
        
        if self.variable_km and self.variable_km < 0:
            raise ValidationError({
                'variable_km': 'O custo variável não pode ser negativo.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)