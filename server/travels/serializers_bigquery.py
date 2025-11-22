from rest_framework import serializers
from django.utils import timezone
from datetime import datetime


class TravelListSerializer(serializers.Serializer):
    """
    Serializer para listagem de viagens (dados vindos do BigQuery)
    """
    id = serializers.CharField(read_only=True)
    license_plate = serializers.CharField(read_only=True, allow_null=True)
    asset_description = serializers.CharField(max_length=255)
    register_number = serializers.CharField(max_length=50)
    garage_name = serializers.CharField(max_length=100)
    full_distance = serializers.DecimalField(max_digits=10, decimal_places=2)
    datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")
    unit_id = serializers.IntegerField(allow_null=True, required=False)
    
    total_stops = serializers.IntegerField(read_only=True, default=0)
    primary_driver = serializers.CharField(read_only=True, allow_null=True, required=False)
    
    unit_name = serializers.SerializerMethodField()
    
    def get_unit_name(self, obj):
        """TODO: Implementar quando tabela unit existir"""
        return None


class TravelDetailSerializer(serializers.Serializer):
    """
    Serializer para detalhes completos de uma viagem
    """
    id = serializers.CharField(read_only=True)
    license_plate = serializers.CharField(read_only=True, allow_null=True)
    asset_description = serializers.CharField(max_length=255)
    register_number = serializers.CharField(max_length=50)
    asset_id = serializers.IntegerField()
    garage_name = serializers.CharField(max_length=100)
    full_distance = serializers.DecimalField(max_digits=10, decimal_places=2)
    datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")
    unit_id = serializers.IntegerField(allow_null=True, required=False)
    
    stops_count = serializers.IntegerField(read_only=True, default=0)
    bill = serializers.DictField(read_only=True, allow_null=True, required=False)
    unit_name = serializers.SerializerMethodField()
    
    def get_unit_name(self, obj):
        return None


class TravelCreateUpdateSerializer(serializers.Serializer):
    """
    Serializer para criar/atualizar viagens
    """
    license_plate = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        help_text="Placa do veículo"
    )
    asset_description = serializers.CharField(max_length=255)
    register_number = serializers.CharField(max_length=50)
    asset_id = serializers.IntegerField()
    garage_name = serializers.CharField(max_length=100)
    full_distance = serializers.DecimalField(max_digits=10, decimal_places=2)
    datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")
    unit_id = serializers.IntegerField(required=False, allow_null=True)
    vehicle_id = serializers.CharField(required=False, allow_null=True)
    
    def validate_datetime(self, value):
        """Valida se a data não é futura"""
        if value > timezone.now():
            raise serializers.ValidationError(
                'A data da viagem não pode ser no futuro.'
            )
        return value
    
    def validate_full_distance(self, value):
        """Valida se a distância é positiva"""
        if value < 0:
            raise serializers.ValidationError(
                'A distância deve ser um número positivo.'
            )
        return value
    
    def validate_unit_id(self, value):
        """Valida se o unit_id está no range válido"""
        if value and (value < 1 or value > 100):
            raise serializers.ValidationError(
                'ID de unidade inválido.'
            )
        return value


class StopSerializer(serializers.Serializer):
    """Serializer para paradas"""
    id = serializers.CharField(read_only=True)
    travel_id = serializers.CharField()
    departure_datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")
    driver = serializers.CharField(max_length=255)
    departure_site = serializers.CharField()
    trip_time = serializers.TimeField(required=False, allow_null=True)
    trip_distance = serializers.DecimalField(max_digits=10, decimal_places=2)
    arrival_datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")
    arrival_site = serializers.CharField()
    
    def validate(self, data):
        """Validação customizada"""
        if 'arrival_datetime' in data and 'departure_datetime' in data:
            if data['arrival_datetime'] < data['departure_datetime']:
                raise serializers.ValidationError({
                    'arrival_datetime': 'A data de chegada deve ser posterior à data de saída.'
                })
        
        if 'trip_distance' in data and data['trip_distance'] < 0:
            raise serializers.ValidationError({
                'trip_distance': 'A distância não pode ser negativa.'
            })
        
        return data


class BillSerializer(serializers.Serializer):
    """Serializer para custos"""
    id = serializers.CharField(read_only=True)
    travel_id = serializers.CharField(required=True, help_text="ID da viagem")
    fix_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    variable_km = serializers.DecimalField(max_digits=10, decimal_places=2)
    datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")
    total_cost = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        read_only=True,
        required=False
    )
    
    def validate_fix_cost(self, value):
        if value < 0:
            raise serializers.ValidationError('O custo fixo não pode ser negativo.')
        return value
    
    def validate_variable_km(self, value):
        if value < 0:
            raise serializers.ValidationError('O custo variável não pode ser negativo.')
        return value


class BillDetailSerializer(BillSerializer):
    """Serializer detalhado com informações da viagem"""
    travel_info = serializers.DictField(read_only=True, required=False)