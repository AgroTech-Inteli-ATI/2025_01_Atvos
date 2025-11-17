"""
Middleware para validar JWT em rotas protegidas
"""
from django.http import JsonResponse
from django.conf import settings
from functools import wraps
from .models import User
import jwt

def jwt_required(view_func):
    """
    Decorator para proteger views com JWT
    
    Uso:
    @api_view(['GET'])
    @jwt_required
    def protected_view(request):
        # request.user_id e request.user_email estarão disponíveis
        return Response({'message': 'Acesso autorizado'})
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Obtém o token do header Authorization
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return JsonResponse(
                {'error': 'Token de autenticação não fornecido.'},
                status=401
            )
        
        if not auth_header.startswith('Bearer '):
            return JsonResponse(
                {'error': 'Formato de token inválido. Use: Bearer <token>'},
                status=401
            )
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decodifica e valida o token
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=['HS256']
            )
            
            # Adiciona os dados do usuário ao request
            request.user_id = payload.get('user_id')
            request.user_email = payload.get('email')
            request.user_name = payload.get('name')
            
            # Opcional: verificar se o usuário ainda existe e está ativo
            try:
                user = User.objects.get(id=request.user_id, ativo=True)
                request.user = user
            except User.DoesNotExist:
                return JsonResponse(
                    {'error': 'Usuário não encontrado ou inativo.'},
                    status=401
                )

            return view_func(request, *args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {'error': 'Token expirado. Faça login novamente.'},
                status=401
            )
        except jwt.InvalidTokenError:
            return JsonResponse(
                {'error': 'Token inválido.'},
                status=401
            )
        except Exception as e:
            return JsonResponse(
                {'error': f'Erro ao validar token: {str(e)}'},
                status=401
            )
    
    return wrapper


# Exemplo de view protegida
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .middleware import jwt_required

@api_view(['GET'])
@jwt_required
def profile(request):
    return Response({
        'message': 'Perfil do usuário',
        'user': {
            'id': request.user_id,
            'name': request.user_name,
            'email': request.user_email
        }
    })
"""