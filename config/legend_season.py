from datetime import datetime, timedelta, timezone

# Legend League season reset time: Last Monday of every month at 05:00 UTC
# Players reset to 5000 trophies at this time.
# Season length is either 28 or 35 days depending on the month.

# Predefined 2025 season reset dates in UTC as per last Mondays and 5:00 UTC reset.
SEASONS_2025 = [
    {"season": 1, "start": datetime(2025, 1, 27, 5, 0, 0, tzinfo=timezone.utc), "length_days": 28},
    {"season": 2, "start": datetime(2025, 2, 24, 5, 0, 0, tzinfo=timezone.utc), "length_days": 35},
    {"season": 3, "start": datetime(2025, 3, 31, 5, 0, 0, tzinfo=timezone.utc), "length_days": 28},
    {"season": 4, "start": datetime(2025, 4, 28, 5, 0, 0, tzinfo=timezone.utc), "length_days": 28},
    {"season": 5, "start": datetime(2025, 5, 26, 5, 0, 0, tzinfo=timezone.utc), "length_days": 35},
    {"season": 6, "start": datetime(2025, 6, 30, 5, 0, 0, tzinfo=timezone.utc), "length_days": 28},
    {"season": 7, "start": datetime(2025, 7, 28, 5, 0, 0, tzinfo=timezone.utc), "length_days": 28},
    {"season": 8, "start": datetime(2025, 8, 25, 5, 0, 0, tzinfo=timezone.utc), "length_days": 35},
    {"season": 9, "start": datetime(2025, 9, 29, 5, 0, 0, tzinfo=timezone.utc), "length_days": 28},
    {"season": 10, "start": datetime(2025, 10, 27, 5, 0, 0, tzinfo=timezone.utc), "length_days": 28},
    {"season": 11, "start": datetime(2025, 11, 24, 5, 0, 0, tzinfo=timezone.utc), "length_days": 35},
    {"season": 12, "start": datetime(2025, 12, 29, 5, 0, 0, tzinfo=timezone.utc), "length_days": 28},
]

def get_current_season(now_utc: datetime = None):
    """
    Return current season number and day number within the season based on current datetime in UTC.
    """
    now_utc = now_utc or datetime.utcnow().replace(tzinfo=timezone.utc)

    for i, season in enumerate(SEASONS_2025):
        start = season["start"]
        length = season["length_days"]
        end = start + timedelta(days=length)
        if start <= now_utc < end:
            day = (now_utc - start).days + 1
            return season["season"], day

    # If not in any season period, return last or first as appropriate
    if now_utc < SEASONS_2025[0]["start"]:
        return None, 0
    return SEASONS_2025[-1]["season"], (now_utc - SEASONS_2025[-1]["start"]).days + 1

