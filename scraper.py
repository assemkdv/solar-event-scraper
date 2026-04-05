"""
scraper.py
Downloads solar flare data from NOAA and saves it to a CSV file.
"""

import csv
import requests
from datetime import date, timedelta
from pathlib import Path

DATA_FILE   = "solar_events.csv"
BASE_URL    = "https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/solar_event_reports"
CLASS_ORDER = {"A": 0, "B": 1, "C": 2, "M": 3, "X": 4}
COLUMNS     = ["date", "start", "peak", "end", "class", "active_region"]


def download_day(d: date) -> list:
    """Download and parse flares for one day."""
    url = f"{BASE_URL}/{d.year}/{d.month:02d}/{d.strftime('%Y%m%d')}events.txt"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 404:
            return []
        response.raise_for_status()
    except requests.RequestException:
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
        flares.append({
            "date":          d.strftime("%Y-%m-%d"),
            "start":         "" if start == "////" else start,
            "peak":          "" if peak  == "////" else peak,
            "end":           "" if end   == "////" else end,
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
    """Combine old and new events, removing duplicates."""
    seen = {}
    for e in existing + new:
        key = f"{e['date']}_{e['start']}_{e['class']}"
        seen[key] = e
    return sorted(seen.values(), key=lambda e: (e["date"], e["start"]))


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
    print(f"Found {len(new_events)} new flares")
    all_events = merge(existing, new_events)
    save_data(all_events)
    print(f"Total in database: {len(all_events)}")


if __name__ == "__main__":
    # Run this file directly to download the last 30 days
    today = date.today()
    start = today - timedelta(days=30)
    download(start, today)