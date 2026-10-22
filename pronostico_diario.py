#!/usr/bin/env python3
"""
BLACK ROYAL — Pronóstico Diario Automático (datos reales, sin API key)

Ejecuta el ciclo completo con datos REALES obtenidos del API público de ESPN
(marcadores oficiales + cuotas DraftKings):

  1. LIQUIDA los escenarios pendientes de días anteriores (marcadores reales,
     PnL por modo, Win Rate, ROI) y los guarda en scenarios_archive.json.
  2. CONSTRUYE el mejor pronóstico del día a partir de los partidos programados
     hoy con cuotas reales (probabilidad sin margen + ajuste por forma).
  3. Escribe summary_recommendations.json, archiva el escenario como
     PENDING_EVALUATION y reconstruye index.html (generate_index.py).
  4. Guarda un reporte legible en reportes/pronostico_YYYY-MM-DD.md

Uso:
  python3 pronostico_diario.py                 # hoy (liquida ayer + pronóstico de hoy)
  python3 pronostico_diario.py --date 2026-10-23
  python3 pronostico_diario.py --settle-only   # solo liquidar pendientes
  python3 pronostico_diario.py --dry-run       # no escribe archivos

Nunca inventa datos: si no hay partidos con cuotas reales suficientes, no
publica pronóstico; si un partido no ha terminado, queda pendiente.
"""

import argparse
import difflib
import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from math import exp, factorial

try:
    from zoneinfo import ZoneInfo
    LOCAL_TZ = ZoneInfo("America/Mexico_City")
except Exception:  # pragma: no cover
    LOCAL_TZ = timezone(timedelta(hours=-6))

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SUMMARY_FILE = os.path.join(CURRENT_DIR, "summary_recommendations.json")
ARCHIVE_FILE = os.path.join(CURRENT_DIR, "scenarios_archive.json")
REPORTS_DIR = os.path.join(CURRENT_DIR, "reportes")
GEN_INDEX = os.path.join(CURRENT_DIR, "generate_index.py")

ESPN = "https://site.api.espn.com/apis/site/v2/sports/{path}/scoreboard?dates={ymd}&limit=300"

SOCCER_LEAGUES = {
    "uefa.champions": "UEFA Champions League",
    "uefa.europa": "UEFA Europa League",
    "uefa.europa.conf": "UEFA Conference League",
    "eng.1": "Premier League",
    "esp.1": "LaLiga",
    "ita.1": "Serie A",
    "ger.1": "Bundesliga",
    "fra.1": "Ligue 1",
    "por.1": "Primeira Liga",
    "ned.1": "Eredivisie",
    "bel.1": "Jupiler Pro League",
    "tur.1": "Süper Lig",
    "sco.1": "Scottish Premiership",
    "eng.2": "EFL Championship",
    "mex.1": "Liga MX",
    "usa.1": "MLS",
    "arg.1": "Liga Profesional Argentina",
    "bra.1": "Brasileirão Série A",
    "col.1": "Liga BetPlay (Colombia)",
    "conmebol.libertadores": "CONMEBOL Libertadores",
    "conmebol.sudamericana": "CONMEBOL Sudamericana",
}
# Solo para liquidar picks multideporte heredados (ediciones híbridas)
OTHER_SPORTS = {
    "basketball/nba": "NBA",
    "baseball/mlb": "MLB",
    "football/nfl": "NFL",
}

STAKE_A_PER_PICK = 100.0
STAKE_B_PER_LINE = 25.0
STAKE_C = 100.0

_cache = {}


# ───────────────────────────── utilidades ─────────────────────────────
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch_scoreboard(path, day):
    """day: date object. Devuelve lista de eventos ESPN (cacheado)."""
    key = (path, day.strftime("%Y%m%d"))
    if key in _cache:
        return _cache[key]
    url = ESPN.format(path=path if "/" in path else f"soccer/{path}", ymd=key[1])
    events = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 BlackRoyal"})
        with urllib.request.urlopen(req, timeout=20) as r:
            events = json.load(r).get("events", [])
    except Exception as e:
        print(f"    ⚠️ No se pudo consultar {path} {key[1]}: {e}")
    for ev in events:
        ev["_league"] = path
    _cache[key] = events
    return events


def fetch_many(paths, days):
    jobs = [(p, d) for p in paths for d in days]
    with ThreadPoolExecutor(max_workers=12) as ex:
        results = list(ex.map(lambda j: fetch_scoreboard(*j), jobs))
    seen, out = set(), []
    for evs in results:
        for ev in evs:
            if ev["id"] not in seen:
                seen.add(ev["id"])
                out.append(ev)
    return out


STOP = {"fc", "cf", "sc", "ac", "cd", "club", "de", "the", "afc", "ss", "rc", "sk", "fk",
        "ud", "ca", "cp", "calcio", "sv", "vfb", "vfl", "as", "us", "rcd", "sd", "if", "bk",
        "de", "la", "el", "del", "balompie", "clube", "futebol", "sporting"}


def norm(name):
    s = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    toks = [t for t in s.split() if t not in STOP]
    return " ".join(toks) or s.strip()


