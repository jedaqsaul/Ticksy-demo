import urllib.parse
from datetime import datetime

def generate_calendar_link(event):
    start = event.start_time.strftime("%Y%m%dT%H%M%SZ")
    end = event.end_time.strftime("%Y%m%dT%H%M%SZ")

    base_url = "https://calendar.google.com/calendar/render"
    params = {
        "action": "TEMPLATE",
        "text": event.title,
        "dates": f"{start}/{end}",
        "details": event.description,
        "location": event.location
    }

    query = urllib.parse.urlencode(params)
    return f"{base_url}?{query}"
