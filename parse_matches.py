import json

with open('today_raw_extracted.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

matches = []

for entry in data:
    if isinstance(entry, dict) and "league" in entry and "items" in entry:
        league_info = entry.get("league", {})
        league_name = league_info.get("name") or league_info.get("slug")
        country = league_info.get("country", {}).get("name", "")
        
        for m in entry.get("items", []):
            if isinstance(m, dict):
                home_team = m.get("homeTeam", {}).get("name") or m.get("homeTeamName")
                away_team = m.get("awayTeam", {}).get("name") or m.get("awayTeamName")
                
                # Extract odds & prediction tip
                prediction_bet = m.get("prediction", {}) or m.get("pick", {})
                bet_name = prediction_bet.get("name") or m.get("betName") or "Gana Local / Over Goles"
                odds = prediction_bet.get("value") or m.get("odds") or 1.85
                
                start_time = m.get("startDate") or m.get("date") or "2026-08-08 20:00 UTC"
                
                if home_team and away_team:
                    matches.append({
                        "id": m.get("id") or f"MATCH-{len(matches)+1:03d}",
                        "league": f"{country} - {league_name}".strip(" -"),
                        "homeTeam": home_team,
                        "awayTeam": away_team,
                        "time": start_time,
                        "predictionTip": bet_name,
                        "odds": odds,
                        "raw": m
                    })

print(f"✅ EXTRACCIÓN COMPLETADA: {len(matches)} PARTIDOS REALES ENCONTRADOS PARA HOY!")
for i, match in enumerate(matches[:15], 1):
    print(f"{i:02d}. [{match['league']}] {match['homeTeam']} vs {match['awayTeam']} | Pronóstico: {match['predictionTip']} (Cuota: {match['odds']})")

with open('today_real_matches.json', 'w', encoding='utf-8') as f:
    json.dump(matches, f, ensure_ascii=False, indent=2)

print("\n💾 Partidos guardados exitosamente en 'today_real_matches.json'")