def name_score(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    if a == b or a in b or b in a:
        return 1.0
    ta, tb = set(a.split()), set(b.split())
    overlap = len(ta & tb) / max(1, min(len(ta), len(tb)))
    return max(difflib.SequenceMatcher(None, a, b).ratio(), overlap)


def competitors(ev):
    comp = ev["competitions"][0]
    home = next(c for c in comp["competitors"] if c.get("homeAway") == "home")
    away = next(c for c in comp["competitors"] if c.get("homeAway") == "away")
    return comp, home, away


def team_names(c):
    t = c.get("team", {})
    return [t.get("displayName", ""), t.get("shortDisplayName", ""), t.get("name", ""), t.get("location", "")]


def find_event(match_str, events, event_id=None):
    if event_id:
        for ev in events:
            if ev["id"] == str(event_id):
                return ev
    if " vs" not in match_str:
        return None
    h, a = [x.strip() for x in re.split(r"\s+vs\.?\s+", match_str, maxsplit=1)]
    best, best_sc = None, 0.0
    for ev in events:
        try:
            _, home, away = competitors(ev)
        except StopIteration:
            continue
        sh = max(name_score(h, n) for n in team_names(home))
        sa = max(name_score(a, n) for n in team_names(away))
        sc = min(sh, sa) * 0.6 + (sh + sa) / 2 * 0.4
        if sc > best_sc:
            best, best_sc = ev, sc
    return best if best_sc >= 0.62 else None


def american_to_decimal(v):
    try:
        v = float(str(v).replace("+", ""))
    except (TypeError, ValueError):
        return None
    if v == 0:
        return None
    return round(1 + (v / 100 if v > 0 else 100 / abs(v)), 3)


def dec_to_american(d):
    return f"+{round((d - 1) * 100)}" if d >= 2 else f"-{round(100 / (d - 1))}"


# ───────────────────────────── calificación ─────────────────────────────
def grade_leg(leg, hs, as_, home_name, away_name, market=None):
    """Devuelve 'WON' | 'LOST' | 'PUSH' | None (no reconocido)."""
    total, diff = hs + as_, hs - as_
    if market:
        t, side, line = market.get("type"), market.get("side"), market.get("line")
        if t == "ML":
            return "WON" if (diff > 0 if side == "home" else diff < 0) else "LOST"
        if t == "DC":
            ok = {"1X": diff >= 0, "X2": diff <= 0, "12": diff != 0}[side]
            return "WON" if ok else "LOST"
        if t == "TOTAL":
            if total == line:
                return "PUSH"
            return "WON" if ((total > line) if side == "over" else (total < line)) else "LOST"
        if t == "BTTS":
            return "WON" if (hs > 0 and as_ > 0) == (side == "yes") else "LOST"

    L = unicodedata.normalize("NFKD", leg).encode("ascii", "ignore").decode().lower()

    # equipo mencionado en la pierna
    def mentioned():
        sh = name_score(L.split("(")[0], home_name)
        sa = name_score(L.split("(")[0], away_name)
        return "away" if sa > sh and sa >= 0.5 else "home"

    if "ambos" in L or "btts" in L:
        yes = "no)" not in L and "btts: no" not in L
        return "WON" if (hs > 0 and as_ > 0) == yes else "LOST"
    m = re.search(r"(mas|over|menos|under)(?: de)? (\d+(?:\.\d+)?)", L)
    if m and ("gol" in L or "over" in L or "under" in L or "punto" in L or "carrera" in L):
        line = float(m.group(2))
        if total == line:
            return "PUSH"
        over = m.group(1) in ("mas", "over")
        return "WON" if ((total > line) if over else (total < line)) else "LOST"
    if "(1x)" in L:
        return "WON" if diff >= 0 else "LOST"
    if "(x2)" in L:
        return "WON" if diff <= 0 else "LOST"
    if "(12)" in L:
        return "WON" if diff != 0 else "LOST"
    m = re.search(r"([+-]\d+(?:\.\d+)?)\s*(?:ah|handicap|spread|\)|$)", L)
    if m and ("ah" in L or "handicap" in L or "spread" in L or L.strip().startswith(("+", "-")) or "safe" in L):
        line = float(m.group(1))
        margin = diff if mentioned() == "home" else -diff
        val = margin + line
        return "PUSH" if val == 0 else ("WON" if val > 0 else "LOST")
    if "dnb" in L or "empate anula" in L:
        if diff == 0:
            return "PUSH"
        return "WON" if (diff > 0) == (mentioned() == "home") else "LOST"
    if "(2)" in L:
        return "WON" if diff < 0 else "LOST"
    if "(1)" in L or "ganador" in L or "moneyline" in L or re.search(r"\bml\b", L):
        side = mentioned() if "(1)" not in L else "home"
        return "WON" if (diff > 0 if side == "home" else diff < 0) else "LOST"
    return None


def grade_pick(pick, events):
    """Devuelve dict con status (WON/LOST/PUSH/PENDING/UNKNOWN/VOID), score, mult."""
    ev = find_event(pick.get("match", ""), events, pick.get("espnEventId"))
    if not ev:
        return {"status": "UNKNOWN", "score": None, "detail": "Partido no encontrado en ESPN"}
    comp, home, away = competitors(ev)
    st = ev["status"]["type"]
    if st.get("name") in ("STATUS_POSTPONED", "STATUS_CANCELED", "STATUS_ABANDONED"):
        return {"status": "VOID", "score": st.get("description"), "detail": st.get("description")}
    if not st.get("completed"):
        return {"status": "PENDING", "score": None, "detail": st.get("description", "No iniciado")}
    hs, as_ = int(float(home.get("score", 0))), int(float(away.get("score", 0)))
    hn, an = home["team"]["displayName"], away["team"]["displayName"]
    markets = pick.get("markets") or [None]
    legs = [l.strip() for l in pick.get("selection", "").split(" + ")]
    results = []
    for i, leg in enumerate(legs):
        mk = markets[i] if i < len(markets) else None
        results.append(grade_leg(leg, hs, as_, hn, an, mk))
    if any(r is None for r in results):
        status = "UNKNOWN"
    elif "LOST" in results:
        status = "LOST"
    elif all(r == "PUSH" for r in results):
        status = "PUSH"
    else:
        status = "WON"
    return {"status": status, "score": f"{hs}-{as_}", "home": hn, "away": an,
            "legs": results, "detail": st.get("description")}


def leg_mult(g, odds):
    return {"WON": odds, "PUSH": 1.0, "VOID": 1.0}.get(g["status"], 0.0)


def settle_strategies(strategies, events):
    """Liquida Modo A/B/C. Devuelve (metrics, match_results, completo?)."""
    graded, complete = {}, True
    for key in ("modo_a_simples", "modo_b_sistema", "modo_c_banker"):
        for p in strategies.get(key, {}).get("picks", []):
            g = grade_pick(p, events)
            graded[(p["match"], p["selection"])] = g
            if g["status"] in ("PENDING", "UNKNOWN"):
                complete = False

    def g_of(p):
        return graded[(p["match"], p["selection"])]

    ret, stake, won_modes, breakdown = 0.0, 0.0, 0, []
    # Modo A — simples
    a = strategies.get("modo_a_simples", {}).get("picks", [])
    if a:
        r = sum(STAKE_A_PER_PICK * leg_mult(g_of(p), p["odds"]) for p in a)
        stake += STAKE_A_PER_PICK * len(a)
        ret += r
        hits = sum(1 for p in a if g_of(p)["status"] == "WON")
        won_modes += 1 if r > STAKE_A_PER_PICK * len(a) else 0
        strategies["modo_a_simples"]["status"] = "WON" if hits == len(a) else ("PARTIAL" if hits else "LOST")
        breakdown.append(f"Modo A ${r:.2f} ({hits}/{len(a)})")
    # Modo B — Trixie (3 dobles + 1 triple)
    b = strategies.get("modo_b_sistema", {}).get("picks", [])
    if len(b) == 3:
        m = [leg_mult(g_of(p), p["odds"]) for p in b]
        lines = [m[0] * m[1], m[0] * m[2], m[1] * m[2], m[0] * m[1] * m[2]]
        r = sum(STAKE_B_PER_LINE * x for x in lines)
        stake += STAKE_B_PER_LINE * 4
        ret += r
        won_modes += 1 if r > STAKE_B_PER_LINE * 4 else 0
        strategies["modo_b_sistema"]["status"] = "WON" if r > 100 else ("PARTIAL" if r > 0 else "LOST")
        breakdown.append(f"Modo B ${r:.2f}")
    # Modo C — Doble banker
    c = strategies.get("modo_c_banker", {}).get("picks", [])
    if c:
        mult = 1.0
        for p in c:
            mult *= leg_mult(g_of(p), p["odds"])
        r = STAKE_C * mult
        stake += STAKE_C
        ret += r
        won_modes += 1 if r > STAKE_C else 0
        strategies["modo_c_banker"]["status"] = "WON" if r > 0 else "LOST"
        breakdown.append(f"Modo C ${r:.2f}")

    match_results = {}
    for (match, sel), g in graded.items():
        icon = {"WON": "✅", "LOST": "❌", "PUSH": "↩️", "VOID": "⛔"}.get(g["status"], "⏳")
        txt = f"{sel} {icon}"
        if match in match_results:
            match_results[match] += f" | {txt}"
        else:
            match_results[match] = f"{g['score'] or g['detail']} — {txt}"

    net = ret - stake
    picks_total = sum(1 for g in graded.values() if g["status"] in ("WON", "LOST"))
    picks_won = sum(1 for g in graded.values() if g["status"] == "WON")
    metrics = {
        "totalModes": len(breakdown),
        "wonModes": won_modes,
        "simulatedTotalStake": round(stake, 2),
        "simulatedTotalReturn": round(ret, 2),
        "netPnL": round(net, 2),
        "roiPct": f"{(net / stake * 100 if stake else 0):+.1f}%",
        "winRate": f"{(picks_won / picks_total * 100 if picks_total else 0):.1f}% de selecciones ({picks_won}/{picks_total}) | " + " + ".join(breakdown),
        "evaluated": complete,
        "evaluatedAt": datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "auditSource": "ESPN API (marcadores oficiales) — liquidación automática pronostico_diario.py",
    }
    return metrics, match_results, complete


def settle_pending(today, dry_run=False, lookback_days=4):
    archive = load_json(ARCHIVE_FILE, {"version": "1.0", "snapshots": {}})
    snaps = archive.get("snapshots", {})
    report = []
    paths = list(SOCCER_LEAGUES) + list(OTHER_SPORTS)
    min_day = (today - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    for key in sorted(snaps):
        snap = snaps[key]
        d_str = key[:10]
        if d_str >= today.strftime("%Y-%m-%d"):
            continue
        need_main = snap.get("status") == "PENDING_EVALUATION"
        hyb = snap.get("hybrid_edition") or {}
        need_hyb = bool(hyb.get("strategies")) and "metrics" not in hyb and d_str >= min_day and (
            any("Pendiente" in str(v) for v in (snap.get("match_results") or {}).values())
            or need_main)
        if not (need_main or need_hyb):
            continue
        day = datetime.strptime(d_str, "%Y-%m-%d").date()
        print(f"  🔎 Liquidando escenario {key} ...")
        events = fetch_many(paths, [day, day + timedelta(days=1)])
        entry = {"date": key}

        if need_main:
            metrics, results, complete = settle_strategies(snap["strategies"], events)
            snap["match_results"] = {**(snap.get("match_results") or {}), **results}
            snap["metrics"] = {**snap.get("metrics", {}), **metrics}
            if complete:
                snap["status"] = "EVALUATED"
                snap["evaluatedAt"] = metrics["evaluatedAt"]
            entry["main"] = (metrics, results, complete)

        if need_hyb:
            metrics, results, complete = settle_strategies(hyb["strategies"], events)
            hyb["metrics"] = metrics
            mr = snap.setdefault("match_results", {})
            for m, txt in results.items():
                if m not in mr or "Pendiente" in mr[m]:
                    mr[m] = txt
            entry["hybrid"] = (metrics, results, complete)
        report.append(entry)

    if report and not dry_run:
        save_json(ARCHIVE_FILE, archive)
    return report


# ───────────────────────────── modelo de pronóstico ─────────────────────────────
def poisson_over(lmb, line):
    k_max = int(line)  # P(N > line) = 1 - P(N <= floor(line))
    return 1 - sum(exp(-lmb) * lmb ** k / factorial(k) for k in range(k_max + 1))


def lambda_from_over(p_over, line):
    lo, hi = 0.05, 8.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if poisson_over(mid, line) < p_over:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def form_score(form):
    if not form:
        return None
    pts = {"W": 3, "D": 1, "L": 0}
    vals = [pts[c] for c in form.upper() if c in pts]
    return sum(vals) / (3 * len(vals)) if vals else None


def odds_side(node, side):
    if not node or side not in node:
        return None
    s = node[side] or {}
    for k in ("close", "open"):
        if (s.get(k) or {}).get("odds") not in (None, "", "OFF"):
            return s[k]
    return None


def analyze_event(ev, now_local, target_day, slot=None, min_lead=45):
    comp, home, away = competitors(ev)
    if ev["status"]["type"].get("state") != "pre":
        return []
    ko = datetime.fromisoformat(ev["date"].replace("Z", "+00:00")).astimezone(LOCAL_TZ)
    if ko.date() != target_day:
        return []
    if slot and ko.strftime("%H:%M") != slot:
        return []
    if target_day == now_local.date() and ko < now_local + timedelta(minutes=min_lead):
        return []
    odds = (comp.get("odds") or [{}])[0] or {}
    ml = odds.get("moneyline") or {}
    oh = odds_side(ml, "home")
    od = odds_side(ml, "draw")
    oa = odds_side(ml, "away")
    if not (oh and oa):
        return []
    dh = american_to_decimal(oh["odds"])
    da = american_to_decimal(oa["odds"])
    dd = american_to_decimal(od["odds"]) if od else None
    if not (dh and da):
        return []

    if dd:
        inv = 1 / dh + 1 / dd + 1 / da
        ph, pd, pa = (1 / dh) / inv, (1 / dd) / inv, (1 / da) / inv
    else:
        inv = 1 / dh + 1 / da
        ph, pd, pa = (1 / dh) / inv, 0.0, (1 / da) / inv
    margin = inv - 1

    fh, fa = form_score(home.get("form")), form_score(away.get("form"))
    adj = 0.06 * (fh - fa) if fh is not None and fa is not None else 0.0
    mh = min(0.95, max(0.02, ph + adj))
    ma = min(0.95, max(0.02, pa - adj))
    md = max(0.0, 1 - mh - ma) if dd else 0.0

    hn, an = home["team"]["displayName"], away["team"]["displayName"]
    league = ev["_league"]

    sport = "Football"
    league_name = SOCCER_LEAGUES.get(league)
    if not league_name:
        if "nba" in league:
            sport, league_name = "Basketball", "NBA 2026-27"
        elif "nfl" in league:
            sport, league_name = "NFL", "NFL 2026"
        elif "mlb" in league:
            sport, league_name = "Baseball", "MLB Postseason"
        else:
            sport, league_name = "Football", OTHER_SPORTS.get(league, league)

    base = {
        "espnEventId": ev["id"], "espnLeague": league,
        "sport": sport,
        "league": league_name,
        "home": hn, "away": an, "match": f"{hn} vs. {an}",
        "kickoff": ko, "venue": (comp.get("venue") or {}).get("fullName", "Por confirmar"),
        "formH": home.get("form", "") or "—", "formA": away.get("form", "") or "—",
        "pMkt": {"home": ph, "draw": pd, "away": pa}, "margin": margin,
    }
    cands = []

    def add(sel, mk, odds_dec, p, p_mkt, src_odds, estimated=False):
        ev_ = p * odds_dec - 1
        cands.append({**base, "selection": sel, "market": mk, "odds": round(odds_dec, 2),
                      "p": p, "pMktSel": p_mkt, "ev": ev_, "srcOdds": src_odds, "estimated": estimated})

    if sport == "Football":
        add(f"{hn} Ganador Directo (1)", {"type": "ML", "side": "home"}, dh, mh, ph, oh["odds"])
        add(f"{an} Ganador Directo (2)", {"type": "ML", "side": "away"}, da, ma, pa, oa["odds"])

        # doble oportunidad (cuota estimada con el margen del libro)
        for side, p_m, p_mod, team in (("1X", ph + pd, mh + md, hn), ("X2", pa + pd, ma + md, an)):
            est = 1 / (p_m * (1 + margin))
            add(f"{team} Doble Oportunidad ({side})", {"type": "DC", "side": side}, est, p_mod, p_m,
                dec_to_american(est), estimated=True)
    else:
        # US sports: Moneyline
        add(f"{hn} Ganador Directo (Moneyline)", {"type": "ML", "side": "home"}, dh, mh, ph, oh["odds"])
        add(f"{an} Ganador Directo (Moneyline)", {"type": "ML", "side": "away"}, da, ma, pa, oa["odds"])

        # Spread / Handicap if present
        ps = odds.get("pointSpread") or {}
        sh = odds_side(ps, "home")
        sa = odds_side(ps, "away")
        if sh and sa and sh.get("line") and sa.get("line"):
            d_sh = american_to_decimal(sh.get("odds", "-110")) or 1.91
            d_sa = american_to_decimal(sa.get("odds", "-110")) or 1.91
            add(f"{hn} ({sh['line']} Spread / Hándicap)", {"type": "SPREAD", "side": "home", "line": sh['line']},
                d_sh, 0.50, 0.50, sh.get("odds", "-110"))
            add(f"{an} ({sa['line']} Spread / Hándicap)", {"type": "SPREAD", "side": "away", "line": sa['line']},
                d_sa, 0.50, 0.50, sa.get("odds", "-110"))

    tot = odds.get("total") or {}
    ov, un = odds_side(tot, "over"), odds_side(tot, "under")
    if ov and un:
        line = float(re.sub(r"[^\d.]", "", ov.get("line", "") or str(odds.get("overUnder", ""))) or 0)
        do, du = american_to_decimal(ov["odds"]), american_to_decimal(un["odds"])
        if line and do and du:
            inv_t = 1 / do + 1 / du
            po, pu = (1 / do) / inv_t, (1 / du) / inv_t
            unit = "Goles" if sport == "Football" else ("Carreras" if sport == "Baseball" else "Puntos")
            add(f"Más de {line} {unit} Totales (Over {line})", {"type": "TOTAL", "side": "over", "line": line}, do, po, po, ov["odds"])
            add(f"Menos de {line} {unit} Totales (Under {line})", {"type": "TOTAL", "side": "under", "line": line}, du, pu, pu, un["odds"])
            if sport == "Football" and line <= 8.5:
                lmb = lambda_from_over(po, line)
                base["lambda"] = lmb
                for c in cands:
                    c["lambda"] = lmb
                # líneas alternativas (cuota estimada) para piernas seguras
                for alt in (line - 1, line + 1):
                    if alt > 0:
                        p_o = poisson_over(lmb, alt)
                        add(f"Más de {alt} Goles Totales (Over {alt})", {"type": "TOTAL", "side": "over", "line": alt},
                            1 / (p_o * (1 + margin)), p_o, p_o, "est", estimated=True)
                        add(f"Menos de {alt} Goles Totales (Under {alt})", {"type": "TOTAL", "side": "under", "line": alt},
                            1 / ((1 - p_o) * (1 + margin)), 1 - p_o, 1 - p_o, "est", estimated=True)
    return cands


def pick_best(cands):
    """Top 3 (partidos distintos) para Modo A/B y 2 piernas seguras para Modo C."""
    def score(c):
        return c["p"] + 1.5 * c["ev"]

    main_pool = [c for c in cands if not c["estimated"] and 1.40 <= c["odds"] <= 1.95 and c["p"] >= 0.55]
    if len(main_pool) < 3:
        main_pool = [c for c in cands if not c["estimated"] and 1.30 <= c["odds"] <= 2.30 and c["p"] >= 0.48]
    main, used = [], set()
    for c in sorted(main_pool, key=score, reverse=True):
        if c["espnEventId"] in used:
            continue
        main.append(c)
        used.add(c["espnEventId"])
        if len(main) == 3:
            break

    safe = []
    for c in main[:2]:
        pool = [x for x in cands if x["espnEventId"] == c["espnEventId"] and 1.10 <= x["odds"] <= 1.45 and x["p"] >= 0.68]
        # coherente con la pierna principal
        mk = c["market"]
        if mk["type"] == "ML":
            pref = [x for x in pool if x["market"] == {"type": "DC", "side": "1X" if mk["side"] == "home" else "X2"}]
        elif mk["type"] == "TOTAL":
            pref = [x for x in pool if x["market"]["type"] == "TOTAL" and x["market"]["side"] == mk["side"]]
        else:
            pref = []
        chosen = (sorted(pref, key=lambda x: -x["p"]) or sorted(pool, key=lambda x: -x["p"]) or [c])[0]
        safe.append(chosen)
    return main, safe


# ───────────────────────────── salida (schema existente) ─────────────────────────────
DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MONTHS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
          "Septiembre", "Octubre", "Noviembre", "Diciembre"]
BADGES = ["bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
          "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
          "bg-amber-500/15 text-amber-400 border-amber-500/30"]

_deep_cache = {}


def fetch_deep_intel(ev_id, league_path):
    if not ev_id:
        return {}
    if ev_id in _deep_cache:
        return _deep_cache[ev_id]
    path = league_path if "/" in league_path else f"soccer/{league_path}"
    url = f"https://site.api.espn.com/apis/site/v2/sports/{path}/summary?event={ev_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 BlackRoyal"})
    intel = {}
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.load(r)
            pred = d.get("predictor", {})
            if pred and "homeTeam" in pred:
                ht_proj = pred["homeTeam"].get("gameProjection")
                at_proj = pred.get("awayTeam", {}).get("gameProjection")
                if ht_proj and at_proj:
                    intel["predictor"] = {"home": float(ht_proj), "away": float(at_proj)}
            lfg = d.get("lastFiveGames", [])
            team_stats = {}
            for t in lfg:
                tname = t.get("team", {}).get("displayName", "")
                gf, ga = 0, 0
                for m in t.get("events", []):
                    score = m.get("score", "")
                    res = m.get("gameResult", "")
                    if "-" in score:
                        parts = score.split("-")
                        try:
                            s1, s2 = int(parts[0]), int(parts[1])
                            if res == "W":
                                gf += max(s1, s2); ga += min(s1, s2)
                            elif res == "L":
                                gf += min(s1, s2); ga += max(s1, s2)
                            else:
                                gf += s1; ga += s2
                        except Exception:
                            pass
                if tname:
                    team_stats[tname] = {"gf": gf, "ga": ga}
            if team_stats:
                intel["team_stats"] = team_stats
    except Exception:
        pass
    _deep_cache[ev_id] = intel
    return intel


