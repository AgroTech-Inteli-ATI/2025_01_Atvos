from django.db import models
from django.contrib.auth.hashers import make_password

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Nome')
    email = models.EmailField(unique=True, max_length=255, verbose_name='Email')
    senha = models.CharField(max_length=255, verbose_name='Senha')
    ativo = models.BooleanField(default=True, verbose_name='Ativo', db_column='active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.name} ({self.email})"

    def save(self, *args, **kwargs):
        """
        Garante que a senha seja criptografada antes de salvar
        Verifica se a senha já não está hasheada
        """
        if self.senha and not self.senha.startswith('pbkdf2_sha256$'):
            self.senha = make_password(self.senha)
        super().save(*args, **kwargs)
    
    def soft_delete(self):
        """
        Realiza a exclusão lógica do usuário
        """
        self.ativo = False
        self.save()
    
