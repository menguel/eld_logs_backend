from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from ..models import ELDlog, Trip


def calculate_hos_compliance(trip: Trip) -> dict:
    """ Implement FMCSA rules:
    - 70 hours over 8 days
    - 14 hours driving window
    - 30 min break after 8 a.m

    Args:
        trip (_type_): _description_
    """
    compliance = {
        "valid": True, 
        "violations": [],
        "remaining_hours": 70.0
    }

    try:
        eignt_days_ago = timezone.now() - timedelta(days=8)

        recent_logs = ELDlog.objects.filter(
            trip__driver=trip.driver,
            start_time__gte=eignt_days_ago
        )

        total_driving = sum(
            log.driving_time.total_seconds()/3600 for log in recent_logs
        )
        total_used = total_driving + trip.current_cycle_used.total_seconds() / 3600

        if total_used > 70:
            compliance["valid"] = False
            compliance["violations"].append(
                f"Violation 70hrs/8days: {total_used:.1f}hrs used"
            )
        compliance["remaining_hours"] = 70 -total_used


        trip_duration = (trip.logs.aggregate(
            total=Sum('driving_time')
        ))['total'] or timedelta()

        if trip_duration > timedelta(hours=14):
            compliance['valid'] = False
            compliance['violations'].append(
                f" Violation window 14 hours: {trip_duration}"
            )

        continuous_driving = timedelta()
        for log in trip.logs.order_by('start_time'):
            if log.status == 'D':
                continuous_driving += log.driving_time
                if continuous_driving >= timedelta(hours=8):
                    if log.rest_breaks < timedelta(minutes=30):
                        compliance['valid'] = False
                        compliance['violations'].append(
                            f"Insufficient break after {continuous_driving} hours of driving"
                        )
                    continuous_driving = timedelta()
            else:
                continuous_driving = timedelta()

    except Exception as e:
        compliance['valid'] = False
        compliance['violations'].append(f"Erreur de calcul: {str(e)}")

    return compliance