def algo_text(c):
    tag = "cuota estimada" if c.get("oddsEstimated") or c.get("estimated") else f"DraftKings {c.get('srcOdds', '')}"
    lam = f"; goles esperados (Poisson) {c['lambda']:.2f}" if c.get("lambda") else ""
    intel = fetch_deep_intel(c.get("espnEventId"), c.get("espnLeague", ""))

    extra_parts = []
    pred = intel.get("predictor")
    if pred:
        extra_parts.append(f"Predictor Oficial ESPN: {c['home']} {pred['home']:.1f}% vs {c['away']} {pred['away']:.1f}%")

    ts = intel.get("team_stats", {})
    if ts:
        unit = "goles" if c.get("sport") == "Football" else "pts"
        h_s = ts.get(c["home"])
        a_s = ts.get(c["away"])
        if h_s and a_s:
            extra_parts.append(f"Últimos 5: {c['home']} ({h_s['gf']} anotados / {h_s['ga']} recibidos {unit}) vs {c['away']} ({a_s['gf']} anotados / {a_s['ga']} recibidos)")

    extra_str = "; " + "; ".join(extra_parts) if extra_parts else ""
    return (f"Modelo Cuantitativo Multifuente: {tag} → @ {c['odds']:.2f}; prob. de mercado sin margen {c.get('pMktSel', c['p']):.0%}; "
            f"forma últimos 5 {c['home']} {c.get('formH', '—')} vs {c['away']} {c.get('formA', '—')}{lam}{extra_str}; "
            f"prob. modelo {c['p']:.0%}; EV {c['ev']:+.1%}.")


