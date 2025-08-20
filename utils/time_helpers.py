# utils/time_helpers.py
from datetime import datetime, timedelta

IST_OFFSET_HOURS = 5
IST_OFFSET_MINUTES = 30

def get_ist_now():
    return datetime.utcnow() + timedelta(hours=IST_OFFSET_HOURS, minutes=IST_OFFSET_MINUTES)

def format_ist(dt=None, fmt="%d-%m-%Y %I:%M %p"):
    if dt is None:
        dt = get_ist_now()
    return dt.strftime(fmt)
  
