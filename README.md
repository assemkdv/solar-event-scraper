# Solar Flare Scraper 

Downloads real solar flare data from NOAA and lets you search it locally.
---

## What it does

- Downloads daily solar flare reports from a NOAA government server
- Saves them to a local CSV file (no database needed)
- Removes duplicate events automatically
- Lets you search by date range or flare intensity
- Can update itself with the latest data anytime

---

## Files

| File | What it does |
|---|---|
| `scraper.py` | Downloads data from NOAA and saves to CSV |
| `query.py` | Search and filter your saved data |
| `update.py` | Pull in the latest data since last run |
| `solar_events.csv` | Your local database (auto-created) |

---

## Setup

```bash
git clone https://github.com/assemkdv/solar-event-scraper.git
cd solar-event-scraper
pip install -r requirements.txt
```

Requires Python 3.8+.

---

## How to run

**Download the last 30 days:**
```bash
python scraper.py
```

**See a quick summary (total flares, breakdown by class, and M-class-and-above list):**
```bash
python query.py
```

**Update with latest flares:**
```bash
python update.py
```

**Download a specific year:**
```python
from scraper import download
from datetime import date

download(date(2024, 1, 1), date(2024, 12, 31))
```

**Custom search:**
```python
from query import search, stats

stats()                                               # summary of everything
search(min_class="M")                                 # M and X class only
search(min_class="X")                                 # X class only
search(start_date="2024-01-01", end_date="2024-06-30")           # by date
search(start_date="2024-01-01", end_date="2024-12-31", min_class="M")  # both
```

---

## Data source

**NOAA National Centers for Environmental Information**
https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports/solar_event_reports/

Free, public NOAA daily solar event reports spanning multiple decades, updated daily. All times (start, peak, and end) are reported in UTC.

The scraper waits briefly between requests and retries on network errors, to stay easy on NOAA's server. Avoid running full-history backfills more often than you need to.

---

## What the data looks like

| date | start | peak | end | class | active_region |
|---|---|---|---|---|---|
| 2024-01-23 | 0309 | 0331 | 0338 | M5.1 | 3559 |
| 2024-05-10 | 0643 | 0654 | 0701 | X3.9 | 3664 |

**Flare classes** (weakest to strongest): A → B → C → M → X

- **C class** — minor, very common
- **M class** — moderate, can cause radio blackouts
- **X class** — major, rare and powerful

---

## Limitations

- Duplicate detection is keyed on date, start, peak, and end time, not classification, so a flare that NOAA later reclassifies is updated in place rather than duplicated. Two distinct flares that happen to share the exact same start/peak/end on the same day (rare) would still be treated as one.
- If a day's report can't be reached after a few retries, that day is skipped and logged, not silently treated as "no flares."
- `solar_events.csv` is committed to this repo as a working snapshot. Running `update.py` or `scraper.py` will refresh it locally with current data.

---

## License

MIT — see [LICENSE](LICENSE).