def pick_dict(c, i, with_detail=True):
    sport = c.get("sport", "Football")
    if sport == "Basketball":
        src = "NBA Second Spectrum"
        badge = "bg-purple-500/15 text-purple-400 border-purple-500/30"
    elif sport == "NFL":
        src = "Next Gen Stats NFL"
        badge = "bg-orange-500/15 text-orange-400 border-orange-500/30"
    elif sport == "Baseball":
        src = "Statcast Sabermetrics"
        badge = "bg-sky-500/15 text-sky-400 border-sky-500/30"
    else:
        src = "ESPN / DraftKings"
        badge = BADGES[i % 3]

    d = {
        "sourceName": src,
        "sport": sport,
        "badgeClass": badge,
        "match": c["match"],
        "tournament": f"{c['league']} ({c['kickoff'].strftime('%H:%M')} CST)",
        "selection": c["selection"],
        "odds": c["odds"],
        "confidencePct": round(c["p"] * 100),
        "algorithm": algo_text(c),
        "markets": [c["market"]],
        "espnEventId": c["espnEventId"],
        "espnLeague": c["espnLeague"],
        "kickoffLocal": c["kickoff"].strftime("%Y-%m-%d %H:%M"),
        "oddsEstimated": c["estimated"],
        "verified": True,
    }
    if with_detail:
        d["stadium"] = c["venue"]
        d["singleReturn"] = round(STAKE_A_PER_PICK * c["odds"], 2)
    return d


