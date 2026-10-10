"""
scraper.py
Downloads solar flare data from NOAA and saves it to a CSV file.
"""

import csv
import re
import time
import requests
from datetime import date, datetime, timedelta
from pathlib import Path

DATA_FILE      = "solar_events.csv"
BASE_URL       = "https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/solar_event_reports"
CLASS_ORDER    = {"A": 0, "B": 1, "C": 2, "M": 3, "X": 4}
COLUMNS        = ["start_time", "peak_time", "end_time", "class", "active_region"]
RETRY_ATTEMPTS = 3      # how many times to retry a day's file after a network error
RETRY_DELAY    = 2      # seconds, doubled after each retry
REQUEST_DELAY  = 0.5    # seconds to wait between days, to stay easy on NOAA's server

_HHMM = re.compile(r"^[A-Z]?(\d{2})(\d{2})$")   # NOAA may prefix a time with A (after), B (before) or U (uncertain)


def to_timestamp(d: date, hhmm: str, not_before: str = "") -> str:
    """
    Turn a NOAA HHMM time on report day `d` into "YYYY-MM-DD HH:MM:SS".

    NOAA reports list every event under the day it started, with bare
    HHMM times. A flare that starts at 23:50 and peaks at 00:05 therefore
    has its peak (and end) on the NEXT day: when the time is earlier than
    `not_before` (the previous timestamp of the same flare), it is moved
    one day forward. "////" (not reported) becomes an empty cell. The
    uncertainty letter is dropped.
    """
    m = _HHMM.match(hhmm)
    if not m:
        return ""
    stamp = datetime(d.year, d.month, d.day, int(m[1]), int(m[2]))
    if not_before and stamp.strftime("%Y-%m-%d %H:%M:%S") < not_before:
        stamp += timedelta(days=1)
    return stamp.strftime("%Y-%m-%d %H:%M:%S")


def download_day(d: date) -> list:
    """Download and parse flares for one day."""
    url = f"{BASE_URL}/{d.year}/{d.month:02d}/{d.strftime('%Y%m%d')}events.txt"

    response = None
    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.get(url, timeout=15)
            break
        except requests.RequestException as exc:
            if attempt == RETRY_ATTEMPTS - 1:
                print(f"Network error fetching {d}, giving up: {exc}")
                return []
            time.sleep(RETRY_DELAY * (2 ** attempt))

    if response.status_code == 404:
        return []  # no report published for this day, not an error

    try:
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Server error fetching {d}: {exc}")
        return []

    flares = []
    for line in response.text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(":"):
            continue
        parts = line.split()
        if "XRA" not in parts:
            continue
        i = parts.index("XRA")
        try:
            start  = parts[i - 5]
            peak   = parts[i - 4]
            end    = parts[i - 3]
            cls    = parts[i + 2].upper()
            region = parts[i + 4] if len(parts) > i + 4 else ""
        except IndexError:
            continue
        if not cls or cls[0] not in CLASS_ORDER:
            continue
        start_time = to_timestamp(d, start)
        peak_time  = to_timestamp(d, peak, not_before=start_time)
        end_time   = to_timestamp(d, end,  not_before=peak_time or start_time)
        flares.append({
            "start_time":    start_time,
            "peak_time":     peak_time,
            "end_time":      end_time,
            "class":         cls,
            "active_region": region,
        })
    return flares


def load_data() -> list:
    """Load saved events from CSV."""
    if not Path(DATA_FILE).exists():
        return []
    with open(DATA_FILE, newline="") as f:
        return list(csv.DictReader(f))


def save_data(events: list):
    """Save all events to CSV."""
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(events)


def merge(existing: list, new: list) -> list:
    """Combine old and new events, removing duplicates.

    Keyed on start/peak/end times rather than class, since NOAA sometimes
    revises a flare's classification after the fact. Keying on class would
    treat a revised event as a brand-new one instead of updating it.
    """
    seen = {}
    for e in existing + new:
        key = f"{e['start_time']}_{e['peak_time']}_{e['end_time']}"
        seen[key] = e
    return sorted(seen.values(), key=lambda e: e["start_time"])


def download(start_date: date, end_date: date):
    """Download flares between two dates and save to CSV."""
    print(f"Downloading {start_date} to {end_date}...")
    existing   = load_data()
    new_events = []
    d = start_date
    while d <= end_date:
        flares = download_day(d)
        new_events.extend(flares)
        d += timedelta(days=1)
        if d <= end_date:
            time.sleep(REQUEST_DELAY)
    print(f"Found {len(new_events)} new flares")
    all_events = merge(existing, new_events)
    save_data(all_events)
    print(f"Total in database: {len(all_events)}")


if __name__ == "__main__":
    # Run this file directly to download the last 30 days
    today = date.today()
    start = today - timedelta(days=30)
    download(start, today)
