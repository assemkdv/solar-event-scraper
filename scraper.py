import requests
from bs4 import BeautifulSoup

url = "https://www.lmsal.com/solarsoft/latest_events/"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

links = []

for a in soup.find_all("a"):
    href = a.get("href")
    
    if href and "gev_" in href:
        links.append(href)

print(links[:5])

def parse_event_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")

    rows = table.find_all("tr")

    events = []

    for row in rows[1:]:  # skip header row
        cols = row.find_all("td")

        if len(cols) < 7:
            continue

        event = {
            "event_number": cols[0].text.strip(),
            "name": cols[1].text.strip(),
            "start": cols[2].text.strip(),
            "stop": cols[3].text.strip(),
            "peak": cols[4].text.strip(),
            "class": cols[5].text.strip(),
            "location": cols[6].text.strip(),
        }

        events.append(event)

    return events

link = links[0]
events = parse_event_page(link)

print(events)

all_events = []

for link in links[:5]:   # just 5 for now (testing)
    events = parse_event_page(link)
    all_events.extend(events)

print(all_events)

def remove_duplicates(events):
    seen = set()
    unique = []

    for e in events:
        key = (e["start"], e["peak"], e["class"])

        if key not in seen:
            seen.add(key)
            unique.append(e)

    return unique

clean_events = remove_duplicates(all_events)

print(clean_events)

import pandas as pd

df = pd.DataFrame(clean_events)
df.to_csv("solar_events.csv", index=False)

print("Saved to solar_events.csv")