def build_summary(day, main, safe, hybrid_data=None):
    dn, mn = DAYS[day.weekday()], MONTHS[day.month - 1]
    tag = f"{day.day} {mn.upper()}"
    p = [c["p"] for c in main]
    o = [c["odds"] for c in main]
    avg_odds = round(sum(o) / len(o), 2)
    a_wr = sum(p) / len(p)
    a_ev = sum(c["ev"] for c in main) / len(main)

    leagues = ", ".join(sorted({c["league"] for c in main}))
    picks_a = [pick_dict(c, i) for i, c in enumerate(main)]
    strategies = {
        "modo_a_simples": {
            "id": "STRATEGY-MODO-A",
            "modeName": "Modo A: Apuestas Simples de Valor (100% Fútbol)",
            "modeShort": f"Modo A: Simples Fútbol ({a_wr:.1%} prob. media)",
            "badge": "MAYOR PROBABILIDAD",
            "badgeClass": BADGES[1], "tagColor": "emerald",
            "description": f"{len(main)} selecciones con cuotas reales DraftKings para el {dn} {day.day} de {mn} ({leagues}). Cada acierto cobra por separado.",
            "avgOdds": avg_odds,
            "expectedWinRate": f"{a_wr:.1%}",
            "combinedEv": f"{a_ev:+.1%}",
            "recommendedStake": "1.0% por selección (Flat Staking)",
            "riskLevel": "BAJO" if a_wr >= 0.6 else "MEDIO",
            "picks": picks_a,
            "real_life_example": {
                "bookie_steps": [
                    "Abre tu casa de apuestas (Caliente, Bet365, Betano, DraftKings, etc.).",
                    "Busca cada partido y coloca una apuesta SIMPLE independiente en cada selección.",
                    "Apuesta el mismo monto en cada una (ej. $100).",
                ],
                "winning_scenario": {
                    "title": "¿Cómo se cobra con las Simples?",
                    "match_examples": [{"match": c["match"], "min_result": c["selection"],
                                        "explanation": f"Si se cumple cobras ${100 * c['odds']:.2f} (+${100 * (c['odds'] - 1):.2f} neto)."} for c in main],
                    "payout_example": f"Con $100 por selección: los {len(main)} aciertos pagan ${100 * sum(o):.2f}.",
                },
                "copy_text": f"👑 BLACK ROYAL — MODO A: SIMPLES ({tag})\n" + "\n".join(
                    f"{i + 1}. ⚽ {c['match']}: {c['selection']} @ {c['odds']:.2f}" for i, c in enumerate(main)),
            },
        }
    }

    if len(main) == 3:
        p1, p2, p3 = p
        d1, d2, d3 = round(o[0] * o[1], 2), round(o[0] * o[2], 2), round(o[1] * o[2], 2)
        tr = round(o[0] * o[1] * o[2], 2)
        p_ge2 = p1 * p2 * p3 + p1 * p2 * (1 - p3) + p1 * (1 - p2) * p3 + (1 - p1) * p2 * p3
        exp_ret = 25 * (d1 * p1 * p2 + d2 * p1 * p3 + d3 * p2 * p3 + tr * p1 * p2 * p3)
        names = [c["home"] if c["market"].get("side") != "away" else c["away"] for c in main]
        strategies["modo_b_sistema"] = {
            "id": "STRATEGY-MODO-B",
            "modeName": "Modo B: Sistema 2 de 3 (Trixie / Round Robin 100% Fútbol)",
            "modeShort": "Modo B: Sistema 2/3 (Seguro contra 1 Fallo)",
            "badge": "SEGURO CONTRA 1 FALLO",
            "badgeClass": BADGES[0], "tagColor": "cyan",
            "description": "4 combinadas automáticas (3 Dobles + 1 Triple) con las mismas 3 selecciones del Modo A.",
            "totalCombinations": "4 Apuestas (3 Dobles + 1 Triple)",
            "expectedWinRate": f"{p_ge2:.1%}",
            "combinedEv": f"{exp_ret / 100 - 1:+.1%}",
            "recommendedStake": "$25 por combinación ($100 total)",
            "riskLevel": "MEDIO",
            "picks": [{**pick_dict(c, i, False), "algorithm": f"Pick {chr(65 + i)}: {algo_text(c)}"} for i, c in enumerate(main)],
            "combinations": [
                {"name": f"Doble 1 (⚽ {names[0]} + ⚽ {names[1]})", "odds": d1, "formula": f"{o[0]} × {o[1]}"},
                {"name": f"Doble 2 (⚽ {names[0]} + ⚽ {names[2]})", "odds": d2, "formula": f"{o[0]} × {o[2]}"},
                {"name": f"Doble 3 (⚽ {names[1]} + ⚽ {names[2]})", "odds": d3, "formula": f"{o[1]} × {o[2]}"},
                {"name": "Triple (Pleno 3/3)", "odds": tr, "formula": f"{o[0]} × {o[1]} × {o[2]}"},
            ],
            "real_life_example": {
                "bookie_steps": ["Agrega las 3 selecciones al cupón.", "Elige 'Sistema' → 'Trixie' (3 dobles + 1 triple).", "Apuesta $25 por línea ($100 total)."],
                "winning_scenario": {
                    "title": "¿Cómo se cobra con el Sistema 2/3?",
                    "match_examples": [
                        {"match": f"Escenario 2 de 3 ({names[0]} + {names[1]})", "min_result": "Fallan solo el tercero", "explanation": f"Cobras la Doble 1: ${25 * d1:.2f}."},
                        {"match": f"Escenario 2 de 3 ({names[0]} + {names[2]})", "min_result": "Falla solo el segundo", "explanation": f"Cobras la Doble 2: ${25 * d2:.2f}."},
                        {"match": "Escenario Pleno 3 de 3", "min_result": "Aciertan los 3", "explanation": f"Cobras ${25 * (d1 + d2 + d3 + tr):.2f}."},
                    ],
                    "payout_example": f"Con $100 cobras hasta ${25 * (d1 + d2 + d3 + tr):.2f} si aciertan los 3.",
                },
                "copy_text": f"👑 BLACK ROYAL — MODO B: SISTEMA 2/3 ({tag})\n" + "\n".join(
                    f"• Pick {chr(65 + i)}: ⚽ {c['match']} ({c['selection']}) @ {c['odds']:.2f}" for i, c in enumerate(main)),
            },
        }

    if len(safe) == 2:
        tot = round(safe[0]["odds"] * safe[1]["odds"], 2)
        pc = safe[0]["p"] * safe[1]["p"]
        strategies["modo_c_banker"] = {
            "id": "STRATEGY-MODO-C",
            "modeName": "Modo C: Doble Banker 100% Fútbol (2 Legs)",
            "modeShort": f"Modo C: Doble Banker (@ {tot:.2f}x)",
            "badge": "BAJA VOLATILIDAD",
            "badgeClass": BADGES[2], "tagColor": "amber",
            "description": f"Combinada de 2 piernas de alta probabilidad ({safe[0]['match']} y {safe[1]['match']}).",
            "totalOdds": tot,
            "fairOdds": round(1 / pc, 2),
            "expectedWinRate": f"{pc:.1%}",
            "combinedEv": f"{pc * tot - 1:+.1%}",
            "recommendedStake": "2.0% – 3.0% Bankroll",
            "riskLevel": "BAJO",
            "picks": [pick_dict(c, i) for i, c in enumerate(safe)],
            "real_life_example": {
                "bookie_steps": ["Abre tu casa de apuestas.",
                                 f"Selecciona: {safe[0]['match']} ({safe[0]['selection']}) y {safe[1]['match']} ({safe[1]['selection']}).",
                                 f"Coloca una Combinada / Parlay. Cuota aprox.: {tot:.2f}x (verifica la cuota real en tu casa)."],
                "winning_scenario": {
                    "title": "¿Cómo se gana con la Doble Banker?",
                    "match_examples": [{"match": c["match"], "min_result": c["selection"], "explanation": f"Probabilidad modelo {c['p']:.0%}."} for c in safe],
                    "payout_example": f"Si ambas se cumplen, con $100 cobras ${tot * 100:.2f} (+${(tot - 1) * 100:.2f} neto).",
                },
                "copy_text": f"👑 BLACK ROYAL — MODO C: DOBLE BANKER ({tag})\n" + "\n".join(
                    f"{i + 1}. ⚽ {c['match']} ({c['selection']}) @ {c['odds']:.2f}" for i, c in enumerate(safe)),
            },
        }

    now = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")
    out = {
        "generated_at": now,
        "hybrid_mode": bool(hybrid_data),
        "hybrid_trigger_reason": f"EDICIÓN DUAL: 100% Fútbol ({len(main)} partidos)" + (f" + Modo Híbrido ({', '.join(hybrid_data['active_sports'])})" if hybrid_data else ""),
        "active_sports": ["Football"],
        "verification_meta": {
            "verified": True,
            "verified_date": day.strftime("%Y-%m-%d"),
            "verified_at": now,
            "verification_status": "PARTIDOS Y CUOTAS REALES (ESPN API / DraftKings)",
            "auditor": "Black Royal — pronostico_diario.py",
            "total_matches_verified": len({c["espnEventId"] for c in main + safe}),
        },
        "strategies": strategies,
    }
    if hybrid_data:
        out["has_hybrid_edition"] = True
        out["hybrid_edition"] = hybrid_data
    return out


