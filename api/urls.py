from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewset

router = DefaultRouter()
router.register(r'trips', TripViewset, basename='trip')

urlpatterns = [
    path('', include(router.urls)),
]
