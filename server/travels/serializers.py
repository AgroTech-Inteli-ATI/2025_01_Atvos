from rest_framework import serializers
from django.utils import timezone
from .models import Travel, Stop, Bill
from km_track_api.models import Vehicle


class TravelCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação e atualização de viagens
    """
    license_plate = serializers.CharField(
        max_length=20,
        write_only=True,
        required=False,
        help_text="Placa do veículo"
    )
    
    class Meta:
        model = Travel
        fields = [
            'asset_description',
            'register_number',
            'asset_id',
            'garage_name',
            'full_distance',
            'datetime',
            'license_plate',  
            'unit_id',
            'vehicle' 
        ]
        extra_kwargs = {
            'vehicle': {'required': False}
        }

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

    def create(self, validated_data):
        license_plate = validated_data.pop('license_plate', None)
        
        if license_plate and not validated_data.get('vehicle'):
            plate_clean = license_plate.replace('-', '').replace(' ', '')[:6]
            vehicle, created = Vehicle.objects.update_or_create(
                plate=plate_clean,
                defaults={
                    'identifier': validated_data.get('asset_id', 0)
                }
            )
            validated_data['vehicle'] = vehicle
        
        return super().create(validated_data)


    def update(self, instance, validated_data):
        """Atualiza Travel e Vehicle se necessário"""
        license_plate = validated_data.pop('license_plate', None)
        
        if license_plate:
            plate_clean = license_plate.replace('-', '').replace(' ', '')[:6]
            vehicle, created = Vehicle.objects.update_or_create(
                plate=plate_clean,
                defaults={
                    'identifier': validated_data.get('asset_id', instance.asset_id)
                }
            )
            validated_data['vehicle'] = vehicle
        
        return super().update(instance, validated_data)


class TravelListSerializer(serializers.ModelSerializer):
    """
    Serializer leve para listagem de viagens.
    """
    unit_name = serializers.SerializerMethodField()
    total_stops = serializers.SerializerMethodField()
    primary_driver = serializers.SerializerMethodField()
    license_plate = serializers.CharField() 
    
    class Meta:
        model = Travel
        fields = [
            'id',
            'license_plate',
            'asset_description',
            'register_number',
            'garage_name',
            'full_distance',
            'datetime',
            'unit_name',
            'total_stops',
            'primary_driver'
        ]

    def get_unit_name(self, obj):
        """Retorna o nome da unidade"""
        # Tabela unit não existe ainda, retornando None
        # Implementar quando a tabela unit for criada
        return None

    def get_total_stops(self, obj):
        """Retorna o número total de paradas"""
        return obj.stops.count()

    def get_primary_driver(self, obj):
        """Retorna o motorista da primeira parada"""
        first_stop = obj.stops.order_by('departure_datetime').first()
        return first_stop.driver if first_stop else None


class TravelDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para detalhes de uma viagem.
    """
    unit_name = serializers.SerializerMethodField()
    stops_count = serializers.SerializerMethodField()
    bill = serializers.SerializerMethodField()
    license_plate = serializers.CharField()  
    
    class Meta:
        model = Travel
        fields = [
            'id',
            'license_plate',
            'asset_description',
            'register_number',
            'asset_id',
            'garage_name',
            'full_distance',
            'datetime',
            'unit_name',
            'unit_id',
            'stops_count',
            'bill'
        ]

    def get_unit_name(self, obj):
        """Retorna o nome da unidade"""
        # Tabela unit não existe ainda, retornando None
        # Implementar quando a tabela unit for criada
        return None

    def get_stops_count(self, obj):
        """Retorna o número de paradas"""
        return obj.stops.count()

    def get_bill(self, obj):
        """Retorna os dados de custo se existir"""
        try:
            bill = obj.bill
            return {
                'fix_cost': float(bill.fix_cost),
                'variable_km': float(bill.variable_km),
                'total_cost': round(bill.total_cost, 2),
                'datetime': bill.datetime
            }
        except Bill.DoesNotExist:
            return None


class StopSerializer(serializers.ModelSerializer):
    """Serializer completo para o modelo Stop."""

    trip_time = serializers.DurationField(required=False, allow_null=True)
    
    class Meta:
        model = Stop
        fields = [
            'id',
            'departure_datetime',
            'driver',
            'departure_site',
            'trip_time',
            'trip_distance',
            'arrival_datetime',
            'arrival_site',
            'travel_id'
        ]
        read_only_fields = ['id']

    def get_duration(self, obj):
        if obj.duration:
            return obj.duration.total_seconds()
        return None

    def validate(self, data):
        """Validação customizada para garantir consistência de datas"""
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

class BillSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Bill com campo calculado total_cost."""
    total_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = Bill
        fields = [
            'travel',  
            'fix_cost',
            'variable_km',
            'total_cost',
            'datetime'
        ]
        read_only_fields = ['total_cost']

    def get_total_cost(self, obj):
        """Calcula o custo total"""
        return round(obj.total_cost, 2)
    
    def to_representation(self, instance):
        """Customize output to show travel_id instead of travel"""
        ret = super().to_representation(instance)
        if 'travel' in ret:
            ret['travel_id'] = ret.pop('travel')
        return ret

    def validate(self, data):
        """Validações customizadas"""
        if 'fix_cost' in data and data['fix_cost'] < 0:
            raise serializers.ValidationError({
                'fix_cost': 'O custo fixo não pode ser negativo.'
            })
        
        if 'variable_km' in data and data['variable_km'] < 0:
            raise serializers.ValidationError({
                'variable_km': 'O custo variável não pode ser negativo.'
            })
        
        return data

class BillDetailSerializer(BillSerializer):
    """Serializer detalhado de Bill com informações da viagem."""
    travel_info = serializers.SerializerMethodField()
    
    class Meta(BillSerializer.Meta):
        fields = BillSerializer.Meta.fields + ['travel_info']

    def get_travel_info(self, obj):
        """Retorna informações básicas da viagem"""
        return {
            'license_plate': obj.travel.license_plate,
            'full_distance': float(obj.travel.full_distance)
        }