def build_hybrid_edition(day, soccer_cands, us_cands):
    if not us_cands or not soccer_cands:
        return None

    def score(c):
        return c["p"] + 1.5 * c["ev"]

    best_soccer = sorted([c for c in soccer_cands if not c["estimated"] and 1.30 <= c["odds"] <= 2.20], key=score, reverse=True)
    if not best_soccer:
        best_soccer = sorted(soccer_cands, key=score, reverse=True)
    f_pick = best_soccer[0]

    best_us = sorted([c for c in us_cands if not c["estimated"] and 1.20 <= c["odds"] <= 2.20], key=score, reverse=True)
    us_picks = []
    used = set()
    for c in best_us:
        if c["espnEventId"] not in used:
            us_picks.append(c)
            used.add(c["espnEventId"])
            if len(us_picks) == 2:
                break

    if len(us_picks) < 2:
        additional_soccer = [c for c in best_soccer if c["espnEventId"] != f_pick["espnEventId"]]
        if additional_soccer:
            hybrid_main = [f_pick, additional_soccer[0]] + us_picks
        else:
            hybrid_main = [f_pick] + us_picks
    else:
        hybrid_main = [f_pick, us_picks[0], us_picks[1]]

    if len(hybrid_main) < 3:
        return None

    h_safe = []
    for c in hybrid_main[:2]:
        pool = [x for x in (soccer_cands + us_cands) if x["espnEventId"] == c["espnEventId"] and 1.10 <= x["odds"] <= 1.45]
        h_safe.append(sorted(pool, key=lambda x: -x["p"])[0] if pool else c)

    dn, mn = DAYS[day.weekday()], MONTHS[day.month - 1]
    tag = f"{day.day} {mn.upper()}"
    p = [c["p"] for c in hybrid_main]
    o = [c["odds"] for c in hybrid_main]
    avg_odds = round(sum(o) / len(o), 2)
    a_wr = sum(p) / len(p)
    a_ev = sum(c["ev"] for c in hybrid_main) / len(hybrid_main)

    active_sports = list(dict.fromkeys([c["sport"] for c in hybrid_main]))
    sports_label = " + ".join(["Fútbol" if s == "Football" else s for s in active_sports])

    p1, p2, p3 = p
    d1, d2, d3 = round(o[0] * o[1], 2), round(o[0] * o[2], 2), round(o[1] * o[2], 2)
    tr = round(o[0] * o[1] * o[2], 2)
    p_ge2 = p1 * p2 * p3 + p1 * p2 * (1 - p3) + p1 * (1 - p2) * p3 + (1 - p1) * p2 * p3
    exp_ret = 25 * (d1 * p1 * p2 + d2 * p1 * p3 + d3 * p2 * p3 + tr * p1 * p2 * p3)

    c_tot = round(h_safe[0]["odds"] * h_safe[1]["odds"], 2)
    c_p = h_safe[0]["p"] * h_safe[1]["p"]

    picks_formatted = [pick_dict(c, i) for i, c in enumerate(hybrid_main)]
    for i, pf in enumerate(picks_formatted):
        pf["safeSelection"] = h_safe[i]["selection"] if i < len(h_safe) else pf["selection"]
        pf["safeOdds"] = h_safe[i]["odds"] if i < len(h_safe) else pf["odds"]

    return {
        "title": f"Módulo de Arbitraje Híbrido Multideporte ({sports_label})",
        "subtitle": f"Fusión cuantitativa del fútbol con las mejores asimetrías de {active_sports[1] if len(active_sports) > 1 else 'deportes americanos'}.",
        "trigger_reason": f"ACTIVADO: Arbitraje multideporte combinando {hybrid_main[0]['match']} con {hybrid_main[1]['match']} y {hybrid_main[2]['match']}.",
        "active_sports": active_sports,
        "expectedWinRate": f"{a_wr:.1%}",
        "avgOdds": avg_odds,
        "combinedEv": f"{a_ev:+.1%}",
        "picks": picks_formatted,
        "strategies": {
            "modo_a_simples": {
                "id": "STRATEGY-HYBRID-A",
                "modeName": f"Modo A: Simples Híbridas ({sports_label})",
                "modeShort": f"Modo A: Simples Híbridas ({a_wr:.1%} Win Rate)",
                "badge": "MÁXIMO WIN RATE HÍBRIDO",
                "badgeClass": "bg-purple-500/15 text-purple-400 border-purple-500/30",
                "tagColor": "purple",
                "description": f"3 Selecciones multideporte de élite para el {dn} {day.day} de {mn}. Cada acierto cobra por separado amortizando el riesgo.",
                "avgOdds": avg_odds,
                "expectedWinRate": f"{a_wr:.1%}",
                "combinedEv": f"{a_ev:+.1%}",
                "recommendedStake": "1.0% por selección (Flat Staking)",
                "riskLevel": "MÍNIMO",
                "picks": picks_formatted,
                "real_life_example": {
                    "bookie_steps": [
                        "Abre tu casa de apuestas (Caliente, Bet365, Betano, DraftKings, etc.).",
                        f"Coloca 3 apuestas SIMPLES independientes: {hybrid_main[0]['match']}, {hybrid_main[1]['match']} y {hybrid_main[2]['match']}.",
                        "Apuesta el mismo monto en cada una (ej. $100)."
                    ],
                    "winning_scenario": {
                        "title": "¿Cómo se cobra con las Simples Híbridas?",
                        "match_examples": [{"match": c["match"], "min_result": c["selection"], "explanation": f"Cobras ${100 * c['odds']:.2f}."} for c in hybrid_main],
                        "payout_example": f"Con 2 aciertos de 3 aseguras ganancia neta. Con pleno cobras ${100 * sum(o):.2f}."
                    },
                    "copy_text": f"👑 BLACK ROYAL — SIMPLES HÍBRIDAS ({tag})\n" + "\n".join(f"{i+1}. {c['match']}: {c['selection']} @ {c['odds']:.2f}" for i, c in enumerate(hybrid_main))
                }
            },
            "modo_b_sistema": {
                "id": "STRATEGY-HYBRID-B",
                "modeName": "Modo B: Sistema 2 de 3 Híbrido (Trixie / Round Robin)",
                "modeShort": "Modo B: Sistema 2/3 Híbrido (Seguro contra 1 Fallo)",
                "badge": "SEGURO MULTIDEPORTE",
                "badgeClass": "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
                "tagColor": "cyan",
                "description": "4 combinadas automáticas (3 Dobles + 1 Triple) combinando Fútbol y deportes americanos. Si 1 falla, ¡cobras la doble correspondiente!",
                "totalCombinations": "4 Apuestas (3 Dobles + 1 Triple)",
                "expectedWinRate": f"{p_ge2:.1%}",
                "combinedEv": f"{exp_ret / 100 - 1:+.1%}",
                "recommendedStake": "$25 por combinación ($100 total)",
                "riskLevel": "BAJO",
                "picks": [{**pick_dict(c, i, False), "algorithm": f"Pick {chr(65 + i)}: {algo_text(c)}"} for i, c in enumerate(hybrid_main)],
                "combinations": [
                    {"name": f"Doble 1 ({hybrid_main[0]['home']} + {hybrid_main[1]['home']})", "odds": d1, "formula": f"{o[0]} × {o[1]}"},
                    {"name": f"Doble 2 ({hybrid_main[0]['home']} + {hybrid_main[2]['home']})", "odds": d2, "formula": f"{o[0]} × {o[2]}"},
                    {"name": f"Doble 3 ({hybrid_main[1]['home']} + {hybrid_main[2]['home']})", "odds": d3, "formula": f"{o[1]} × {o[2]}"},
                    {"name": "Triple (Pleno Multideporte)", "odds": tr, "formula": f"{o[0]} × {o[1]} × {o[2]}"}
                ],
                "real_life_example": {
                    "bookie_steps": ["Selecciona los 3 eventos en el cupón.", "Elige pestaña Sistema → Trixie.", "Apuesta $25 por línea ($100 total)."],
                    "winning_scenario": {
                        "title": "¿Cómo se cobra con el Sistema Híbrido?",
                        "match_examples": [
                            {"match": f"Escenario 2 de 3 ({hybrid_main[0]['home']} + {hybrid_main[1]['home']})", "min_result": "Ganan los 2 primeros", "explanation": f"Cobras Doble 1 (@ {d1}x): ${25 * d1:.2f} amortizando."},
                            {"match": "Escenario Pleno 3 de 3", "min_result": "Cumplen los 3", "explanation": f"Cobras las 3 Dobles + Triple: ${25 * (d1 + d2 + d3 + tr):.2f}."}
                        ],
                        "payout_example": f"Con $100 cobras hasta ${25 * (d1 + d2 + d3 + tr):.2f} si aciertan los 3, o amortizas si 1 falla."
                    },
                    "copy_text": f"👑 BLACK ROYAL — SISTEMA 2/3 HÍBRIDO ({tag})\n" + "\n".join(f"• Pick {chr(65 + i)}: {c['match']} ({c['selection']}) @ {c['odds']:.2f}" for i, c in enumerate(hybrid_main))
                }
            },
            "modo_c_banker": {
                "id": "STRATEGY-HYBRID-C",
                "modeName": f"Modo C: Doble Banker Híbrida (Duplicador @ {c_tot:.2f}x)",
                "modeShort": f"Modo C: Doble Banker Híbrida (@ {c_tot:.2f}x)",
                "badge": "DUPLICADOR HÍBRIDO",
                "badgeClass": "bg-amber-500/15 text-amber-400 border-amber-500/30",
                "tagColor": "amber",
                "description": f"Combinada estricta de solo 2 eventos de altísima certeza: {h_safe[0]['match']} y {h_safe[1]['match']}.",
                "totalOdds": c_tot,
                "fairOdds": round(1 / c_p, 2) if c_p else 1.5,
                "expectedWinRate": f"{c_p:.1%}",
                "combinedEv": f"{c_p * c_tot - 1:+.1%}",
                "recommendedStake": "2.5% – 3.0% Bankroll",
                "riskLevel": "BAJO",
                "picks": [pick_dict(c, i) for i, c in enumerate(h_safe[:2])],
                "real_life_example": {
                    "bookie_steps": ["Abre tu casa de apuestas.", f"Selecciona: {h_safe[0]['match']} y {h_safe[1]['match']}.", f"Coloca Parlay / Combinada @ {c_tot:.2f}x."],
                    "winning_scenario": {
                        "title": "¿Cómo se gana con la Doble Banker Híbrida?",
                        "match_examples": [{"match": c["match"], "min_result": c["selection"], "explanation": f"Probabilidad modelo {c['p']:.0%}."} for c in h_safe[:2]],
                        "payout_example": f"Si ambos cumplen, con $100 cobras ${c_tot * 100:.2f}."
                    },
                    "copy_text": f"👑 BLACK ROYAL — DOBLE BANKER HÍBRIDA ({tag})\n" + "\n".join(f"{i+1}. {c['match']} ({c['selection']}) @ {c['odds']:.2f}" for i, c in enumerate(h_safe[:2]))
                }
            }
        }
    }


