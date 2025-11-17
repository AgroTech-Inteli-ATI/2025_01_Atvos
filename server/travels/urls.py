from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TravelViewSet, BillViewSet

router = DefaultRouter()
router.register(r'travels', TravelViewSet, basename='travel')
router.register(r'bills', BillViewSet, basename='bill')

urlpatterns = [
    path('', include(router.urls)),
]