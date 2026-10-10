"""
query.py
Search your saved solar flare data.
"""

from scraper import load_data, CLASS_ORDER


def search(start_date="", end_date="", min_class=""):
    """
    Search the saved data.

    Examples:
        search(min_class="M")
        search(start_date="2024-01-01", end_date="2024-03-31")
        search(start_date="2024-01-01", end_date="2024-03-31", min_class="X")
    """
    events = load_data()

    if not events:
        print("No data yet! Run scraper.py first.")
        return []

    if start_date:
        events = [e for e in events if e["start_time"][:10] >= start_date]

    if end_date:
        events = [e for e in events if e["start_time"][:10] <= end_date]

    if min_class:
        min_val = CLASS_ORDER.get(min_class[0].upper(), 0)
        events  = [e for e in events if e["class"] and CLASS_ORDER.get(e["class"][0].upper(), -1) >= min_val]

    print(f"\nFound {len(events)} flares\n")
    print(f"{'Start':<20} {'Peak':<20} {'End':<20} {'Class':<8} {'Region'}")
    print("-" * 76)
    for e in events[:50]:
        print(f"{e['start_time']:<20} {e['peak_time']:<20} {e['end_time']:<20} {e['class']:<8} {e['active_region']}")
    if len(events) > 50:
        print(f"\n... and {len(events) - 50} more. Open solar_events.csv to see all.")

    return events


def stats():
    """Print a summary of all your saved data."""
    events = load_data()
    if not events:
        print("No data yet! Run scraper.py first.")
        return

    dates        = [e["start_time"][:10] for e in events]
    class_counts = {}
    for e in events:
        letter = e["class"][0] if e["class"] else "?"
        class_counts[letter] = class_counts.get(letter, 0) + 1

    print(f"\n{'='*30}")
    print(f"  Total flares : {len(events)}")
    print(f"  From         : {min(dates)}")
    print(f"  To           : {max(dates)}")
    print(f"\n  Breakdown by class:")
    for letter in ["A", "B", "C", "M", "X"]:
        count = class_counts.get(letter, 0)
        bar   = "█" * (count // 10)
        print(f"    {letter}: {count:>5}  {bar}")
    print(f"{'='*30}\n")


if __name__ == "__main__":
    # Run this file directly to see your data
    stats()
    print("--- M class and above ---")
    search(min_class="M")