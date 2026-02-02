import requests
from datetime import datetime, timedelta

OPENSKY_STATES_URL = "https://opensky-network.org/api/states/all"
OPENSKY_FLIGHTS_URL = "https://opensky-network.org/api/flights/aircraft"


def find_icao24_by_registration(registration: str):
    """
    Probeert ICAO24 te vinden op basis van aircraft registration.
    MVP-heuristiek via callsign.
    """
    try:
        r = requests.get(OPENSKY_STATES_URL, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return None

    reg_clean = registration.replace("-", "").upper()

    for state in data.get("states", []):
        callsign = (state[1] or "").strip().upper()
        if reg_clean in callsign:
            return state[0]  # ICAO24

    return None


def day_to_unix_range(date_obj):
    start = datetime.combine(date_obj, datetime.min.time())
    end = start + timedelta(days=1)
    return int(start.timestamp()), int(end.timestamp())


def fetch_flights_by_icao24(icao24: str, date_obj):
    begin, end = day_to_unix_range(date_obj)

    params = {
        "icao24": icao24,
        "begin": begin,
        "end": end
    }

    try:
        r = requests.get(OPENSKY_FLIGHTS_URL, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []