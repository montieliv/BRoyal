#!/usr/bin/env python3
"""
BLACK ROYAL — Fuentes complementarias (opcionales)

  • The Odds API  (the-odds-api.com): cuotas de varias casas -> mejor cuota,
    consenso sin margen y cuota REAL de Doble Oportunidad.
  • API-Football  (api-football.com): predicción oficial, % 1X2 y lesiones.

Ambas usan plan GRATIS con API key (sin tarjeta). Las keys se leen de:
    1) variables de entorno  ODDS_API_KEY / API_FOOTBALL_KEY
    2) archivo api_keys.json (ver api_keys.example.json; está en .gitignore)

Si falta una key, esa fuente se omite sin romper nada. Todo es INFORMATIVO:
no modifica las probabilidades ni las cuotas del motor; solo agrega contexto
y advertencias (⚠️) cuando una fuente contradice el pick.

Para cuidar los límites gratuitos (Odds API ~500 créditos/mes, API-Football
100 consultas/día) solo consulta los mejores partidos del día y cachea las
respuestas en .cache/ (2 h cuotas, 6 h predicciones/lesiones).
"""

import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from statistics import mean

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(CURRENT_DIR, ".cache")
KEYS_FILE = os.path.join(CURRENT_DIR, "api_keys.json")

ODDS_BASE = "https://api.the-odds-api.com/v4"
APIF_BASE = "https://v3.football.api-sports.io"

# Liga ESPN -> sport key de The Odds API (las inexistentes se ignoran sin error)
ODDS_SPORT_KEYS = {
    "uefa.champions": "soccer_uefa_champs_league",
    "uefa.europa": "soccer_uefa_europa_league",
    "uefa.europa.conf": "soccer_uefa_europa_conference_league",
    "eng.1": "soccer_epl",
    "esp.1": "soccer_spain_la_liga",
    "ita.1": "soccer_italy_serie_a",
    "ger.1": "soccer_germany_bundesliga",
    "fra.1": "soccer_france_ligue_one",
    "por.1": "soccer_portugal_primeira_liga",
    "ned.1": "soccer_netherlands_eredivisie",
    "bel.1": "soccer_belgium_first_div",
    "tur.1": "soccer_turkey_super_league",
    "sco.1": "soccer_spl",
    "eng.2": "soccer_efl_champ",
    "mex.1": "soccer_mexico_ligamx",
    "usa.1": "soccer_usa_mls",
    "arg.1": "soccer_argentina_primera_division",
    "bra.1": "soccer_brazil_campeonato",
    "conmebol.libertadores": "soccer_conmebol_copa_libertadores",
    "conmebol.sudamericana": "soccer_conmebol_copa_sudamericana",
}

MAX_EVENTS = 6        # partidos que se enriquecen con cuotas multicasa
MAX_DC_EVENTS = 4     # partidos con consulta extra de Doble Oportunidad real
MAX_APIF_EVENTS = 3   # partidos con predicción + lesiones (respeta el límite de 10 req/min)

_state = {"odds_remaining": None, "odds_used": None, "notes": []}


# ───────────────────────────── infraestructura ─────────────────────────────
def load_keys():
    keys = {"odds": os.environ.get("ODDS_API_KEY", "").strip(),
            "apif": os.environ.get("API_FOOTBALL_KEY", "").strip()}
    try:
        with open(KEYS_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        keys["odds"] = keys["odds"] or str(d.get("odds_api_key", "")).strip()
        keys["apif"] = keys["apif"] or str(d.get("api_football_key", "")).strip()
    except (OSError, ValueError):
        pass
    return keys


def _http_json(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "BlackRoyal/1.0", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r), dict(r.headers)


def _cached(name, ttl_s, fn):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, re.sub(r"[^A-Za-z0-9_.-]", "_", name) + ".json")
    try:
        if time.time() - os.path.getmtime(path) < ttl_s:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except (OSError, ValueError):
        pass
    data = fn()
    if data is not None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    return data


def _note(msg):
    _state["notes"].append(msg)
    print(f"    ℹ️ {msg}")


# ───────────────────────────── The Odds API ─────────────────────────────
class OddsAPI:
    def __init__(self, key):
        self.key = key

    def _get(self, path, **params):
        params["apiKey"] = self.key
        url = f"{ODDS_BASE}{path}?{urllib.parse.urlencode(params)}"
        data, hdr = _http_json(url)
        low = {k.lower(): v for k, v in hdr.items()}
        _state["odds_remaining"] = low.get("x-requests-remaining", _state["odds_remaining"])
        _state["odds_used"] = low.get("x-requests-used", _state["odds_used"])
        return data

    def active_sports(self):
        """Gratis (no consume créditos). Sirve también para validar la key."""
        try:
            return _cached("odds_sports", 6 * 3600, lambda: self._get("/sports/"))
        except Exception as e:
            _note(f"The Odds API no disponible ({e}). Revisa la key.")
            return None

    def league_odds(self, sport_key, day):
        def fetch():
            try:
                return self._get(f"/sports/{sport_key}/odds/", regions="eu", markets="h2h,totals",
                                 oddsFormat="decimal", dateFormat="iso")
            except Exception as e:
                _note(f"The Odds API {sport_key}: {e}")
                return None
        return _cached(f"odds_{sport_key}_{day:%Y%m%d}", 2 * 3600, fetch) or []

    def event_market(self, sport_key, event_id, market, day):
        def fetch():
            try:
                return self._get(f"/sports/{sport_key}/events/{event_id}/odds", regions="eu",
                                 markets=market, oddsFormat="decimal", dateFormat="iso")
            except Exception as e:
                _note(f"The Odds API {market} ({event_id}): {e}")
                return None
        return _cached(f"odds_ev_{event_id}_{market}_{day:%Y%m%d}", 2 * 3600, fetch)


def _find_odds_event(events, home, away, ko, name_score):
    best, best_sc = None, 0.0
    for e in events or []:
        try:
            t = datetime.fromisoformat(e["commence_time"].replace("Z", "+00:00"))
        except (KeyError, ValueError):
            continue
        if abs((t - ko).total_seconds()) > 6 * 3600:
            continue
        sh, sa = name_score(home, e.get("home_team", "")), name_score(away, e.get("away_team", ""))
        sc = min(sh, sa) * 0.6 + (sh + sa) / 2 * 0.4
        if sc > best_sc:
            best, best_sc = e, sc
    return best if best_sc >= 0.62 else None


def _summarize(event, market_key, pick_fn, point=None, devig=True):
    """Resume un mercado entre casas: mejor cuota, promedio y prob. de consenso sin margen.
    pick_fn(outcome_name)->bool selecciona el resultado apostado."""
    prices, probs, best, best_book = [], [], 0.0, ""
    for bk in (event or {}).get("bookmakers", []):
        mk = next((m for m in bk.get("markets", []) if m.get("key") == market_key), None)
        if not mk:
            continue
        outs = [o for o in mk.get("outcomes", [])
                if point is None or o.get("point") is None or abs(float(o["point"]) - point) < 1e-9]
        sel = [o for o in outs if pick_fn(o.get("name", ""))]
        if len(sel) != 1 or not sel[0].get("price"):
            continue
        price = float(sel[0]["price"])
        prices.append(price)
        if price > best:
            best, best_book = price, bk.get("title", bk.get("key", ""))
        if devig and len(outs) >= 2:
            inv = sum(1 / float(o["price"]) for o in outs if o.get("price"))
            if inv > 0:
                probs.append((1 / price) / inv)
    if not prices:
        return None
    return {"best": round(best, 2), "book": best_book, "avg": round(mean(prices), 2),
            "n": len(prices), "consensusP": round(mean(probs), 3) if probs else None}


# ───────────────────────────── API-Football ─────────────────────────────
class APIFootball:
    def __init__(self, key):
        self.key = key

    def _get(self, path, **params):
        time.sleep(1.0)
        url = f"{APIF_BASE}{path}?{urllib.parse.urlencode(params)}"
        data, _ = _http_json(url, headers={"x-apisports-key": self.key})
        errs = data.get("errors")
        if errs:
            msg = "; ".join(errs.values()) if isinstance(errs, dict) else str(errs)
            raise RuntimeError(msg)
        return data.get("response", [])

    def fixtures(self, day):
        def fetch():
            try:
                return self._get("/fixtures", date=f"{day:%Y-%m-%d}")
            except Exception as e:
                _note(f"API-Football fixtures: {e}")
                return None
        return _cached(f"apif_fixtures_{day:%Y%m%d}", 2 * 3600, fetch) or []

    def predictions(self, fid):
        def fetch():
            try:
                r = self._get("/predictions", fixture=fid)
                return r[0] if r else None
            except Exception as e:
                _note(f"API-Football predictions {fid}: {e}")
                return None
        return _cached(f"apif_pred_{fid}", 6 * 3600, fetch)

    def injuries(self, fid):
        def fetch():
            try:
                return self._get("/injuries", fixture=fid)
            except Exception as e:
                _note(f"API-Football injuries {fid}: {e}")
                return None
        return _cached(f"apif_inj_{fid}", 6 * 3600, fetch) or []


def _find_fixture(fixtures, home, away, ko, name_score):
    best, best_sc = None, 0.0
    for f in fixtures or []:
        try:
            t = datetime.fromisoformat(f["fixture"]["date"].replace("Z", "+00:00"))
            fh, fa = f["teams"]["home"]["name"], f["teams"]["away"]["name"]
        except (KeyError, ValueError):
            continue
        if abs((t - ko).total_seconds()) > 6 * 3600:
            continue
        sh, sa = name_score(home, fh), name_score(away, fa)
        sc = min(sh, sa) * 0.6 + (sh + sa) / 2 * 0.4
        if sc > best_sc:
            best, best_sc = f, sc
    return best if best_sc >= 0.62 else None


def _pct(v):
    try:
        return float(str(v).replace("%", "").strip()) / 100
    except (TypeError, ValueError):
        return None


def _apif_summary(pred, inj, fixture, name_score):
    out = {"fixtureId": fixture["fixture"]["id"]}
    if pred:
        pc = (pred.get("predictions") or {}).get("percent") or {}
        out["percent"] = {k: _pct(pc.get(k)) for k in ("home", "draw", "away")}
        out["advice"] = (pred.get("predictions") or {}).get("advice")
        out["winner"] = ((pred.get("predictions") or {}).get("winner") or {}).get("name")
    hn = fixture["teams"]["home"]["name"]
    players = {"home": [], "away": []}
    for i in inj or []:
        side = "home" if name_score(i.get("team", {}).get("name", ""), hn) >= 0.9 else "away"
        nm = (i.get("player") or {}).get("name")
        if nm and nm not in players[side]:
            players[side].append(nm)
    out["injuries"] = players
    return out


# ───────────────────────────── orquestación ─────────────────────────────
def enrich(soccer_cands, day, name_score):
    """Adjunta c['extra'] a los candidatos de los mejores partidos. No modifica odds/p."""
    keys = load_keys()
    if not keys["odds"] and not keys["apif"]:
        print("  • Fuentes extra: desactivadas (sin API keys; ver api_keys.example.json)")
        return
    odds = OddsAPI(keys["odds"]) if keys["odds"] else None
    apif = APIFootball(keys["apif"]) if keys["apif"] else None
    if odds and odds.active_sports() is None:
        odds = None

    by_ev = {}
    for c in soccer_cands:
        by_ev.setdefault(c["espnEventId"], []).append(c)

    def best_score(cs):
        real = [x for x in cs if not x["estimated"]] or cs
        return max(x["p"] + 1.5 * x["ev"] for x in real)

    top = sorted(by_ev.values(), key=best_score, reverse=True)[:MAX_EVENTS]
    apif_fixtures = apif.fixtures(day) if apif else []
    found_o = found_a = 0

    for idx, cs in enumerate(top):
        c0 = cs[0]
        ex = {}
        ko = c0["kickoff"].astimezone(timezone.utc)
        sk = ODDS_SPORT_KEYS.get(c0["espnLeague"])
        if odds and sk:
            ev = _find_odds_event(odds.league_odds(sk, day), c0["home"], c0["away"], ko, name_score)
            if ev:
                ex["oddsapi"] = ev
                found_o += 1
                if idx < MAX_DC_EVENTS:
                    dc = odds.event_market(sk, ev["id"], "double_chance", day)
                    if dc:
                        ex["oddsapiDC"] = dc
        if apif:
            fx = _find_fixture(apif_fixtures, c0["home"], c0["away"], ko, name_score)
            if fx and idx < MAX_APIF_EVENTS:
                ex["apif"] = _apif_summary(apif.predictions(fx["fixture"]["id"]),
                                           apif.injuries(fx["fixture"]["id"]), fx, name_score)
                found_a += 1
        if ex:
            for c in cs:
                c["extra"] = ex

    msg = f"  • Fuentes extra: {len(top)} partidos revisados"
    if odds:
        msg += f" | Odds API: {found_o} con cuotas multicasa"
        if _state["odds_remaining"] is not None:
            msg += f" (créditos restantes: {_state['odds_remaining']})"
    if apif:
        msg += f" | API-Football: {found_a} con predicción/lesiones"
    print(msg)


