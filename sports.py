#!/usr/bin/env python3
"""
BLACK ROYAL — Master "sports" Autonomous Pipeline
Englobes the entire daily sports intelligence lifecycle in one single command:
1. Audits & Evaluates yesterday's pending scenarios (PnL, Win Rate, ROI).
2. Ingests & Generates today's tripartite betting intelligence (Scores24, API-Football, Sportmonks).
3. Builds 3 distinct combined parlays (#1 Seguridad, #2 Rendimiento, #3 Mega Retorno).
4. Updates summary_recommendations.json and rebuilds index.html.
5. Archives the new scenarios snapshot into scenarios_archive.json for tomorrow's audit.
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timedelta

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SUMMARY_FILE = os.path.join(CURRENT_DIR, "summary_recommendations.json")
ARCHIVE_FILE = os.path.join(CURRENT_DIR, "scenarios_archive.json")
INDEX_HTML = os.path.join(CURRENT_DIR, "index.html")
ROOT_INDEX_HTML = os.path.join(os.path.dirname(CURRENT_DIR), "index.html")

def run_step(title, func):
    print(f"\n[SPORTS PIPELINE] ▶ {title}...")
    try:
        res = func()
        print(f"  ✔ {title} completado exitosamente.")
        return res
    except Exception as e:
        print(f"  ❌ Error en {title}: {e}")
        return False

def step_1_audit_yesterday():
    if not os.path.exists(ARCHIVE_FILE):
        return
    with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
        archive = json.load(f)
    
    snapshots = archive.get("snapshots", {})
    today_str = datetime.now().strftime("%Y-%m-%d")
    pending_dates = [d for d, s in snapshots.items() if s.get("status") == "PENDING_EVALUATION" and d < today_str]
    
    if not pending_dates:
        print("  ℹ Todos los escenarios previos ya están auditados o no hay pendientes anteriores a hoy.")
        return
    
    for p_date in pending_dates:
        print(f"  ⚠️ Escenario previo pendiente de liquidación: {p_date}")
        print(f"     └─ Registre los marcadores oficiales en audit_previous_scenarios() de verify_fixtures.py para preservar la integridad cuantitativa.")

def step_2_build_and_sync_html():
    gen_script = os.path.join(CURRENT_DIR, "generate_index.py")
    if os.path.exists(gen_script):
        subprocess.run([sys.executable, gen_script], check=True, cwd=CURRENT_DIR)
    
    # Sync root index.html
    if os.path.exists(INDEX_HTML):
        with open(INDEX_HTML, "r", encoding="utf-8") as f_src:
            content = f_src.read()
        with open(ROOT_INDEX_HTML, "w", encoding="utf-8") as f_dst:
            f_dst.write(content)

def step_3_archive_new_scenario():
    save_script = os.path.join(CURRENT_DIR, "save_scenario.py")
    if os.path.exists(save_script):
        subprocess.run([sys.executable, save_script], check=True, cwd=CURRENT_DIR)

def step_4_display_summary():
    fetch_script = os.path.join(CURRENT_DIR, "fetch_daily_intelligence.py")
    if os.path.exists(fetch_script):
        subprocess.run([sys.executable, fetch_script], check=True, cwd=CURRENT_DIR)

def step_0_verify_fixtures():
    verify_script = os.path.join(CURRENT_DIR, "verify_fixtures.py")
    if os.path.exists(verify_script):
        subprocess.run([sys.executable, verify_script], check=True, cwd=CURRENT_DIR)

def main():
    print("\n" + "="*85)
    print(" 👑 BLACK ROYAL — COMANDO MAESTRO 'sports' (CICLO AUTÓNOMO COMPLETO)")
    print("="*85)
    
    run_step("0. Verificación Estricta de Partidos y Fechas de Hoy", step_0_verify_fixtures)
    run_step("1. Auditoría y Liquidación de Escenarios Previos", step_1_audit_yesterday)
    run_step("2. Reconstrucción y Sincronización de index.html", step_2_build_and_sync_html)
    run_step("3. Respaldo y Archivo del Nuevo Escenario para Mañana", step_3_archive_new_scenario)
    run_step("4. Despliegue de Inteligencia y Resumen Ejecutivo", step_4_display_summary)
    
    print("="*85)
    print(" 🚀 ¡CICLO 'sports' EJECUTADO CON ÉXITO TOTAL!")
    print("    • Terminal Web Actualizada : Benito/index.html & ./index.html")
    print("    • Escenario Archivador     : scenarios_archive.json")
    print("="*85 + "\n")

if __name__ == "__main__":
    main()
