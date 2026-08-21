#!/usr/bin/env python3
"""
BLACK ROYAL — Scenario Archiver for Modo A, Modo B, and Modo C
"""

import json
import os
import sys
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SUMMARY_FILE = os.path.join(CURRENT_DIR, "summary_recommendations.json")
ARCHIVE_FILE = os.path.join(CURRENT_DIR, "scenarios_archive.json")

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error reading {filepath}: {e}")
    return default

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def archive_current_scenario(target_date="2026-08-20"):
    summary_data = load_json(SUMMARY_FILE, {})
    archive = load_json(ARCHIVE_FILE, {"version": "1.0", "snapshots": {}})
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    strategies = summary_data.get("strategies", {})

    snapshot = {
        "date": target_date,
        "saved_at": timestamp,
        "status": "PENDING_EVALUATION",
        "strategies": {
            "modo_a_simples": {
                "name": "Modo A: Apuestas Simples de Valor (75% Win Rate)",
                "expectedWinRate": "75.0%",
                "simulatedStakeTotal": 300.0, # $100 per pick
                "status": "PENDING",
                "picks": strategies.get("modo_a_simples", {}).get("picks", [])
            },
            "modo_b_sistema": {
                "name": "Modo B: Sistema 2/3 Trixie (Seguro 1 Fallo)",
                "expectedWinRate": "85.0%",
                "simulatedStakeTotal": 100.0, # 4 bets of $25
                "status": "PENDING",
                "picks": strategies.get("modo_b_sistema", {}).get("picks", [])
            },
            "modo_c_banker": {
                "name": "Modo C: Doble Banker (Duplicador @ 2.18x)",
                "expectedWinRate": "76.5%",
                "totalOdds": 2.18,
                "simulatedStakeTotal": 100.0,
                "status": "PENDING",
                "picks": strategies.get("modo_c_banker", {}).get("picks", [])
            }
        },
        "metrics": {
            "totalModes": 3,
            "simulatedTotalStake": 500.0,
            "evaluated": False,
            "netPnL": 0.0,
            "roiPct": "0.0%"
        }
    }

    archive["snapshots"][target_date] = snapshot
    save_json(ARCHIVE_FILE, archive)
    
    print("\n" + "="*85)
    print(f" 💾 ¡ESCENARIO GUARDADO CON ÉXITO PARA EVALUACIÓN POSTERIOR!")
    print(f"    Fecha de Registro: {target_date} ({timestamp})")
    print(f"    Archivo Destino  : scenarios_archive.json")
    print("="*85)
    print(f"  • Estrategias Activas : Modo A (Simples), Modo B (Sistema 2/3), Modo C (Doble Banker)")
    print(f"  • Tasa Éxito Esperada : 75% – 85% Win Rate")
    print("="*85 + "\n")
    return True

if __name__ == "__main__":
    archive_current_scenario("2026-08-20")
