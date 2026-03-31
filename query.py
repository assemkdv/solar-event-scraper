import pandas as pd

# load your data
df = pd.read_csv("solar_events.csv")

# 🔍 filter by class (C, M, X)
def filter_by_class(letter):
    return df[df["class"].str.startswith(letter)]

# 🔍 filter by date range
def filter_by_date(start, end):
    df["start"] = pd.to_datetime(df["start"], format="%Y/%m/%d %H:%M:%S")
    return df[(df["start"] >= start) & (df["start"] <= end)]


# TESTS
print("C-class events:")
print(filter_by_class("C"))

print("\nEvents on March 26:")
print(filter_by_date("2026-03-26 00:00:00", "2026-03-26 23:59:59"))
print(f"Total events in dataset: {len(df)}")