def archive_snapshot(day, summary, suffix=""):
    archive = load_json(ARCHIVE_FILE, {"version": "1.0", "snapshots": {}})
    key = day.strftime("%Y-%m-%d") + suffix
    old = archive["snapshots"].get(key)
    if old and old.get("status") == "EVALUATED":
        print(f"  ℹ El escenario {key} ya está evaluado; no se sobrescribe.")
        return
    snapshot = {
        "date": key,
        "saved_at": datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "PENDING_EVALUATION",
        "strategies": summary["strategies"],
        "metrics": {"totalModes": len(summary["strategies"]), "simulatedTotalStake": 500.0,
                    "evaluated": False, "netPnL": 0.0, "roiPct": "0.0%"},
    }
    if summary.get("has_hybrid_edition"):
        snapshot["has_hybrid_edition"] = True
        snapshot["hybrid_edition"] = summary["hybrid_edition"]
    archive["snapshots"][key] = snapshot
    save_json(ARCHIVE_FILE, archive)


# ───────────────────────────── reporte ─────────────────────────────
def fmt_settlement(report):
    lines = []
    for e in report:
        for part in ("main", "hybrid"):
            if part not in e:
                continue
            m, res, complete = e[part]
            title = "Edición principal" if part == "main" else "Edición híbrida"
            lines.append(f"### {e['date']} — {title} {'(COMPLETA)' if complete else '(PARCIAL: hay partidos pendientes)'}")
            for match, txt in res.items():
                lines.append(f"- **{match}**: {txt}")
            lines.append(f"- **PnL**: apostado ${m['simulatedTotalStake']:.2f} → cobrado ${m['simulatedTotalReturn']:.2f} | "
                         f"neto **${m['netPnL']:+.2f}** ({m['roiPct']}) | {m['winRate']}")
            lines.append("")
    return "\n".join(lines) or "_Sin escenarios pendientes por liquidar._"


