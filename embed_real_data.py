import json
from bs4 import BeautifulSoup

with open('today_real_matches_parsed.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

# Let's inspect the html file and update the JS matches array
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Create a clean JavaScript array of matches
js_matches_str = json.dumps(matches, ensure_ascii=False, indent=2)

# Insert script tag before </body>
script_injection = f"""
  <script>
    // INGESTA REAL EN VIVO SCORES24 BETA (71 PARTIDOS DE HOY)
    window.SCORES24_TODAY_MATCHES = {js_matches_str};
    console.log("⚡ Ingesta de hoy de Scores24 cargada:", window.SCORES24_TODAY_MATCHES.length, "partidos.");
  </script>
</body>
"""

if 'window.SCORES24_TODAY_MATCHES =' in html:
    # Replace existing injection
    import re
    html = re.sub(r'<script>\s*// INGESTA REAL EN VIVO SCORES24.*?</script>\s*</body>', script_injection, html, flags=re.DOTALL)
else:
    html = html.replace('</body>', script_injection)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ ¡INDEX.HTML ACTUALIZADO CON LOS {len(matches)} PARTIDOS REALES DE HOY DESDE SCORES24!")
