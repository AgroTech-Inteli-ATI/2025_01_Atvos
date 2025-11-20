from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
import traceback

from travels.bigquery_manager import BigQueryManager


@api_view(['GET'])
def travel_summary(request):
    """
    Retorna resumo geral de viagens e custos.
    """
    bq = BigQueryManager()
    
    try:
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        unit_id = request.query_params.get('unit_id')
   
        auto_calculated_dates = False
        
        if not start_date:
            start_dt = timezone.now() - timedelta(days=30)
            start_date_sql = start_dt.strftime('%Y-%m-%d %H:%M:%S')
            auto_calculated_dates = True
        else:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                start_date_sql = start_dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': 'Formato de data inválido para start_date. Use ISO 8601 (ex: 2024-01-01T00:00:00Z)'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if not end_date:
            end_dt = timezone.now()
            end_date_sql = end_dt.strftime('%Y-%m-%d %H:%M:%S')
            auto_calculated_dates = True
        else:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                end_date_sql = end_dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': 'Formato de data inválido para end_date. Use ISO 8601 (ex: 2024-12-31T23:59:59Z)'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
        
        unit_id_int = None
        if unit_id:
            try:
                unit_id_int = int(unit_id)
                if unit_id_int < 1:
                    raise ValueError
            except ValueError:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_UNIT_ID',
                        'message': 'ID de unidade inválido. Deve ser um número inteiro positivo.'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
        
        sql = f"""
        WITH travel_data AS (
            SELECT 
                t.id,
                t.full_distance,
                t.datetime,
                t.unit_id
            FROM `{bq.get_table_id('travel')}` t
            WHERE t.datetime >= TIMESTAMP('{start_date_sql}')
              AND t.datetime <= TIMESTAMP('{end_date_sql}')
        """
        
        if unit_id_int:
            sql += f" AND t.unit_id = {unit_id_int}"
        
        sql += f"""
        ),
        bill_data AS (
            SELECT
                b.travel_id,
                b.fix_cost,
                b.variable_km,
                b.datetime
            FROM `{bq.get_table_id('bill')}` b
            WHERE b.datetime >= TIMESTAMP('{start_date_sql}')
              AND b.datetime <= TIMESTAMP('{end_date_sql}')
        )
        SELECT
            -- Estatísticas de Viagens
            COALESCE(SUM(td.full_distance), 0) as total_distance,
            COUNT(DISTINCT td.id) as total_travels,
            COALESCE(AVG(td.full_distance), 0) as avg_distance,
            
            -- Estatísticas de Custos
            COALESCE(SUM(bd.fix_cost + (bd.variable_km * td.full_distance)), 0) as total_cost,
            COALESCE(AVG(bd.fix_cost + (bd.variable_km * td.full_distance)), 0) as avg_cost
        FROM travel_data td
        LEFT JOIN bill_data bd ON td.id = bd.travel_id
        """
        
        results = bq.query(sql)
        
        if not results or len(results) == 0:
            data = {
                'total_distance_km': 0.0,
                'total_cost': 0.0,
                'total_travels': 0,
                'avg_cost_per_travel': 0.0,
                'avg_distance_per_travel': 0.0,
            }
        else:
            row = results[0]
            data = {
                'total_distance_km': round(float(row['total_distance']), 2),
                'total_cost': round(float(row['total_cost']), 2),
                'total_travels': int(row['total_travels']),
                'avg_cost_per_travel': round(float(row['avg_cost']), 2),
                'avg_distance_per_travel': round(float(row['avg_distance']), 2),
            }

        filters_applied = {}
        
        if auto_calculated_dates:
            filters_applied['date_range'] = 'last_30_days'
            filters_applied['start_date_calculated'] = start_date_sql
            filters_applied['end_date_calculated'] = end_date_sql
        else:
            if start_date:
                filters_applied['start_date'] = start_date
            if end_date:
                filters_applied['end_date'] = end_date
        
        if unit_id:
            filters_applied['unit_id'] = unit_id_int
        
        if filters_applied:
            data['filters_applied'] = filters_applied
        
        return Response({
            'success': True,
            'data': data,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        traceback.print_exc()
        return Response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e)
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def cost_evolution(request):
    """
    Retorna a evolução dos custos ao longo do tempo.
    """
    bq = BigQueryManager()
    
    try:
        period = request.query_params.get('period', 'month')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        unit_id = request.query_params.get('unit_id')
        limit = request.query_params.get('limit', '12')
        
        if period not in ['day', 'week', 'month']:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_PERIOD',
                    'message': 'Período deve ser "day", "week" ou "month"'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            limit_int = int(limit)
            if limit_int < 1 or limit_int > 100:
                raise ValueError
        except ValueError:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_LIMIT',
                    'message': 'Limit deve ser um número entre 1 e 100'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        start_date_sql = None
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                start_date_sql = start_dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': 'Formato de data inválido para start_date'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if period == 'day':
                start_dt = timezone.now() - timedelta(days=limit_int)
            elif period == 'week':
                start_dt = timezone.now() - timedelta(weeks=limit_int)
            else:  
                start_dt = timezone.now() - timedelta(days=limit_int * 30)
            start_date_sql = start_dt.strftime('%Y-%m-%d %H:%M:%S')
        
        end_date_sql = None
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                end_date_sql = end_dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': 'Formato de data inválido para end_date'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
        
        unit_id_int = None
        if unit_id:
            try:
                unit_id_int = int(unit_id)
                if unit_id_int < 1:
                    raise ValueError
            except ValueError:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_UNIT_ID',
                        'message': 'ID de unidade inválido'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if period == 'day':
            trunc_func = "DATE_TRUNC(datetime, DAY)"
            format_func = "FORMAT_DATE('%Y-%m-%d', DATE_TRUNC(datetime, DAY))"
        elif period == 'week':
            trunc_func = "DATE_TRUNC(datetime, WEEK)"
            format_func = "FORMAT_DATE('%Y-W%U', DATE_TRUNC(datetime, WEEK))"
        else:
            trunc_func = "DATE_TRUNC(datetime, MONTH)"
            format_func = "FORMAT_DATE('%Y-%m', DATE_TRUNC(datetime, MONTH))"
        
        sql = f"""
        WITH bill_travel_data AS (
            SELECT
                b.id as bill_id,
                b.travel_id,
                b.fix_cost,
                b.variable_km,
                b.datetime,
                t.full_distance,
                t.unit_id,
                (b.fix_cost + (b.variable_km * t.full_distance)) as calculated_cost
            FROM `{bq.get_table_id('bill')}` b
            INNER JOIN `{bq.get_table_id('travel')}` t ON b.travel_id = t.id
            WHERE b.datetime >= TIMESTAMP('{start_date_sql}')
              AND t.datetime >= TIMESTAMP('{start_date_sql}')
        """
        
        if end_date_sql:
            sql += f"""
              AND b.datetime <= TIMESTAMP('{end_date_sql}')
              AND t.datetime <= TIMESTAMP('{end_date_sql}')"""
        
        if unit_id_int:
            sql += f" AND t.unit_id = {unit_id_int}"
        
        sql += f"""
        )
        SELECT
            {trunc_func} as period_date,
            {format_func} as period_formatted,
            COUNT(bill_id) as total_bills,
            SUM(fix_cost) as total_fix_cost,
            SUM(variable_km * full_distance) as total_variable_cost,
            SUM(calculated_cost) as total_cost,
            SUM(full_distance) as total_distance,
            AVG(calculated_cost) as avg_cost
        FROM bill_travel_data
        GROUP BY period_date, period_formatted
        ORDER BY period_date ASC
        LIMIT {limit_int}
        """

        results = bq.query(sql)
        
        evolution_data = []
        for row in results:
            evolution_data.append({
                'period': row['period_formatted'],
                'period_full_date': row['period_date'].isoformat() if row['period_date'] else None,
                'total_cost': round(float(row['total_cost'] or 0), 2),
                'fix_cost': round(float(row['total_fix_cost'] or 0), 2),
                'variable_cost': round(float(row['total_variable_cost'] or 0), 2),
                'total_distance_km': round(float(row['total_distance'] or 0), 2),
                'total_bills': int(row['total_bills']),
                'avg_cost': round(float(row['avg_cost'] or 0), 2)
            })
        
        params_info = {
            'period': period,
            'limit': limit_int,
            'results_count': len(evolution_data)
        }
        
        if start_date:
            params_info['start_date'] = start_date
        elif start_date_sql:
            params_info['start_date_calculated'] = start_date_sql
            
        if end_date:
            params_info['end_date'] = end_date
            
        if unit_id:
            params_info['unit_id'] = unit_id_int
        
        return Response({
            'success': True,
            'data': evolution_data,
            'params': params_info,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        traceback.print_exc()
        return Response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e)
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)