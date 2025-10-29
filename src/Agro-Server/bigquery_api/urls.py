from django.urls import path
from api import views

urlpatterns = [
    path("api/inserir/", views.inserir_registro),
    path("api/atualizar/", views.atualizar_registro),
    path("api/remover/", views.remover_registro),
]
