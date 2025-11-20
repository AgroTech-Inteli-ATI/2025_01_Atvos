from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .serializers_bigquery import (
    TravelListSerializer,
    TravelDetailSerializer,
    TravelCreateUpdateSerializer,
    StopSerializer,
    BillSerializer,
    BillDetailSerializer
)
from .bigquery_manager import BigQueryManager
import uuid
from datetime import datetime, timedelta
import traceback


class TravelViewSet(viewsets.ViewSet):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bq = BigQueryManager()
    
    def list(self, request):
        """Lista viagens com filtros e paginação"""
        try:
            search = request.query_params.get('search', '')
            unit_id = request.query_params.get('unit_id', '')
            start_date = request.query_params.get('start_date', '')
            end_date = request.query_params.get('end_date', '')
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 20))
            
            if not start_date:
                start_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.utcnow().strftime('%Y-%m-%d')

            sql = f"""
            WITH stop_stats AS (
                SELECT 
                    travel_id,
                    COUNT(*) as total_stops,
                    ARRAY_AGG(driver ORDER BY departure_datetime LIMIT 1)[SAFE_OFFSET(0)] as primary_driver
                FROM `{self.bq.get_table_id('stop')}`
                GROUP BY travel_id
            )
            SELECT 
                t.*,
                v.plate as license_plate,
                COALESCE(ss.total_stops, 0) as total_stops,
                ss.primary_driver
            FROM `{self.bq.get_table_id('travel')}` t
            LEFT JOIN `{self.bq.get_table_id('vehicle')}` v ON t.vehicle_id = v.id
            LEFT JOIN stop_stats ss ON ss.travel_id = t.id
            WHERE 1=1
            """

            if search:
                search_safe = search.replace("'", "''")
                sql += f" AND (v.plate LIKE '%{search_safe}%' OR t.asset_description LIKE '%{search_safe}%')"
            
            if unit_id:
                try:
                    unit_id_int = int(unit_id)
                    sql += f" AND t.unit_id = {unit_id_int}"
                except ValueError:
                    return Response({
                        'success': False,
                        'error': {'code': 'INVALID_UNIT_ID', 'message': 'unit_id deve ser numérico'},
                        'timestamp': timezone.now().isoformat()
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if start_date:
                sql += f" AND t.datetime >= '{start_date}'"
            
            if end_date:
                sql += f" AND t.datetime <= '{end_date}'"
            
            offset = (page - 1) * limit
            sql += f" ORDER BY t.datetime DESC LIMIT {limit} OFFSET {offset}"
            
            results = self.bq.query(sql)
            
            count_sql = f"""
            SELECT COUNT(*) as total 
            FROM `{self.bq.get_table_id('travel')}` t
            WHERE 1=1
            """
            
            if search:
                search_safe = search.replace("'", "''")
                count_sql = f"""
                SELECT COUNT(*) as total 
                FROM `{self.bq.get_table_id('travel')}` t
                LEFT JOIN `{self.bq.get_table_id('vehicle')}` v ON t.vehicle_id = v.id
                WHERE (v.plate LIKE '%{search_safe}%' OR t.asset_description LIKE '%{search_safe}%')
                """
            
            if unit_id:
                count_sql += f" AND t.unit_id = {int(unit_id)}"
            
            if start_date:
                count_sql += f" AND t.datetime >= '{start_date}'"
            
            if end_date:
                count_sql += f" AND t.datetime <= '{end_date}'"
            
            count_result = self.bq.query(count_sql)
            total = count_result[0]['total'] if count_result else 0

            serializer = TravelListSerializer(results, many=True)
            
            return Response({
                'success': True,
                'data': serializer.data,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'totalPages': (total + limit - 1) // limit
                },
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            traceback.print_exc()
            return Response({
                'success': False,
                'error': {
                    'code': 'QUERY_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """Retorna detalhes de uma viagem específica"""
        try:
            date_filter = (datetime.utcnow() - timedelta(days=1095)).strftime('%Y-%m-%d')
            
            sql = f"""
            WITH stop_count AS (
                SELECT travel_id, COUNT(*) as stops_count
                FROM `{self.bq.get_table_id('stop')}`
                WHERE travel_id = '{pk}'
                GROUP BY travel_id
            )
            SELECT 
                t.*,
                v.plate as license_plate,
                COALESCE(sc.stops_count, 0) as stops_count,
                b.fix_cost,
                b.variable_km,
                (b.fix_cost + (b.variable_km * t.full_distance)) as total_cost,
                b.datetime as bill_datetime
            FROM `{self.bq.get_table_id('travel')}` t
            LEFT JOIN `{self.bq.get_table_id('vehicle')}` v ON t.vehicle_id = v.id
            LEFT JOIN `{self.bq.get_table_id('bill')}` b ON b.travel_id = t.id
            LEFT JOIN stop_count sc ON sc.travel_id = t.id
            WHERE t.id = '{pk}'
            AND t.datetime >= '{date_filter}'
            """
            
            results = self.bq.query(sql)
            
            if not results:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'TRAVEL_NOT_FOUND',
                        'message': f'Viagem com ID {pk} não encontrada'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_404_NOT_FOUND)
            
            travel_data = results[0]
            
            if travel_data.get('fix_cost'):
                travel_data['bill'] = {
                    'fix_cost': float(travel_data['fix_cost']),
                    'variable_km': float(travel_data['variable_km']),
                    'total_cost': round(float(travel_data['total_cost']), 2),
                    'datetime': travel_data['bill_datetime']
                }
            else:
                travel_data['bill'] = None
            
            travel_data.pop('fix_cost', None)
            travel_data.pop('variable_km', None)
            travel_data.pop('bill_datetime', None)
            
            serializer = TravelDetailSerializer(travel_data)
            
            return Response({
                'success': True,
                'data': serializer.data,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            traceback.print_exc()
            return Response({
                'success': False,
                'error': {
                    'code': 'QUERY_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def create(self, request):
        """Cria uma nova viagem"""
        try:
            serializer = TravelCreateUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': serializer.errors
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            data = serializer.validated_data.copy()
            
            travel_id = str(uuid.uuid4())
            data['id'] = travel_id
            
            license_plate = data.pop('license_plate', None)
            if license_plate:
                vehicle_id = self._get_or_create_vehicle(license_plate, data.get('asset_id', 0))
                data['vehicle_id'] = vehicle_id
            
            now = datetime.utcnow().isoformat()
            data['created_at'] = now
            data['updated_at'] = now

            if isinstance(data.get('datetime'), datetime):
                data['datetime'] = data['datetime'].isoformat()
            
            if 'full_distance' in data:
                data['full_distance'] = float(data['full_distance'])
            
            success = self.bq.insert_rows('travel', [data])
            
            if success:
                dt_value = data.get('datetime')
                if isinstance(dt_value, datetime):
                    dt_value = dt_value.isoformat()

                return Response({
                    'success': True,
                    'data': {
                        'id': travel_id,
                        'asset_description': data.get('asset_description'),
                        'register_number': data.get('register_number'),
                        'license_plate': license_plate,
                        'datetime': dt_value  
                    },
                    'message': 'Viagem criada com sucesso',
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_201_CREATED)

            else:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INSERT_ERROR',
                        'message': 'Erro ao criar viagem'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            traceback.print_exc()
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
    

    
    def destroy(self, request, pk=None):
        """Remove uma viagem"""
        try:
            date_filter = (datetime.utcnow() - timedelta(days=1095)).strftime('%Y-%m-%d')
            
            check_sql = f"""
            SELECT id, TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), created_at, MINUTE) as age_minutes
            FROM `{self.bq.get_table_id('travel')}` 
            WHERE id = '{pk}' 
            AND datetime >= '{date_filter}'
            """
            existing = self.bq.query(check_sql)
            
            if not existing:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'TRAVEL_NOT_FOUND',
                        'message': f'Viagem com ID {pk} não encontrada'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_404_NOT_FOUND)
            
            age_minutes = existing[0].get('age_minutes', 0)
            if age_minutes < 90:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'STREAMING_BUFFER_ERROR',
                        'message': f'Não é possível deletar viagens recém-criadas. Aguarde {90 - age_minutes} minutos.',
                        'details': 'BigQuery não permite DELETE em dados no streaming buffer (< 90 min)'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_409_CONFLICT)
            
            self.bq.delete_rows('stop', f"travel_id = '{pk}'")
            self.bq.delete_rows('bill', f"travel_id = '{pk}'")
            
            success = self.bq.delete_rows(
                'travel', 
                f"id = '{pk}' AND datetime >= '{date_filter}'"
            )
            
            if success:
                return Response({
                    'success': True,
                    'message': 'Viagem removida com sucesso',
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'DELETE_ERROR',
                        'message': 'Erro ao deletar viagem'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            traceback.print_exc()
            return Response({
                'success': False,
                'error': {
                    'code': 'DELETE_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='stops')
    def stops(self, request, pk=None):
        """Lista paradas de uma viagem"""
        try:
            sql = f"""
            SELECT * FROM `{self.bq.get_table_id('stop')}`
            WHERE travel_id = '{pk}'
            ORDER BY departure_datetime
            """
            
            results = self.bq.query(sql)
            
            serializer = StopSerializer(results, many=True)
            
            return Response({
                'success': True,
                'data': serializer.data,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            traceback.print_exc()
            return Response({
                'success': False,
                'error': {
                    'code': 'QUERY_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_or_create_vehicle(self, plate: str, asset_id: int) -> str:
        """Busca ou cria veículo"""
        plate_clean = plate.replace('-', '').replace(' ', '').upper()[:6]
        
        sql = f"SELECT id FROM `{self.bq.get_table_id('vehicle')}` WHERE plate = '{plate_clean}'"
        results = self.bq.query(sql)
        
        if results:
            return results[0]['id']
        
        vehicle_id = str(uuid.uuid4())
        vehicle_data = {
            'id': vehicle_id,
            'plate': plate_clean,
            'identifier': asset_id,
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.bq.insert_rows('vehicle', [vehicle_data])
        return vehicle_id


class BillViewSet(viewsets.ViewSet):
    """ViewSet para operações de Bill"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bq = BigQueryManager()
    
    def list(self, request):
        """Lista custos"""
        try:
            travel_id = request.query_params.get('travel_id', '')
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 20))
            
            date_filter = (datetime.utcnow() - timedelta(days=1095)).strftime('%Y-%m-%d')
            
            sql = f"""
            SELECT 
                b.*,
                t.full_distance,
                v.plate as license_plate,
                (b.fix_cost + (b.variable_km * t.full_distance)) as total_cost
            FROM `{self.bq.get_table_id('bill')}` b
            JOIN `{self.bq.get_table_id('travel')}` t ON b.travel_id = t.id
            LEFT JOIN `{self.bq.get_table_id('vehicle')}` v ON t.vehicle_id = v.id
            WHERE t.datetime >= '{date_filter}'
            """
            
            if travel_id:
                sql += f" AND b.travel_id = '{travel_id}'"
            
            offset = (page - 1) * limit
            sql += f" ORDER BY b.datetime DESC LIMIT {limit} OFFSET {offset}"
            
            results = self.bq.query(sql)
            
            for result in results:
                result['total_cost'] = round(float(result['total_cost']), 2)
                result['travel_info'] = {
                    'license_plate': result.pop('license_plate'),
                    'full_distance': float(result.pop('full_distance'))
                }
            
            serializer = BillDetailSerializer(results, many=True)
            
            return Response({
                'success': True,
                'data': serializer.data,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            traceback.print_exc()
            return Response({
                'success': False,
                'error': {
                    'code': 'QUERY_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """Cria novo custo"""
        try:
            serializer = BillSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': serializer.errors
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            data = serializer.validated_data
            
            travel_id = data.get('travel_id') 
            
            date_filter = (datetime.utcnow() - timedelta(days=1095)).strftime('%Y-%m-%d')
            check_sql = f"""
            SELECT id, full_distance 
            FROM `{self.bq.get_table_id('travel')}` 
            WHERE id = '{travel_id}' 
            AND datetime >= '{date_filter}'
            """
            travel = self.bq.query(check_sql)
            
            if not travel:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'TRAVEL_NOT_FOUND',
                        'message': f'Viagem com ID {travel_id} não encontrada'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_404_NOT_FOUND)
            
            bill_id = str(uuid.uuid4())
            
            dt = data.get('datetime')
            if isinstance(dt, datetime):
                dt = dt.isoformat()

            bill_data = {
                'id': bill_id,
                'travel_id': travel_id,
                'fix_cost': float(data.get('fix_cost', 0)),
                'variable_km': float(data.get('variable_km', 0)),
                'datetime': dt,
            }
            
            success = self.bq.insert_rows('bill', [bill_data])
            
            if success:
                full_distance = float(travel[0]['full_distance'])
                total_cost = bill_data['fix_cost'] + (bill_data['variable_km'] * full_distance)
                
                return Response({
                    'success': True,
                    'data': {
                        'travel_id': travel_id,
                        'fix_cost': bill_data['fix_cost'],
                        'variable_km': bill_data['variable_km'],
                        'total_cost': round(total_cost, 2),
                        'datetime': bill_data['datetime']
                    },
                    'message': 'Custo registrado com sucesso',
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INSERT_ERROR',
                        'message': 'Erro ao criar custo'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            traceback.print_exc()
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)