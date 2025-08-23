# utils/time_helpers.py

from datetime import datetime, timedelta, timezone
from typing import Tuple
import pytz

def get_current_utc_time() -> datetime:
    return datetime.utcnow().replace(tzinfo=timezone.utc)

def get_ist_time() -> datetime:
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

def get_current_legend_season_and_day(seasons: list) -> Tuple[int, int]:
    """Determine the current legend league season number and day based on seasons list."""
    now = get_current_utc_time()

    for season in seasons:
        start = season["start"].replace(tzinfo=timezone.utc)
        end = season["end"].replace(tzinfo=timezone.utc)
        if start <= now <= end:
            duration = (now - start).days + 1  # +1 for current day number
            return season["season_number"], duration

    # If no current season found, return last season and last day
    last_season = seasons[-1]
    return last_season["season_number"], last_season["duration_days"]
    
