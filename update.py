"""
update.py
Run this anytime to pull in the latest flare data.
"""

from datetime import date, timedelta, datetime
from scraper import load_data, download


def update():
    existing = load_data()

    if existing:
        latest = max(e["date"] for e in existing)
        start  = datetime.strptime(latest, "%Y-%m-%d").date() - timedelta(days=2)
    else:
        start  = date.today() - timedelta(days=30)

    end = date.today()
    print(f"Updating from {start} to {end}...")
    download(start, end)
    print("Done!")


if __name__ == "__main__":
    update()