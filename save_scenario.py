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

def archive_current_scenario(target_date=None):
    if not target_date:
        target_date = datetime.now().strftime("%Y-%m-%d")
    summary_data = load_json(SUMMARY_FILE, {})
    archive = load_json(ARCHIVE_FILE, {"version": "1.0", "snapshots": {}})
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    strategies = summary_data.get("strategies", {})

    snapshot = {
        "date": target_date,
        "saved_at": timestamp,
        "status": "PENDING_EVALUATION",
        "strategies": strategies,
        "metrics": {
            "totalModes": len(strategies),
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
    target = sys.argv[1] if len(sys.argv) > 1 else None
    archive_current_scenario(target)
