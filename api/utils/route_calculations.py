
def generate_route_instructions(trip):

    """ Generates basic route instructions for a Trip.
    For example, departure, pick-up and drop-off locations are returned, as well as
    and a few suggestions for breaks.$
    """

    instructions = {
        "starting_point": trip.current_location,
        "pickup_point": trip.pickup_location,
        "dropoff_point": trip.dropoff_location,
        "suggested_stops": [
            "Stop pour carburant (tous les 1 000 miles)",
            "Pause de repos (après 8 heures de conduite)",
            "Arrêt pour chargement/déchargement (1 heure)"
        ]
    }

    return instructions