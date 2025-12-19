import json
import requests
from bs4 import BeautifulSoup

print("HELLO FROM ACTIONS - SCRIPT STARTED")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

VENDOR_KEYWORDS = ["bt-miners", "bt miners", "bt-miners.com"]

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

urls = config["urls"]
top_n = config.get("top_n", 3)

def normalize(text):
    return text.lower().strip()

print("=" * 80)
print("ASICMinerValue BT-MINERS Rank Check (Recommended)")
print("=" * 80)

alert_list = []

for url in urls:
    print(f"\nChecking: {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=25)
        print(f"HTTP status: {resp.status_code}")
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ REQUEST ERROR: {e}")
        alert_list.append((url, "REQUEST ERROR"))
        continue

    soup = BeautifulSoup(resp.text, "html.parser")

    rows = soup.select("table tbody tr")
    print(f"Found {len(rows)} vendor rows")

    vendors = []
    for r in rows:
        tds = r.find_all("td")
        if tds:
            vendors.append(tds[0].get_text(strip=True))

    if not vendors:
        print("❌ NO VENDOR TABLE FOUND")
        alert_list.append((url, "NO DATA"))
        continue

    bt_rank = None
    for i, v in enumerate(vendors, start=1):
        if any(k in normalize(v) for k in VENDOR_KEYWORDS):
            bt_rank = i
            break

    top3 = vendors[:3]

    if bt_rank is None:
        print(f"❌ BT-MINERS: MISSING | Top3: {top3}")
        alert_list.append((url, "MISSING"))
    elif bt_rank > top_n:
        print(f"❌ BT-MINERS rank #{bt_rank} | Top3: {top3}")
        alert_list.append((url, f"#{bt_rank}"))
    else:
        print(f"✅ BT-MINERS rank #{bt_rank} | Top3: {top3}")

print("\n" + "=" * 80)
print("ALERT SUMMARY")
print("=" * 80)

if not alert_list:
    print("🎉 All models are within Top 3")
else:
    for url, reason in alert_list:
        print(f"ALERT: {url} -> {reason}")