def _market_side(c):
    """-> ('home'|'away'|None, tipo) para comparar contra fuentes externas."""
    mk = c.get("market", {})
    t, side = mk.get("type"), mk.get("side")
    if t == "COMBO":
        t = "ML" if mk.get("subtype") == "ML_OVER" else "DC"
    return t, side


def describe(c):
    """Devuelve (nota_texto, dict_comparación) para un candidato; ('', None) si no hay datos."""
    ex = c.get("extra")
    if not ex:
        return "", None
    mk = c.get("market", {})
    t, side = _market_side(c)
    home, away = c["home"], c["away"]
    cmp_, parts, warns = {}, [], []

    ev = ex.get("oddsapi")
    if ev:
        from difflib import SequenceMatcher
        def is_team(name, team):
            return SequenceMatcher(None, name.lower(), team.lower()).ratio() > 0.6 or team.lower() in name.lower()

        summ = None
        if mk.get("type") == "ML":
            team = home if side == "home" else away
            summ = _summarize(ev, "h2h", lambda n: is_team(n, team))
        elif mk.get("type") == "TOTAL" and mk.get("line") is not None:
            want = "over" if side == "over" else "under"
            summ = _summarize(ev, "totals", lambda n: n.lower() == want, point=float(mk["line"]))
        if summ:
            cmp_["multicasa"] = summ
            txt = f"Odds API: mejor cuota {summ['best']:.2f} ({summ['book']}), promedio {summ['avg']:.2f} en {summ['n']} casas"
            if summ.get("consensusP") is not None:
                txt += f"; consenso sin margen {summ['consensusP']:.0%}"
                if abs(summ["consensusP"] - c["p"]) > 0.08:
                    warns.append(f"⚠️ consenso de casas {summ['consensusP']:.0%} vs modelo {c['p']:.0%}")
            parts.append(txt)

    dcev = ex.get("oddsapiDC")
    if dcev and t == "DC" and side in ("1X", "X2"):
        team = home if side == "1X" else away
        s = _summarize(dcev, "double_chance",
                       lambda n: "draw" in n.lower() and (team.lower() in n.lower() or
                                                          ("home" if side == "1X" else "away") in n.lower()),
                       devig=False)
        if s:
            cmp_["dobleOportunidadReal"] = s
            parts.append(f"{side} real {s['best']:.2f} ({s['book']})")

    af = ex.get("apif")
    if af:
        cmp_["apiFootball"] = af
        pc = af.get("percent") or {}
        if pc.get("home") is not None:
            ph, pd_, pa = pc["home"], pc.get("draw") or 0.0, pc["away"]
            segs = f"{c['home']} {ph:.0%}/emp {pd_:.0%}/{c['away']} {pa:.0%}"
            parts.append(f"API-Football: {segs}" + (f" — «{af['advice']}»" if af.get("advice") else ""))
            if t == "ML":
                mine = ph if side == "home" else pa
            elif t == "DC":
                mine = (ph + pd_) if side == "1X" else (pa + pd_)
            else:
                mine = None
            if mine is not None and mine < 0.45:
                warns.append(f"⚠️ API-Football solo da {mine:.0%} a este resultado")
        inj = af.get("injuries") or {}
        for lbl, team in (("home", home), ("away", away)):
            if inj.get(lbl):
                names = ", ".join(inj[lbl][:3]) + ("…" if len(inj[lbl]) > 3 else "")
                parts.append(f"bajas {team}: {len(inj[lbl])} ({names})")
        if not any(inj.get(k) for k in ("home", "away")) and pc:
            parts.append("sin bajas reportadas")

    if warns:
        cmp_["warnings"] = warns
    note = "; ".join(parts + warns)
    return note, (cmp_ or None)
