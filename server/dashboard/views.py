from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from datetime import datetime, timedelta

from travels.models import Travel, Bill


@api_view(['GET'])
def travel_summary(request):
    """
    Retorna resumo geral de viagens e custos.
    """
    try:
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        unit_id = request.query_params.get('unit_id')
        
        travels = Travel.objects.all()
        bills = Bill.objects.all()
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                travels = travels.filter(datetime__gte=start_dt)
                bills = bills.filter(datetime__gte=start_dt)
            except ValueError:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': 'Formato de data inválido para start_date'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                travels = travels.filter(datetime__lte=end_dt)
                bills = bills.filter(datetime__lte=end_dt)
            except ValueError:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': 'Formato de data inválido para end_date'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if unit_id:
            try:
                unit_id_int = int(unit_id)
                travels = travels.filter(unit_id=unit_id_int)
                bills = bills.filter(travel__unit_id=unit_id_int)
            except ValueError:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_UNIT_ID',
                        'message': 'ID de unidade inválido'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
        
        travel_stats = travels.aggregate(
            total_distance=Sum('full_distance'),
            total_travels=Count('id'),
            avg_distance=Avg('full_distance')
        )

        cost_stats = bills.select_related('travel').annotate(
            calculated_cost=F('fix_cost') + (F('variable_km') * F('travel__full_distance'))
        ).aggregate(
            total_cost=Sum('calculated_cost'),
            avg_cost=Avg('calculated_cost')
        )
        
        data = {
            'total_distance_km': round(float(travel_stats['total_distance'] or 0), 2),
            'total_cost': round(float(cost_stats['total_cost'] or 0), 2),
            'total_travels': travel_stats['total_travels'],
            'avg_cost_per_travel': round(float(cost_stats['avg_cost'] or 0), 2),
            'avg_distance_per_travel': round(float(travel_stats['avg_distance'] or 0), 2),
        }
        
        filters_applied = {}
        if start_date:
            filters_applied['start_date'] = start_date
        if end_date:
            filters_applied['end_date'] = end_date
        if unit_id:
            filters_applied['unit_id'] = unit_id
        
        if filters_applied:
            data['filters_applied'] = filters_applied
        
        return Response({
            'success': True,
            'data': data,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
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
        
        bills = Bill.objects.select_related('travel').all()
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                bills = bills.filter(datetime__gte=start_dt)
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
            bills = bills.filter(datetime__gte=start_dt)
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                bills = bills.filter(datetime__lte=end_dt)
            except ValueError:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': 'Formato de data inválido para end_date'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if unit_id:
            try:
                unit_id_int = int(unit_id)
                bills = bills.filter(travel__unit_id=unit_id_int)
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
            trunc_func = TruncDate
            date_format = '%Y-%m-%d'
        elif period == 'week':
            trunc_func = TruncWeek
            date_format = '%Y-W%U'
        else:  
            trunc_func = TruncMonth
            date_format = '%Y-%m'
        
        bills_by_period = bills.annotate(
            period_date=trunc_func('datetime'),
            calculated_cost=F('fix_cost') + (F('variable_km') * F('travel__full_distance'))
        ).values('period_date').annotate(
            total_bills=Count('id'),
            total_fix_cost=Sum('fix_cost'),
            total_variable_cost=Sum(F('variable_km') * F('travel__full_distance')),
            total_cost=Sum('calculated_cost'),
            total_distance=Sum('travel__full_distance'),
            avg_cost=Avg('calculated_cost')
        ).order_by('period_date')[:limit_int]
        
        evolution_data = []
        for item in bills_by_period:
            period_date = item['period_date']
            
            evolution_data.append({
                'period': period_date.strftime(date_format),
                'period_full_date': period_date.isoformat(),
                'total_cost': round(float(item['total_cost'] or 0), 2),
                'fix_cost': round(float(item['total_fix_cost'] or 0), 2),
                'variable_cost': round(float(item['total_variable_cost'] or 0), 2),
                'total_distance_km': round(float(item['total_distance'] or 0), 2),
                'total_bills': item['total_bills'],
                'avg_cost': round(float(item['avg_cost'] or 0), 2)
            })
        
        params_info = {
            'period': period,
            'limit': limit_int,
            'results_count': len(evolution_data)
        }
        
        if start_date:
            params_info['start_date'] = start_date
        if end_date:
            params_info['end_date'] = end_date
        if unit_id:
            params_info['unit_id'] = unit_id
        
        return Response({
            'success': True,
            'data': evolution_data,
            'params': params_info,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e)
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)