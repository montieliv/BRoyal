import urllib.request
import re
import json

url = 'https://scores24.live/es/predictions/soccer/today'
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
)

print(f"📡 Conectando a {url}...")
with urllib.request.urlopen(req) as response:
    html = response.read().decode('utf-8')

match = re.search(r'window\.URQL_DATA=JSON\.parse\("(.*?)"\);', html)
if not match:
    print("❌ No se encontró URQL_DATA")
    exit(1)

escaped = match.group(1)
data = json.loads(json.loads(f'"{escaped}"'))

items = []
for k, v in data.items():
    data_inner = json.loads(v["data"])
    for qkey, qval in data_inner.items():
        if isinstance(qval, list):
            items.extend(qval)
        elif isinstance(qval, dict):
            for subk, subval in qval.items():
                if isinstance(subval, list):
                    items.extend(subval)

print(f"✅ Total items extraídos de GraphQL: {len(items)}")

# Print keys of items
for i, item in enumerate(items[:5]):
    if isinstance(item, dict):
        print(f"\nItem {i} Keys: {list(item.keys())}")
        print("Preview:", json.dumps(item, ensure_ascii=False)[:300])

# Parse matches based on keys found
matches = []
for item in items:
    if isinstance(item, dict):
        # Look for team names or match info inside
        item_str = json.dumps(item, ensure_ascii=False)
        name = item.get("name") or item.get("title")
        slug = item.get("slug")
        if "vs" in str(name).lower() or "vs" in str(slug).lower() or "teams" in item_str.lower():
            matches.append(item)

print(f"\n⚽ Total de objetos con partidos identificados: {len(matches)}")
with open('today_raw_extracted.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print("💾 Guardado en 'today_raw_extracted.json'")
