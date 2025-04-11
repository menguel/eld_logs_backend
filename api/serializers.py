from rest_framework import serializers
from .models import Driver, Trip, ELDlog
from django.contrib.auth import get_user_model

# User = get_user_model

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['full_name', 'license_number']

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email']

class ELDLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ELDlog
        fields = '__all__'
        read_only_fields = ['driving_time']

class TripSerializer(serializers.ModelSerializer):

    driver = DriverSerializer(required=True)
    
    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = ['created_at']

    def validate_current_cycle_used(self, value):
        """Personalised validation for driving time"""
        if value.total_seconds() < 0:
            raise serializers.ValidationError("Cycle time cannot be negative")
        return value
    
    def create(self, validated_data):
        """Creating a trip with associated logs"""
        driver_data = validated_data.pop('driver', None)
        logs_data = validated_data.pop('logs', [])

        if driver_data is None:
            raise serializers.ValidationError({"driver" : "This field is required!"})
        
        license_number = driver_data.get('license_number')
        if not license_number:
            raise serializers.ValidationError({"license_number": "This field is required"})

        driver, created = Driver.objects.get_or_create(
            license_number=license_number,
            defaults={'full_name': driver_data.get('full_name', '')}
        )

        trip = Trip.objects.create(driver=driver, **validated_data)

        for log_data in logs_data:
            ELDlog.objects.create(trip=trip, **log_data)

        return trip