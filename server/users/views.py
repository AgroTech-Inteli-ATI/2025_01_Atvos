from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from django.conf import settings
from .models import User
from .serializers import UserSerializer, LoginSerializer
import jwt
from datetime import datetime, timedelta
from functools import wraps

def token_required(f):
    """
    Decorator para validar o token JWT
    """
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return Response(
                {'error': 'Token não fornecido.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            # Remove o prefixo 'Bearer ' se existir
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decodifica o token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            request.user_id = payload['user_id']
            
        except jwt.ExpiredSignatureError:
            return Response(
                {'error': 'Token expirado.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except jwt.InvalidTokenError:
            return Response(
                {'error': 'Token inválido.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return f(request, *args, **kwargs)
    
    return decorated_function


@api_view(['POST'])
def register(request):

    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        response_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_at': user.created_at
        }
        
        return Response(
            {
                'message': 'Usuário cadastrado com sucesso!',
                'user': response_data
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(
        {
            'message': 'Erro ao cadastrar usuário.',
            'errors': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def login(request):

    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                'message': 'Dados inválidos.',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    email = serializer.validated_data['email']
    senha = serializer.validated_data['senha']
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'Email ou senha incorretos.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not check_password(senha, user.senha):
        return Response(
            {'error': 'Email ou senha incorretos.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Gera o JWT token
    expiration = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    payload = {
        'user_id': user.id,
        'email': user.email,
        'name': user.name,
        'exp': expiration,
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    return Response(
        {
            'message': 'Login realizado com sucesso!',
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['PUT','PATCH'])
@token_required
def update_user(request, user_id):

    # Verifica se o usuário está tentando atualizar seus próprios dados
    if request.user_id != user_id:
        return Response(
            {'error': 'Você não tem permissão para atualizar este usuário.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'Usuário não encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # PUT requer todos os campos, PATCH permite atualização parcial
    partial = request.method == 'PATCH'
    
    serializer = UserSerializer(user, data=request.data, partial=partial)
    
    if serializer.is_valid():
        updated_user = serializer.save()
        
        response_data = {
            'id': updated_user.id,
            'name': updated_user.name,
            'email': updated_user.email,
            'updated_at': updated_user.updated_at
        }
        
        return Response(
            {
                'message': 'Usuário atualizado com sucesso!',
                'user': response_data
            },
            status=status.HTTP_200_OK
        )
    
    return Response(
        {
            'message': 'Erro ao atualizar usuário.',
            'errors': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['DELETE'])
@token_required
def delete_user(request, user_id):

    # Verifica se o usuário está tentando deletar sua própria conta
    if request.user_id != user_id:
        return Response(
            {'error': 'Você não tem permissão para desativar este usuário.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Busca apenas usuários ativos
        user = User.objects.get(id=user_id, ativo=True)
    except User.DoesNotExist:
        return Response(
            {'error': 'Usuário não encontrado ou já está inativo.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Realiza o soft delete
    user.soft_delete()
    
    return Response(
        {
            'message': 'Usuário desativado com sucesso!',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'ativo': user.ativo
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@token_required
def get_user(request, user_id):

    # Verifica se o usuário está consultando seus próprios dados
    if request.user_id != user_id:
        return Response(
            {'error': 'Você não tem permissão para acessar este usuário.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'Usuário não encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    response_data = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'created_at': user.created_at,
        'updated_at': user.updated_at
    }
    
    return Response(
        {'user': response_data},
        status=status.HTTP_200_OK
    )


