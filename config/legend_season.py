# config/legend_season.py

from datetime import datetime, timezone

# Legend League 2025 Official Season Schedule (all times UTC)
# Seasons reset on last Monday of the month at 05:00 UTC

LEGEND_SEASONS_2025 = [
    {
        "season_number": 1,
        "start": datetime(2025, 1, 27, 5, 0, tzinfo=timezone.utc),
        "end": datetime(2025, 2, 24, 4, 59, tzinfo=timezone.utc),
        "duration_days": 28
    },
    {
        "season_number": 2,
        "start": datetime(2025, 2, 24, 5, 0, tzinfo=timezone.utc),
        "end": datetime(2025, 3, 31, 4, 59, tzinfo=timezone.utc),
        "duration_days": 35
    },
    {
        "season_number": 3,
        "start": datetime(2025, 3, 31, 5, 0, tzinfo=timezone.utc),
        "end": datetime(2025, 4, 28, 4, 59, tzinfo=timezone.utc),
        "duration_days": 28
    },
    {
        "season_number": 4,
        "start": datetime(2025, 4, 28, 5, 0, tzinfo=timezone.utc),
        "end": datetime(2025, 5, 26, 4, 59, tzinfo=timezone.utc),
        "duration_days": 28
    },
    {
        "season_number": 5,
        "start": datetime(2025, 5, 26, 5, 0, tzinfo=timezone.utc),
        "end": datetime(2025, 6, 30, 4, 59, tzinfo=timezone.utc),
        "duration_days": 35
    },
    {
        "season_number": 6,
        "start": datetime(2025, 6, 30, 5, 0, tzinfo=timezone.utc),
        "end": datetime(2025, 7, 28, 4, 59, tzinfo=timezone.utc),
        "duration_days": 28
    },
    {
        "season_number": 7,
        "start": datetime(2025, 7, 28, 5, 0, tzinfo=timezone.utc),
        "end": datetime(2025, 8, 25, 4, 59, tzinfo=timezone.utc),
        "duration_days": 28
    },
    {
        "season_number": 8,
        "start": datetime(2025, 8, 25, 5, 0, tzinfo=timezone.utc),
        "end": datetime(2025, 9, 29, 4, 59, tzinfo=timezone.utc),
        "duration_days": 35
    },
    {
        "season_number": 9,
        "start": datetime(2025, 9, 29, 5, 0, tzinfo=timezone.utc),
        "end": datetime(2025, 10, 27, 4, 59, tzinfo=timezone.utc),
        "duration_days": 28
    },
    {
        "season_number": 10,
        "start": datetime(2025, 10, 27, 5, 0, tzinfo=timezone.utc),
        "end": datetime(2025, 11, 24, 4, 59, tzinfo=timezone.utc),
        "duration_days": 28
    },
    {
        "season_number": 11,
        "start": datetime(2025, 11, 24, 5, 0, tzinfo=timezone.utc),
        "end": datetime(2025, 12, 29, 4, 59, tzinfo=timezone.utc),
        "duration_days": 35
    },
    {
        "season_number": 12,
        "start": datetime(2025, 12, 29, 5, 0, tzinfo=timezone.utc),
        "end": datetime(2026, 1, 26, 4, 59, tzinfo=timezone.utc),
        "duration_days": 28
    }
]
