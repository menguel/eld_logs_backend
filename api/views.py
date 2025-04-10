from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Trip, ELDlog
from .serializers import TripSerializer, ELDLogsSerializer
from .utils.hos_calculations import calculate_hos_compliance
from django.utils import timezone
# Create your views here.

class TripViewset(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        trip = serializer.save()
        compliance = calculate_hos_compliance(trip)

        if not compliance['valid']:
            trip.delete()
            return Response(
                {"errors": compliance['violations']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def get_queryset(self):
    #     return Trip.objects.filter(driver=self.request.user)
    
    # def perform_create(self, serializer):
    #     serializer.save(driver=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_log(self, request, pk=None):

        trip = self.get_object()
        serializer = ELDLogsSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(trip=trip)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def compliance_report(self, request, pk=None):

        trip = self.get_object()
        report = calculate_hos_compliance(trip)
        return Response(report)