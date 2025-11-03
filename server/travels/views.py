from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Travel, Stop, Bill
from .serializers import (
    TravelListSerializer,
    TravelDetailSerializer,
    TravelCreateUpdateSerializer,
    StopSerializer,
    BillSerializer,
    BillDetailSerializer
)
from .filters import TravelFilter, BillFilter
from .pagination import CustomPagination


class TravelViewSet(viewsets.ModelViewSet):

    queryset = Travel.objects.select_related('vehicle').all()
    pagination_class = CustomPagination
    filterset_class = TravelFilter
    search_fields = ['vehicle__plate', 'stops__driver', 'asset_description']
    ordering_fields = ['datetime', 'full_distance', 'vehicle__plate']
    ordering = ['-datetime']

    def get_serializer_class(self):
        """Retorna serializer apropriado baseado na action"""
        if self.action == 'list':
            return TravelListSerializer
        elif self.action == 'retrieve':
            return TravelDetailSerializer
        else:  
            return TravelCreateUpdateSerializer

    def list(self, request, *args, **kwargs):
        """Lista viagens com filtros e paginação"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.paginator.get_paginated_response(serializer.data)
            if isinstance(paginated_response, dict):
                paginated_response['timestamp'] = timezone.now().isoformat()
            return Response(paginated_response)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'timestamp': timezone.now().isoformat()
        })

    def retrieve(self, request, *args, **kwargs):
        """Retorna detalhes de uma viagem específica"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'success': True,
                'data': serializer.data,
                'timestamp': timezone.now().isoformat()
            })
        except Travel.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'TRAVEL_NOT_FOUND',
                    'message': f'Viagem com ID {kwargs.get("pk")} não encontrada'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        """Cria uma nova viagem"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            travel = serializer.save()
            return Response({
                'success': True,
                'data': {
                    'id': travel.id,
                    'asset_description': travel.asset_description,
                    'register_number': travel.register_number,
                    'license_plate': travel.license_plate,
                    'datetime': travel.datetime
                },
                'message': 'Viagem criada com sucesso',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Dados inválidos',
                'details': serializer.errors
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Atualiza uma viagem (PUT - completo)"""
        partial = kwargs.pop('partial', False)
        
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=partial
            )
            
            if serializer.is_valid():
                travel = serializer.save()
                return Response({
                    'success': True,
                    'data': {
                        'id': travel.id,
                        'garage_name': travel.garage_name,
                        'full_distance': float(travel.full_distance),
                        'license_plate': travel.license_plate,
                        'updated_at': travel.updated_at
                    },
                    'message': 'Viagem atualizada com sucesso',
                    'timestamp': timezone.now().isoformat()
                })
            
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Dados inválidos',
                    'details': serializer.errors
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Travel.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'TRAVEL_NOT_FOUND',
                    'message': f'Viagem com ID {kwargs.get("pk")} não encontrada'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        """Atualiza uma viagem (PATCH - parcial)"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Remove uma viagem"""
        try:
            instance = self.get_object()
            instance.delete()
            return Response({
                'success': True,
                'message': 'Viagem removida com sucesso',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
        except Travel.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'TRAVEL_NOT_FOUND',
                    'message': f'Viagem com ID {kwargs.get("pk")} não encontrada'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='stops')
    def stops(self, request, pk=None):
        """
        Endpoint customizado: GET /api/travels/{id}/stops/
        Lista todas as paradas de uma viagem específica
        """
        try:
            travel = self.get_object()
            stops = travel.stops.all()
            serializer = StopSerializer(stops, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'timestamp': timezone.now().isoformat()
            })
        except Travel.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'TRAVEL_NOT_FOUND',
                    'message': f'Viagem com ID {pk} não encontrada'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_404_NOT_FOUND)


class BillViewSet(viewsets.ModelViewSet):

    queryset = Bill.objects.select_related('travel').all()
    pagination_class = CustomPagination
    filterset_class = BillFilter
    ordering = ['-datetime']

    def get_serializer_class(self):
        """Retorna serializer apropriado baseado na action"""
        if self.action == 'list':
            return BillDetailSerializer
        return BillSerializer

    def list(self, request, *args, **kwargs):
        """Lista custos com filtros e paginação"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.paginator.get_paginated_response(serializer.data)
            if isinstance(paginated_response, dict):
                paginated_response['timestamp'] = timezone.now().isoformat()
            return Response(paginated_response)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'timestamp': timezone.now().isoformat()
        })

    def create(self, request, *args, **kwargs):
        """Cria um novo custo"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            travel_id = request.data.get('travel')
            if not Travel.objects.filter(id=travel_id).exists():
                return Response({
                    'success': False,
                    'error': {
                        'code': 'TRAVEL_NOT_FOUND',
                        'message': f'Viagem com ID {travel_id} não encontrada'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_404_NOT_FOUND)
            
            bill = serializer.save()
            
            return Response({
                'success': True,
                'data': {
                    'travel_id': bill.travel_id,
                    'fix_cost': float(bill.fix_cost),
                    'variable_km': float(bill.variable_km),
                    'total_cost': round(bill.total_cost, 2),
                    'datetime': bill.datetime
                },
                'message': 'Custo registrado com sucesso',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Dados inválidos',
                'details': serializer.errors
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_400_BAD_REQUEST)