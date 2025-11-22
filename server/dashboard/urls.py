from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('travel-summary/', views.travel_summary, name='travel-summary'),
    path('cost-evolution/', views.cost_evolution, name='cost-evolution'),
]