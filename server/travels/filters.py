import django_filters
from django.db.models import Q
from .models import Travel, Bill


class TravelFilter(django_filters.FilterSet):
    """
    Filtro customizado para viagens com suporte a:
    - Busca por texto (motorista, placa)
    - Filtro por unidade
    - Filtro por período
    """
    search = django_filters.CharFilter(method='filter_search')
    unit_id = django_filters.NumberFilter(field_name='unit_id')
    start_date = django_filters.DateTimeFilter(
        field_name='datetime',
        lookup_expr='gte'
    )
    end_date = django_filters.DateTimeFilter(
        field_name='datetime',
        lookup_expr='lte'
    )

    class Meta:
        model = Travel
        fields = ['unit_id', 'start_date', 'end_date']

    def filter_search(self, queryset, name, value):
        """
        Busca em múltiplos campos:
        - Placa do veículo (através do relacionamento vehicle)
        - Nome do motorista (nas paradas)
        - Descrição do ativo
        - Número de registro
        - Nome da garagem
        """
        
        if not value:
            print("⚠️  Valor vazio, retornando queryset original")
            return queryset
        
        q_objects = Q()
        
        q_objects |= Q(vehicle__plate__icontains=value)
        
        q_objects |= Q(stops__driver__icontains=value)
        
        q_objects |= Q(asset_description__icontains=value)
        
        q_objects |= Q(register_number__icontains=value)
        
        q_objects |= Q(garage_name__icontains=value)
        
        filtered = queryset.filter(q_objects).distinct()
        
        return filtered


class BillFilter(django_filters.FilterSet):
    """
    Filtro para custos.
    """
    travel_id = django_filters.NumberFilter(field_name='travel_id')
    
    class Meta:
        model = Bill
        fields = ['travel_id']