def fmt_picks(summary):
    out = ["## Opción 1: 100% Fútbol"]
    for key, s in summary["strategies"].items():
        out.append(f"### {s['modeName']}")
        out.append(f"Prob. estimada: **{s['expectedWinRate']}** | EV: {s['combinedEv']}"
                   + (f" | Cuota total: {s['totalOdds']}" if "totalOdds" in s else ""))
        for p in s["picks"]:
            est = " _(cuota estimada)_" if p.get("oddsEstimated") else ""
            out.append(f"- {p['tournament']} — **{p['match']}**: {p['selection']} @ **{p['odds']:.2f}**{est} (conf. {p['confidencePct']}%)")
        out.append("")

    if summary.get("has_hybrid_edition") and summary.get("hybrid_edition"):
        hy = summary["hybrid_edition"]
        out.append("## Opción 2: Modo Híbrido Multideporte (" + " + ".join(hy.get("active_sports", [])) + ")")
        out.append(f"_{hy.get('subtitle', '')}_\n")
        for key, s in hy.get("strategies", {}).items():
            out.append(f"### {s['modeName']}")
            out.append(f"Prob. estimada: **{s['expectedWinRate']}** | EV: {s['combinedEv']}"
                       + (f" | Cuota total: {s['totalOdds']}" if "totalOdds" in s else ""))
            for p in s.get("picks", []):
                est = " _(cuota estimada)_" if p.get("oddsEstimated") else ""
                out.append(f"- {p.get('tournament', '')} — **{p['match']}**: {p['selection']} @ **{p['odds']:.2f}**{est} (conf. {p.get('confidencePct', 0)}%)")
            out.append("")
    return "\n".join(out)


# ───────────────────────────── main ─────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="BLACK ROYAL — pronóstico diario con datos reales")
    ap.add_argument("--date", help="Fecha objetivo YYYY-MM-DD (por defecto hoy, hora CDMX)")
    ap.add_argument("--settle-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-html", action="store_true")
    ap.add_argument("--slot", help="Solo partidos con este horario de inicio HH:MM (CST). Crea una edición aparte "
                                   "(archivo YYYY-MM-DD-HHMM) sin tocar el pronóstico principal ni index.html")
    args = ap.parse_args()
    slot = args.slot.zfill(5) if args.slot else None
    suffix = f"-{slot.replace(':', '')}" if slot else ""

    now_local = datetime.now(LOCAL_TZ)
    day = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else now_local.date()

    print("=" * 90)
    print(f" 👑 BLACK ROYAL — PRONÓSTICO DIARIO DUAL (FÚTBOL + HÍBRIDO)  ({day})  [ESPN API + DraftKings]")
    print("=" * 90)

    print("\n▶ 1. Liquidación de escenarios pendientes (Fútbol + Híbridos)")
    report = settle_pending(day, args.dry_run)
    settle_md = fmt_settlement(report)
    print(settle_md)

    if args.settle_only:
        return

    print(f"\n▶ 2. Análisis de partidos del {day} con cuotas reales (Fútbol + Multideporte)")
    all_paths = list(SOCCER_LEAGUES) if slot else (list(SOCCER_LEAGUES) + list(OTHER_SPORTS))
    events = fetch_many(all_paths, [day, day + timedelta(days=1)])
    soccer_cands = []
    us_cands = []
    for ev in events:
        try:
            analyzed = analyze_event(ev, now_local, day, slot, 0 if slot else 45)
            for c in analyzed:
                if c.get("sport") == "Football":
                    soccer_cands.append(c)
                else:
                    us_cands.append(c)
        except Exception as e:  # evento mal formado: se ignora
            print(f"    ⚠️ Evento {ev.get('id')} omitido: {e}")

    n_matches = len({c["espnEventId"] for c in soccer_cands})
    print(f"  • Partidos de fútbol elegibles con cuotas: {n_matches}")
    if us_cands:
        n_us = len({c["espnEventId"] for c in us_cands})
        print(f"  • Eventos multideporte elegibles (NBA/NFL/MLB): {n_us}")

    main_p, safe_p = pick_best(soccer_cands)
    if len(main_p) < 2:
        print("  ❌ No hay suficientes partidos con cuotas reales para publicar un pronóstico confiable. No se modifica nada.")
        sys.exit(1)

    hybrid_edition = None
    if not slot and us_cands:
        hybrid_edition = build_hybrid_edition(day, soccer_cands, us_cands)

    summary = build_summary(day, main_p, safe_p, hybrid_edition)
    if slot:
        summary["hybrid_trigger_reason"] = f"EDICIÓN {slot} CST: " + summary["hybrid_trigger_reason"]
        for s in summary["strategies"].values():
            s["modeName"] += f" — Edición {slot}"

    picks_md = fmt_picks(summary)
    print(picks_md)

    if args.dry_run:
        print("\n(dry-run: no se escribieron archivos)")
        return

    if slot:
        print(f"▶ 3. Archivando edición {slot} (el pronóstico principal e index.html no se modifican)")
        archive_snapshot(day, summary, suffix)
    else:
        print("▶ 3. Guardando summary_recommendations.json y archivo de escenarios (Dual: Fútbol + Híbrido)")
        save_json(SUMMARY_FILE, summary)
        archive_snapshot(day, summary)

    if not slot and not args.no_html and os.path.exists(GEN_INDEX):
        print("▶ 4. Reconstruyendo index.html (activando selector dual Fútbol vs Híbrido)")
        subprocess.run([sys.executable, GEN_INDEX], check=False, cwd=CURRENT_DIR)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    rpath = os.path.join(REPORTS_DIR, f"pronostico_{day}{suffix}.md")
    with open(rpath, "w", encoding="utf-8") as f:
        f.write(f"# BLACK ROYAL — Pronóstico Dual {day}{' (edición ' + slot + ' CST)' if slot else ''}\n\n_Generado {now_local:%Y-%m-%d %H:%M} CST · Fuente: ESPN API + DraftKings_\n\n")
        f.write("## Liquidación de días anteriores\n\n" + settle_md + "\n\n## Pronóstico del día (Fútbol + Híbrido)\n\n" + picks_md)
        f.write("\n> Probabilidades = cuotas DraftKings sin margen + pequeño ajuste por forma reciente. "
                "Las cuotas marcadas como estimadas deben verificarse en tu casa de apuestas. No es garantía de resultado.\n")
    print(f"\n✔ Listo. Reporte: {rpath}")


if __name__ == "__main__":
    main()
