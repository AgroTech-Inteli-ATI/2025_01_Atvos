from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User
import re

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para cadastro de usuários
    """
    senha = serializers.CharField(
        write_only=True, 
        min_length=6, 
        style={'input_type': 'password'},
        help_text='Senha deve ter no mínimo 6 caracteres'
    )
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'senha', 'ativo', 'created_at', 'updated_at']
        read_only_fields = ['id', 'ativo', 'created_at', 'updated_at']
        extra_kwargs = {
            'email': {
                'required': True,
                'help_text': 'Email válido e único'
            },
            'name': {
                'required': True,
                'help_text': 'Nome completo do usuário'
            }
        }

    def validate_email(self, value):
        """
        Valida o formato do email e verifica duplicidade
        """
        # Valida formato do email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Formato de email inválido.")
        
        # Converte para minúsculo
        email = value.lower().strip()
        
        # Verifica se o email já existe (apenas na criação)
        if self.instance is None:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError(
                    "Este email já está cadastrado no sistema."
                )
        # Na atualização, verifica se o email pertence a outro usuário
        else:
            if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(
                    "Este email já está cadastrado no sistema."
                )
        
        return email

    def validate_name(self, value):
        """
        Valida o nome do usuário
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "O nome deve ter no mínimo 3 caracteres."
            )
        return value.strip()

    def validate_senha(self, value):
        """
        Valida a força da senha
        """
        if len(value) < 6:
            raise serializers.ValidationError(
                "A senha deve ter no mínimo 6 caracteres."
            )
        
        if not any(char.isdigit() for char in value):
             raise serializers.ValidationError(
                 "A senha deve conter pelo menos um número."
             )
        
        return value

    def create(self, validated_data):
        """
        Cria usuário com senha criptografada
        """
        validated_data['senha'] = make_password(validated_data['senha'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Atualiza usuário, criptografando a senha se fornecida
        """
        if 'senha' in validated_data:
            validated_data['senha'] = make_password(validated_data['senha'])
        return super().update(instance, validated_data)


class LoginSerializer(serializers.Serializer):
    """
    Serializer para login de usuários
    """
    email = serializers.EmailField(
        required=True,
        help_text='Email cadastrado'
    )
    senha = serializers.CharField(
        required=True, 
        write_only=True, 
        style={'input_type': 'password'},
        help_text='Senha do usuário'
    )

    def validate_email(self, value):
        """
        Normaliza o email
        """
        return value.lower().strip()