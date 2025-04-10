from django.db import models
from datetime import timedelta
from django.core.validators import MinLengthValidator
from django.utils import timezone
# Create your models here.

class Driver(models.Model):
    full_name = models.CharField(max_length=255)
    license_number = models.CharField(
        max_length=20,
        unique=20,
        validators=[MinLengthValidator(5)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.license_number})"


class Trip(models.Model):
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    current_cycle_used = models.DurationField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Trip #{self.id} - {self.pickup_location} to {self.dropoff_location}"
    

class ELDlog(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='logs')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    driving_time = models.DurationField(editable=False)
    rest_breaks = models.DurationField(default=timedelta(minutes=30))
    status_choices = [
        ('D', 'Driving'),
        ('OFF', 'Off Duty'),
        ('SB', 'Sleep Berth'),
        ('ON', 'On Duty')
    ]
    status = models.CharField(max_length=3, choices=status_choices)
    
    def save(self, *args, **kwargs):

        if self.start_time and self.end_time:
            self.driving_time = self.end_time - self.start_time
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Log {self.id} - {self.get_status_display()}"
