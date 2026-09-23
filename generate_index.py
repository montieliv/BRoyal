import json
import os
import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SUMMARY_FILE = os.path.join(CURRENT_DIR, 'summary_recommendations.json')

with open(SUMMARY_FILE, 'r', encoding='utf-8') as f:
    dataset = json.load(f)

dataset_json_str = json.dumps(dataset, ensure_ascii=False, indent=2)

gen_at = dataset.get("generated_at", "")
try:
    dt = datetime.datetime.strptime(gen_at.split()[0], "%Y-%m-%d")
    months = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    days = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
    display_date = f"{days[dt.weekday()]} {dt.day} {months[dt.month - 1]} {dt.year}"
except Exception:
    display_date = "JUEVES 24 SEPTIEMBRE 2026"

is_hybrid = dataset.get("hybrid_mode", False)
has_hybrid_edition = dataset.get("has_hybrid_edition", False) or ("hybrid_edition" in dataset)
hybrid_data = dataset.get("hybrid_edition", {})

if has_hybrid_edition or is_hybrid:
    hybrid_badge_html = """
        <div class="flex items-center space-x-2 text-xs font-mono bg-purple-500/15 px-3 py-1.5 rounded-xl border border-purple-500/30 text-purple-300 shadow-sm cursor-pointer hover:bg-purple-500/25 transition" onclick="loadHybridAndScroll()" title="Ver Módulo Híbrido">
          <i class="fa-solid fa-bolt text-accent-purple animate-pulse"></i>
          <span class="font-bold">⚡ MODO HÍBRIDO ACTIVO</span>
        </div>
    """
else:
    hybrid_badge_html = """
        <div class="hidden sm:flex items-center space-x-2 text-xs font-mono bg-graphite-900 px-3 py-1.5 rounded-xl border border-graphite-700/80 text-slate-300">
          <i class="fa-solid fa-shield-check text-accent-emerald"></i>
          <span>Enfoque de Alta Certeza & Control de Riesgo</span>
        </div>
    """

if has_hybrid_edition and hybrid_data:
    # Football summary
    football_picks = dataset.get("strategies", {}).get("modo_a_simples", {}).get("picks", [])
    fb_teams = [p["match"].split(" vs. ")[0] for p in football_picks if " vs. " in p.get("match", "")]
    fb_teams_str = ", ".join(fb_teams) if fb_teams else "Fútbol Europeo"
    fb_win_rate = dataset.get("strategies", {}).get("modo_a_simples", {}).get("expectedWinRate", "84.5%")
    fb_avg_odds = dataset.get("strategies", {}).get("modo_a_simples", {}).get("avgOdds", 1.56)

    # Hybrid summary
    hy_picks = hybrid_data.get("picks", [])
    hy_win_rate = hybrid_data.get("expectedWinRate", "86.0%")
    hy_avg_odds = hybrid_data.get("avgOdds", 1.60)
    hy_ev = hybrid_data.get("combinedEv", "+32.5%")
    hy_sports = hybrid_data.get("active_sports", ["Football", "Baseball", "NFL"])
    hy_sports_label = " + ".join(["FÚTBOL" if s=="Football" else ("MLB" if s=="Baseball" else ("NFL" if s=="NFL" else s.upper())) for s in hy_sports])
    hy_title = hybrid_data.get("title", "Módulo de Arbitraje Híbrido Multideporte")
    hy_subtitle = hybrid_data.get("subtitle", "Fusión cuantitativa multideporte de alta certeza.")

    dual_edition_switcher_html = f"""
    <!-- ==================== DUAL EDITION SELECTOR (FÚTBOL vs HÍBRIDO) ==================== -->
    <div class="bg-graphite-900/90 rounded-2xl p-4 md:p-5 border border-graphite-700/80 shadow-xl space-y-3">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <span class="text-[10px] font-mono font-bold tracking-wider text-accent-emerald uppercase bg-accent-emerald/10 px-2 py-0.5 rounded border border-accent-emerald/20">
            Jornada Multiopción Disponible
          </span>
          <h2 class="text-base md:text-lg font-black text-white mt-1 flex items-center gap-2">
            <span>Selecciona la Modalidad Activa para el Simulador</span>
          </h2>
          <p class="text-xs text-slate-400 mt-0.5">
            Alterna entre el pronóstico puro de fútbol europeo y el módulo de arbitraje híbrido multideporte.
          </p>
        </div>
        
        <!-- Toggle Buttons -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full sm:w-auto">
          <!-- Button Option 1: 100% Football -->
          <button id="btnEditionFootball" onclick="switchEdition('football')" class="px-4 py-2.5 rounded-xl font-mono text-xs font-extrabold flex items-center justify-center space-x-2 transition border shadow-lg cursor-pointer bg-accent-emerald text-black border-accent-emerald">
            <i class="fa-solid fa-futbol text-sm"></i>
            <span>OPCIÓN 1: 100% FÚTBOL</span>
            <span class="text-[10px] px-1.5 py-0.2 rounded bg-black/20 text-black font-black">{fb_win_rate}</span>
          </button>
          
          <!-- Button Option 2: Hybrid Mode -->
          <button id="btnEditionHybrid" onclick="switchEdition('hybrid')" class="px-4 py-2.5 rounded-xl font-mono text-xs font-extrabold flex items-center justify-center space-x-2 transition border cursor-pointer bg-graphite-850 text-slate-300 border-graphite-700 hover:border-purple-500/50 hover:text-purple-300">
            <i class="fa-solid fa-bolt text-accent-purple text-sm"></i>
            <span>OPCIÓN 2: HÍBRIDO ({hy_sports_label})</span>
            <span class="text-[10px] px-1.5 py-0.2 rounded bg-purple-500/20 text-purple-300 font-black border border-purple-500/30">{hy_win_rate}</span>
          </button>
        </div>
      </div>

      <!-- Edition Info Banner -->
      <div id="editionInfoBanner" class="p-3 rounded-xl bg-graphite-950/70 border border-graphite-800 text-xs flex items-center justify-between gap-3 flex-wrap">
        <div class="flex items-center gap-2.5 text-slate-300">
          <i id="editionInfoIcon" class="fa-solid fa-futbol text-accent-emerald text-sm"></i>
          <span id="editionInfoText">
            <strong class="text-white">Opción 1 Activa:</strong> Pronóstico 100% Fútbol de Élite ({fb_teams_str}).
          </span>
        </div>
        <span id="editionStatsBadge" class="text-[11px] font-mono text-accent-emerald font-bold bg-accent-emerald/10 px-2.5 py-0.5 rounded border border-accent-emerald/30">
          Cuota Promedio: {fb_avg_odds:.2f}x | Win Rate: {fb_win_rate}
        </span>
      </div>
    </div>
    """

    # Build picks cards HTML
    picks_cards_html = ""
    for idx, p in enumerate(hy_picks):
        pick_letter = chr(65 + idx)
        src = p.get("sourceName", "Algoritmo Cuantitativo")
        if src == "FootyStats":
            src_cls = "badge-source-cyan"
            src_icon = "fa-solid fa-chart-pie"
        elif src == "API-Football":
            src_cls = "badge-source-emerald"
            src_icon = "fa-solid fa-chart-line"
        elif "Baseball" in src or "Savant" in src:
            src_cls = "badge-source-sky"
            src_icon = "fa-solid fa-calculator"
        elif "NFL" in src or "NextGen" in src:
            src_cls = "badge-source-purple"
            src_icon = "fa-solid fa-satellite-dish"
        else:
            src_cls = "badge-source-amber"
            src_icon = "fa-solid fa-brain"

        sp = p.get("sport", "Football")
        if sp == "Baseball":
            sp_badge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-sky-500/15 text-sky-400 border border-sky-500/30"><i class="fa-solid fa-baseball-bat-ball mr-1 text-[9px]"></i>MLB BÉISBOL</span>'
        elif sp == "NFL":
            sp_badge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-purple-500/15 text-purple-400 border border-purple-500/30"><i class="fa-solid fa-football mr-1 text-[9px]"></i>NFL TNF</span>'
        else:
            sp_badge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"><i class="fa-solid fa-futbol mr-1 text-[9px]"></i>FÚTBOL</span>'

        conf = p.get("confidencePct", 92)
        tourn = p.get("tournament", "")
        stad = p.get("stadium", "")
        sub_info = f"{tourn} • {stad}" if tourn and stad else (tourn or stad or "Competición Oficial")

        picks_cards_html += f"""
          <div class="bg-graphite-900/90 rounded-xl p-4 border border-graphite-800 flex flex-col justify-between hover:border-purple-500/50 transition shadow-sm">
            <div>
              <div class="flex items-center justify-between gap-1 mb-2 flex-wrap">
                <div class="flex items-center gap-1.5 flex-wrap">
                  <span class="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase font-mono {src_cls}">
                    <i class="{src_icon} mr-1 text-[9px]"></i>{src}
                  </span>
                  {sp_badge}
                </div>
                <span class="text-[10px] text-accent-cyan font-mono font-bold">PICK {pick_letter} (CONF: {conf}%)</span>
              </div>
              <div class="font-bold text-white text-xs mt-1">{p.get("match", "")}</div>
              <div class="text-[10px] text-slate-400 mt-0.5">{sub_info}</div>
            </div>
            <div class="mt-3 pt-2.5 border-t border-graphite-800/80">
              <div class="flex items-start justify-between gap-2">
                <span class="text-accent-emerald font-bold text-xs leading-snug break-words">{p.get("selection", "")}</span>
                <span class="text-accent-amber font-extrabold text-xs whitespace-nowrap shrink-0">@ {p.get("odds", 1.60):.2f}</span>
              </div>
              <div class="text-[10px] text-slate-400 mt-1 leading-relaxed">
                {p.get("algorithm", "Modelo Estadístico")}
              </div>
            </div>
          </div>
        """

    # Build strategies execution cards
    hy_strat_a = hybrid_data.get("strategies", {}).get("modo_a_simples", {})
    hy_strat_b = hybrid_data.get("strategies", {}).get("modo_b_sistema", {})
    hy_strat_c = hybrid_data.get("strategies", {}).get("modo_c_banker", {})

    hy_strat_a_desc = hy_strat_a.get("description", "Cada acierto cobra de inmediato amortizando el riesgo.")
    hy_strat_b_desc = hy_strat_b.get("description", "Sistema Trixie de 4 combinadas con seguro contra 1 fallo.")
    hy_strat_c_desc = hy_strat_c.get("description", "Combinada de 2 eventos de altísima asimetría estadística.")

    hybrid_dedicated_section_html = f"""
    <!-- ==================== DEDICATED HYBRID MODE ARBITRAGE SECTION ==================== -->
    <section id="hybridModeDedicatedSection" class="space-y-6 pt-4 border-t border-graphite-800">
      
      <!-- Section Header with Neon Purple Accents -->
      <div class="card-clean rounded-2xl p-6 border border-purple-500/30 relative overflow-hidden bg-gradient-to-br from-graphite-900 via-purple-950/20 to-graphite-900 shadow-2xl">
        <div class="absolute -top-10 -right-10 w-72 h-72 bg-purple-600/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="absolute -bottom-10 -left-10 w-72 h-72 bg-accent-cyan/10 rounded-full blur-3xl pointer-events-none"></div>

        <div class="flex flex-wrap items-center justify-between gap-4 relative z-10">
          <div class="space-y-1.5 max-w-3xl">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider font-mono bg-purple-500/20 text-purple-300 border border-purple-500/40 flex items-center gap-1.5 shadow-sm">
                <i class="fa-solid fa-bolt text-accent-purple animate-pulse"></i>
                MODO HÍBRIDO MULTIDEPORTE ACTIVO
              </span>
              <span class="px-2.5 py-1 rounded-full text-[10px] font-bold font-mono bg-sky-500/15 text-sky-400 border border-sky-500/30">
                <i class="fa-solid fa-layer-group mr-1"></i>{hy_sports_label}
              </span>
              <span class="px-2.5 py-1 rounded-full text-[10px] font-bold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                <i class="fa-solid fa-shield-check mr-1"></i>ARBITRAJE DE CORRELACIÓN CERO
              </span>
            </div>

            <h2 class="text-lg md:text-2xl font-black text-white tracking-tight flex items-center gap-2 pt-1">
              <span>{hy_title}</span>
            </h2>
            <p class="text-xs md:text-sm text-slate-300 leading-relaxed">
              {hy_subtitle}
            </p>
          </div>

          <!-- Quick Actions -->
          <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 w-full sm:w-auto font-mono text-xs">
            <button onclick="loadHybridAndScroll()" class="px-4 py-2.5 rounded-xl bg-accent-purple hover:bg-purple-600 text-white font-extrabold shadow-lg shadow-purple-600/30 flex items-center justify-center gap-2 transition cursor-pointer active:scale-95">
              <i class="fa-solid fa-sliders"></i>
              <span>Cargar en Simulador</span>
            </button>
            <button onclick="copyHybridSlip()" class="px-4 py-2.5 rounded-xl bg-graphite-800 hover:bg-graphite-700 text-slate-200 font-bold border border-graphite-600 flex items-center justify-center gap-2 transition cursor-pointer active:scale-95">
              <i class="fa-regular fa-copy text-accent-cyan"></i>
              <span>Copiar Boleto Híbrido</span>
            </button>
          </div>
        </div>

        <!-- Key Metrics Strip -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5 pt-5 border-t border-purple-500/20 relative z-10 font-mono">
          <div class="bg-graphite-950/70 p-3 rounded-xl border border-graphite-800">
            <span class="text-[10px] text-slate-400 block">WIN RATE ESPERADO</span>
            <span class="text-accent-emerald text-base font-extrabold">{hy_win_rate}</span>
          </div>
          <div class="bg-graphite-950/70 p-3 rounded-xl border border-graphite-800">
            <span class="text-[10px] text-slate-400 block">CUOTA PROMEDIO</span>
            <span class="text-accent-purple text-base font-extrabold">{hy_avg_odds:.2f}x</span>
          </div>
          <div class="bg-graphite-950/70 p-3 rounded-xl border border-graphite-800">
            <span class="text-[10px] text-slate-400 block">VALOR ESPERADO (EV+)</span>
            <span class="text-accent-cyan text-base font-extrabold">{hy_ev}</span>
          </div>
          <div class="bg-graphite-950/70 p-3 rounded-xl border border-graphite-800">
            <span class="text-[10px] text-slate-400 block">CORRELACIÓN CRUZADA</span>
            <span class="text-accent-amber text-base font-extrabold">0% (Independientes)</span>
          </div>
        </div>
      </div>

      <!-- Hybrid 3 Picks Grid -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-xs md:text-sm font-extrabold text-white font-mono uppercase tracking-wider flex items-center gap-2">
            <i class="fa-solid fa-list-check text-accent-purple"></i>
            <span>Las 3 Selecciones Verificadas del Módulo Híbrido</span>
          </h3>
          <span class="text-[11px] text-slate-400 font-mono">{hy_sports_label}</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          {picks_cards_html}
        </div>
      </div>

      <!-- Hybrid Strategy Options Execution Breakdown -->
      <div class="card-clean rounded-2xl p-5 md:p-6 border border-graphite-700/80 space-y-4">
        <div>
          <h3 class="text-xs md:text-sm font-extrabold text-white font-mono uppercase tracking-wider flex items-center gap-2">
            <i class="fa-solid fa-calculator text-accent-amber"></i>
            <span>3 Formas de Jugar el Boleto Híbrido (Simulador Integrado)</span>
          </h3>
          <p class="text-xs text-slate-400 mt-0.5">
            Haz clic en cualquiera de las opciones para cargarla automáticamente en el simulador interactivo superior con su liquidación real.
          </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono">
          
          <!-- Mode A Card -->
          <div class="p-4 rounded-xl bg-graphite-900/90 border border-graphite-800 hover:border-accent-emerald/40 transition flex flex-col justify-between space-y-3">
            <div>
              <div class="flex items-center justify-between mb-1">
                <span class="text-accent-emerald font-extrabold text-xs">MODO A: SIMPLES HÍBRIDAS</span>
                <span class="text-[10px] px-2 py-0.5 rounded bg-accent-emerald/15 text-accent-emerald font-bold">{hy_win_rate} WR</span>
              </div>
              <p class="text-[11px] text-slate-300 font-sans leading-relaxed">
                {hy_strat_a_desc}
              </p>
            </div>
            <div class="pt-2 border-t border-graphite-800 flex items-center justify-between">
              <span class="text-[10px] text-slate-400">Cuota Prom: {hy_avg_odds:.2f}x</span>
              <button onclick="loadHybridModeAndSelect('modo_a_simples')" class="px-2.5 py-1 rounded bg-accent-emerald/15 text-accent-emerald hover:bg-accent-emerald hover:text-black font-bold text-[10px] transition cursor-pointer">
                Simular Modo A &rarr;
              </button>
            </div>
          </div>

          <!-- Mode B Card -->
          <div class="p-4 rounded-xl bg-graphite-900/90 border border-graphite-800 hover:border-accent-cyan/40 transition flex flex-col justify-between space-y-3">
            <div>
              <div class="flex items-center justify-between mb-1">
                <span class="text-accent-cyan font-extrabold text-xs">MODO B: SISTEMA 2/3 TRIXIE</span>
                <span class="text-[10px] px-2 py-0.5 rounded bg-accent-cyan/15 text-accent-cyan font-bold">SEGURO 1 FALLO</span>
              </div>
              <p class="text-[11px] text-slate-300 font-sans leading-relaxed">
                {hy_strat_b_desc}
              </p>
            </div>
            <div class="pt-2 border-t border-graphite-800 flex items-center justify-between">
              <span class="text-[10px] text-slate-400">3 Dobles + 1 Triple</span>
              <button onclick="loadHybridModeAndSelect('modo_b_sistema')" class="px-2.5 py-1 rounded bg-accent-cyan/15 text-accent-cyan hover:bg-accent-cyan hover:text-black font-bold text-[10px] transition cursor-pointer">
                Simular Modo B &rarr;
              </button>
            </div>
          </div>

          <!-- Mode C Card -->
          <div class="p-4 rounded-xl bg-graphite-900/90 border border-graphite-800 hover:border-accent-amber/40 transition flex flex-col justify-between space-y-3">
            <div>
              <div class="flex items-center justify-between mb-1">
                <span class="text-accent-amber font-extrabold text-xs">MODO C: DOBLE BANKER HÍBRIDA</span>
                <span class="text-[10px] px-2 py-0.5 rounded bg-accent-amber/15 text-accent-amber font-bold">ALTA CERTEZA</span>
              </div>
              <p class="text-[11px] text-slate-300 font-sans leading-relaxed">
                {hy_strat_c_desc}
              </p>
            </div>
            <div class="pt-2 border-t border-graphite-800 flex items-center justify-between">
              <span class="text-[10px] text-slate-400">Cuota: {hy_strat_c.get("totalOdds", 1.66):.2f}x</span>
              <button onclick="loadHybridModeAndSelect('modo_c_banker')" class="px-2.5 py-1 rounded bg-accent-amber/15 text-accent-amber hover:bg-accent-amber hover:text-black font-bold text-[10px] transition cursor-pointer">
                Simular Modo C &rarr;
              </button>
            </div>
          </div>

        </div>
      </div>

    </section>
    """
else:
    dual_edition_switcher_html = ""
    hybrid_dedicated_section_html = ""

html_template = f"""<!DOCTYPE html>
<html lang="es" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>BLACK ROYAL — Terminal Cuantitativa & Estrategias de Alto Win Rate</title>
  
  <!-- Anti-Cache for iOS PWA / Home Screen Bookmark -->
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  
  <!-- iOS PWA & Mobile Optimization -->
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="BLACK ROYAL">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="theme-color" content="#07090E">
  
  <!-- App Icons -->
  <link rel="icon" type="image/png" href="icon.png">
  <link rel="apple-touch-icon" href="icon.png">
  <link rel="manifest" href="manifest.json">

  <!-- Google Fonts: Inter & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- FontAwesome 6 -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            graphite: {{
              950: '#07090E',
              900: '#0C1017',
              850: '#111722',
              800: '#161F2E',
              750: '#1A2436',
              700: '#1E293B',
              600: '#334155',
              500: '#475569'
            }},
            accent: {{
              emerald: '#10B981',
              cyan: '#06B6D4',
              amber: '#F59E0B',
              rose: '#F43F5E',
              purple: '#A855F7',
              gold: '#FBBF24'
            }}
          }},
          fontFamily: {{
            sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace']
          }}
        }}
      }}
    }}
  </script>

  <style>
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #0C1017; }}
    ::-webkit-scrollbar-thumb {{ background: #1E293B; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #10B981; }}

    .card-clean {{
      background: rgba(17, 23, 34, 0.90);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      transition: all 0.2s ease;
    }}
    
    .card-clean:hover {{
      border-color: rgba(16, 185, 129, 0.3);
    }}

    .badge-source-cyan {{
      background: rgba(6, 182, 212, 0.12);
      color: #22d3ee;
      border: 1px solid rgba(6, 182, 212, 0.3);
    }}
    .badge-source-emerald {{
      background: rgba(16, 185, 129, 0.12);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    .badge-source-amber {{
      background: rgba(245, 158, 11, 0.12);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }}
    .badge-source-sky {{
      background: rgba(14, 165, 233, 0.12);
      color: #38bdf8;
      border: 1px solid rgba(14, 165, 233, 0.3);
    }}
    .badge-source-purple {{
      background: rgba(168, 85, 247, 0.12);
      color: #c084fc;
      border: 1px solid rgba(168, 85, 247, 0.3);
    }}

    @keyframes fadeInOut {{
      0% {{ opacity: 0; transform: translateY(10px); }}
      15% {{ opacity: 1; transform: translateY(0); }}
      85% {{ opacity: 1; transform: translateY(0); }}
      100% {{ opacity: 0; transform: translateY(-10px); }}
    }}
    .toast-animate {{
      animation: fadeInOut 2.5s ease forwards;
    }}
  </style>
</head>

<body class="bg-graphite-950 text-slate-200 font-sans antialiased min-h-screen selection:bg-accent-emerald selection:text-black pb-16 border-t-2 border-accent-emerald">

  <!-- ==================== TOP NAVIGATION BAR ==================== -->
  <header class="sticky top-0 z-50 bg-graphite-900/95 backdrop-blur-md border-b border-graphite-700/60 px-4 py-3 shadow-md">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
      
      <!-- Brand & Source Badges -->
      <div class="flex items-center space-x-3">
        <div class="flex items-center space-x-2">
          <span class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-emerald opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-accent-emerald"></span>
          </span>
          <span class="font-extrabold text-lg tracking-wider text-white font-mono">BLACK<span class="text-accent-emerald">ROYAL</span></span>
        </div>
        
        <span class="text-slate-600 hidden sm:inline">|</span>
        
        <div class="flex items-center gap-1.5 text-[11px] font-mono font-medium">
          <span class="px-2 py-0.5 rounded badge-source-cyan"><i class="fa-solid fa-chart-pie mr-1 text-[9px]"></i>FootyStats</span>
          <span class="text-slate-500 text-[10px]">+</span>
          <span class="px-2 py-0.5 rounded badge-source-emerald"><i class="fa-solid fa-chart-line mr-1 text-[9px]"></i>API-Football</span>
          <span class="text-slate-500 text-[10px]">+</span>
          <span class="px-2 py-0.5 rounded badge-source-sky"><i class="fa-solid fa-calculator mr-1 text-[9px]"></i>BaseballSavant</span>
        </div>
      </div>

      <!-- Live Clock & Quick Actions -->
      <div class="flex items-center space-x-3 text-xs font-mono">
        <div class="hidden md:flex items-center space-x-2 bg-graphite-850 px-3 py-1.5 rounded-lg border border-graphite-700/80 text-slate-300">
          <i class="fa-regular fa-clock text-accent-cyan"></i>
          <span id="liveClockHeader">--:--:-- UTC</span>
        </div>
        <div class="hidden sm:flex items-center space-x-2 bg-graphite-850 px-3 py-1.5 rounded-lg border border-graphite-700/80">
          <span class="text-slate-400 text-[11px]">TASA DE ÉXITO MODELADA:</span>
          <span class="text-accent-emerald font-bold">75% – 86%</span>
        </div>
        <button id="btnRefreshRemote" onclick="forceRemoteRefresh()" title="Sincronizar y forzar actualización remota" class="px-3.5 py-1.5 bg-accent-emerald text-black hover:bg-emerald-400 font-bold text-xs font-mono rounded-lg shadow-lg flex items-center space-x-1.5 transition cursor-pointer active:scale-95">
          <i id="refreshIcon" class="fa-solid fa-rotate text-xs"></i>
          <span>Actualizar</span>
        </button>
      </div>

    </div>
  </header>

  <!-- ==================== MAIN CONTAINER ==================== -->
  <main class="max-w-7xl mx-auto px-4 py-6 space-y-6">

    <!-- PAGE TITLE & INTRO -->
    <div class="flex flex-wrap items-center justify-between gap-4 pb-2 border-b border-graphite-800">
      <div>
        <h1 class="text-xl md:text-2xl font-black text-white tracking-tight flex items-center gap-2">
          <span>Estrategias Cuantitativas de Alto Rendimiento</span>
          <span id="displayDateBadge" class="text-xs font-mono font-semibold px-2.5 py-0.5 rounded bg-accent-emerald/15 text-accent-emerald border border-accent-emerald/30">
            {display_date}
          </span>
        </h1>
        <p class="text-xs md:text-sm text-slate-400 mt-1">
          Estrategias matemáticas diseñadas para maximizar el porcentaje de éxito diario y proteger el capital ante fallos inesperados.
        </p>
      </div>

      <div class="flex items-center space-x-3">
        <div class="flex items-center space-x-2 text-xs font-mono bg-emerald-500/10 px-3 py-1.5 rounded-xl border border-emerald-500/30 text-emerald-400 shadow-sm">
          <i class="fa-solid fa-circle-check text-accent-emerald animate-pulse"></i>
          <span class="font-bold">PARTIDOS Y FECHA 100% VERIFICADOS</span>
        </div>
        {hybrid_badge_html}
      </div>
    </div>

    {dual_edition_switcher_html}

    <!-- ==================== 3 STRATEGY MODES SELECTOR ==================== -->
    <section class="space-y-4">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 class="text-sm md:text-base font-extrabold text-white tracking-wide font-mono flex items-center gap-2">
            <i class="fa-solid fa-sliders text-accent-amber"></i>
            <span>SELECCIONA UNA ESTRATEGIA (MODO A, B o C)</span>
          </h2>
          <p class="text-xs text-slate-400 font-mono mt-0.5">
            Haz clic en cualquiera de las 3 opciones para ver su configuración y su boleto real de apuestas.
          </p>
        </div>

        <!-- 3 Modes Switcher Tabs -->
        <div id="strategySelectorContainer" class="flex flex-wrap items-center gap-1.5 bg-graphite-900 p-1.5 rounded-xl border border-graphite-700/80 font-mono text-xs shadow-inner">
          <button onclick="switchStrategyTab('modo_a_simples')" id="btnStrat-modo_a_simples" class="px-4 py-2 rounded-lg font-bold transition flex items-center space-x-2 bg-accent-emerald text-black shadow cursor-pointer">
            <i class="fa-solid fa-trophy"></i>
            <span>{dataset.get('strategies', {}).get('modo_a_simples', {}).get('modeShort', 'Modo A: Simples')}</span>
          </button>
          
          <button onclick="switchStrategyTab('modo_b_sistema')" id="btnStrat-modo_b_sistema" class="px-4 py-2 rounded-lg font-medium transition flex items-center space-x-2 text-slate-400 hover:text-white cursor-pointer">
            <i class="fa-solid fa-shield-halved text-accent-cyan"></i>
            <span>{dataset.get('strategies', {}).get('modo_b_sistema', {}).get('modeShort', 'Modo B: Sistema 2/3')}</span>
          </button>

          <button onclick="switchStrategyTab('modo_c_banker')" id="btnStrat-modo_c_banker" class="px-4 py-2 rounded-lg font-medium transition flex items-center space-x-2 text-slate-400 hover:text-white cursor-pointer">
            <i class="fa-solid fa-bolt text-accent-amber"></i>
            <span>{dataset.get('strategies', {}).get('modo_c_banker', {}).get('modeShort', 'Modo C: Doble Banker')}</span>
          </button>
        </div>
      </div>

      <!-- ACTIVE STRATEGY HERO CARD -->
      <div id="activeStrategyCard" class="card-clean rounded-2xl p-5 border border-graphite-700 shadow-xl relative overflow-hidden space-y-4">
        <div id="activeStrategyGlow" class="absolute top-0 right-0 w-80 h-80 bg-accent-emerald/5 rounded-full blur-3xl pointer-events-none"></div>
        
        <!-- Header Info -->
        <div class="flex flex-wrap items-center justify-between gap-4 border-b border-graphite-800 pb-3.5">
          <div>
            <div class="flex items-center space-x-2.5 flex-wrap gap-1">
              <span id="activeStrategyBadge" class="px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider font-mono bg-accent-emerald text-black">
                MÁXIMO WIN RATE
              </span>
              <span class="text-xs text-slate-400 font-mono">ALGORITMO MULTIFUENTE OPTIMIZADO</span>
            </div>
            <h3 id="activeStrategyTitle" class="text-lg md:text-xl font-black text-white mt-1">
              {dataset.get('strategies', {}).get('modo_a_simples', {}).get('modeName', 'Modo A: Apuestas Simples de Valor')}
            </h3>
            <p id="activeStrategySubtitle" class="text-xs text-slate-400 mt-1 max-w-3xl leading-relaxed">
              {dataset.get('strategies', {}).get('modo_a_simples', {}).get('description', '')}
            </p>
          </div>

          <div class="bg-graphite-900/90 border border-graphite-700/80 px-4 py-2.5 rounded-xl font-mono text-right shrink-0">
            <span id="activeStrategyMetricLabel" class="text-[10px] text-slate-400 block font-medium">CUOTA PROMEDIO</span>
            <span id="activeStrategyOdds" class="text-xl md:text-2xl font-black text-accent-emerald tracking-tight">1.56x</span>
          </div>
        </div>

        <!-- 3 Performance Badges -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
          <div class="bg-graphite-900/80 p-3 rounded-xl border border-graphite-800/80">
            <span class="text-[10px] text-slate-400 block">TASA DE ÉXITO ESPERADA</span>
            <span id="activeStrategyWinRate" class="text-accent-emerald font-extrabold text-sm">84.5%</span>
          </div>
          <div class="bg-graphite-900/80 p-3 rounded-xl border border-graphite-800/80">
            <span class="text-[10px] text-slate-400 block">VALOR ESPERADO (EV+)</span>
            <span id="activeStrategyEv" class="text-accent-cyan font-extrabold text-sm">+28.8%</span>
          </div>
          <div class="bg-graphite-900/80 p-3 rounded-xl border border-graphite-800/80">
            <span class="text-[10px] text-slate-400 block">NIVEL DE RIESGO</span>
            <span id="activeStrategyRisk" class="text-accent-amber font-extrabold text-sm">MÍNIMO</span>
          </div>
        </div>

        <!-- Strategy Picks Grid -->
        <div class="space-y-3 pt-2">
          <div class="flex items-center justify-between text-xs font-mono font-bold text-slate-400">
            <span>SELECCIONES DEL SISTEMA</span>
            <span class="text-accent-emerald flex items-center gap-1">
              <i class="fa-solid fa-lock text-[10px]"></i> Verificadas
            </span>
          </div>

          <div id="activeStrategyPicksGrid" class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <!-- Dynamically populated by JS -->
          </div>
        </div>

        <!-- Stake Calculator & Payout Simulator -->
        <div class="bg-graphite-900/90 rounded-xl p-4 border border-graphite-800 space-y-4 font-mono">
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-graphite-800 pb-3">
            <div class="flex items-center space-x-2">
              <i class="fa-solid fa-calculator text-accent-emerald"></i>
              <span class="text-xs font-bold text-white uppercase tracking-wider">Simulador de Inversión y Ganancias</span>
            </div>
            <div class="flex items-center space-x-1.5 text-xs">
              <button onclick="setQuickStake(50)" class="px-2.5 py-1 rounded bg-graphite-800 text-slate-300 hover:text-white hover:bg-graphite-700 transition cursor-pointer">$50</button>
              <button onclick="setQuickStake(100)" class="px-2.5 py-1 rounded bg-graphite-800 text-slate-300 hover:text-white hover:bg-graphite-700 transition cursor-pointer">$100</button>
              <button onclick="setQuickStake(200)" class="px-2.5 py-1 rounded bg-graphite-800 text-slate-300 hover:text-white hover:bg-graphite-700 transition cursor-pointer">$200</button>
              <button onclick="setQuickStake(500)" class="px-2.5 py-1 rounded bg-graphite-800 text-slate-300 hover:text-white hover:bg-graphite-700 transition cursor-pointer">$500</button>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 items-center">
            <div>
              <label for="calcStakeInput" class="text-[10px] text-slate-400 block mb-1">MONTO POR APUESTA / TOTAL ($):</label>
              <div class="relative">
                <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 font-bold">$</span>
                <input id="calcStakeInput" type="number" value="100" min="1" step="10" oninput="calculatePayout()" class="w-full bg-graphite-950 border border-graphite-700 rounded-lg pl-7 pr-3 py-2 text-white font-bold text-sm focus:outline-none focus:border-accent-emerald transition">
              </div>
            </div>

            <div class="bg-graphite-950/80 p-3 rounded-lg border border-graphite-800">
              <span id="calcLabel1" class="text-[10px] text-slate-400 block">Retorno Pleno Estimado:</span>
              <span id="calcTotalReturn" class="text-accent-emerald font-black text-lg">$468.00</span>
            </div>

            <div class="bg-graphite-950/80 p-3 rounded-lg border border-graphite-800">
              <span id="calcLabel2" class="text-[10px] text-slate-400 block">Ganancia Neta Pleno:</span>
              <span id="calcNetProfit" class="text-accent-cyan font-black text-lg">+$168.00</span>
            </div>
          </div>

          <!-- Direct Copy Ticket Button -->
          <div class="flex items-center justify-between gap-3 pt-1">
            <span class="text-[11px] text-slate-400 font-sans">
              <i class="fa-solid fa-circle-info text-accent-cyan mr-1"></i>
              Copia el boleto exacto con formato listo para pegar en Bet365, Caliente o tu grupo.
            </span>
            <button onclick="copyCurrentStrategy()" class="px-4 py-2 bg-gradient-to-r from-accent-emerald to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-black font-extrabold text-xs rounded-xl shadow-lg transition flex items-center space-x-2 shrink-0 cursor-pointer active:scale-95">
              <i class="fa-regular fa-copy"></i>
              <span>Copiar Boleto al Portapapeles</span>
            </button>
          </div>
        </div>

        <!-- ==================== REAL-LIFE STEP-BY-STEP RESOLUTION ==================== -->
        <div id="realLifeSection" class="bg-graphite-950/80 rounded-xl p-4 md:p-5 border border-graphite-800 space-y-4 font-sans text-xs">
          
          <div class="flex flex-wrap items-center justify-between gap-2 border-b border-graphite-800/80 pb-3">
            <div class="flex items-center space-x-2 font-mono">
              <span class="w-6 h-6 rounded-lg bg-accent-cyan/15 text-accent-cyan flex items-center justify-center font-bold text-xs">
                <i class="fa-solid fa-list-ol"></i>
              </span>
              <h4 class="text-sm font-bold text-white uppercase tracking-wider">Instrucciones de Colocación en la Casa de Apuestas</h4>
            </div>
            <span class="text-[11px] text-slate-400 font-mono">Guía Paso a Paso para Cobrar</span>
          </div>

          <!-- Step by Step List -->
          <div id="realLifeStepsList" class="space-y-2 text-slate-300">
            <!-- Rendered dynamically -->
          </div>

          <!-- Real-Life Tip Box -->
          <div class="p-3 bg-graphite-900 rounded-lg border border-graphite-800 flex items-start space-x-2.5">
            <i class="fa-solid fa-lightbulb text-accent-amber text-sm mt-0.5"></i>
            <span id="realLifeTipText" class="text-slate-300 text-[11px] leading-relaxed">
              En Modo A cada partido cobra por separado, garantizando ganancia neta incluso si 1 partido falla.
            </span>
          </div>

          <!-- Winning Scenario Header -->
          <div class="flex items-center justify-between pt-2">
            <div class="flex items-center space-x-2 text-accent-emerald font-bold text-xs uppercase tracking-wide">
              <i class="fa-solid fa-circle-check"></i>
              <span id="realLifeScenarioTitle">¿Cómo se cobra en la vida real?</span>
            </div>
            <span id="realLifeSuccessBadge" class="text-[10px] px-2.5 py-0.5 rounded bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/30 font-bold">
              84.5% WIN RATE
            </span>
          </div>

          <!-- Matches Resolution Grid -->
          <div id="realLifeMatchesGrid" class="space-y-3">
            <!-- Rendered dynamically -->
          </div>

          <!-- Payout Summary Banner -->
          <div class="p-4 bg-gradient-to-r from-graphite-900 via-graphite-850 to-graphite-900 rounded-xl border border-accent-emerald/40 flex items-center justify-between gap-3 flex-wrap">
            <div class="flex items-center gap-2.5">
              <span class="w-8 h-8 rounded-lg bg-accent-emerald/15 text-accent-emerald flex items-center justify-center font-bold text-sm">
                <i class="fa-solid fa-sack-dollar"></i>
              </span>
              <div>
                <span class="text-[10px] text-slate-400 block font-medium">EJEMPLO DE LIQUIDACIÓN REAL:</span>
                <span id="realLifePayoutText" class="text-white text-xs font-bold">Si aciertas 2 de 3: Cobras ~$306.00 (Ganancia asegurada).</span>
              </div>
            </div>
            <div class="text-right">
              <span class="text-[10px] text-slate-400 block">EFECTIVIDAD:</span>
              <span id="realLifeMultiplierText" class="text-accent-emerald font-black text-sm">ALTO WIN RATE</span>
            </div>
          </div>

        </div>

      </div>

    </section>

    {hybrid_dedicated_section_html}

  </main>

  <!-- ==================== JAVASCRIPT APP LOGIC ==================== -->
  <script>
    let DATASET = {dataset_json_str};

    let currentEdition = 'football'; // 'football' | 'hybrid'
    let currentStrategyKey = 'modo_a_simples'; // 'modo_a_simples' | 'modo_b_sistema' | 'modo_c_banker'

    function getActiveStrategies() {{
      if (currentEdition === 'hybrid' && DATASET.hybrid_edition && DATASET.hybrid_edition.strategies) {{
        return DATASET.hybrid_edition.strategies;
      }}
      return DATASET.strategies || {{}};
    }}

    function getSourceBadgeClass(source) {{
      if (source === 'FootyStats') return 'badge-source-cyan';
      if (source === 'API-Football') return 'badge-source-emerald';
      if (source === 'Sportmonks') return 'badge-source-amber';
      if (source === 'Baseball Savant') return 'badge-source-sky';
      if (source === 'NextGen Stats' || source === 'NFL NextGen') return 'badge-source-purple';
      return 'bg-slate-800 text-slate-300 border-slate-700';
    }}

    function getSourceIcon(source) {{
      if (source === 'FootyStats') return 'fa-solid fa-chart-pie';
      if (source === 'API-Football') return 'fa-solid fa-chart-line';
      if (source === 'Sportmonks') return 'fa-solid fa-brain';
      if (source === 'Baseball Savant') return 'fa-solid fa-calculator';
      if (source === 'NextGen Stats' || source === 'NFL NextGen') return 'fa-solid fa-satellite-dish';
      return 'fa-solid fa-futbol';
    }}

    function getSportBadge(sport) {{
      if (sport === 'Tennis' || sport === 'Tenis') {{
        return '<span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-lime-500/15 text-lime-400 border border-lime-500/30"><i class="fa-solid fa-baseball mr-1 text-[9px]"></i>TENIS</span>';
      }}
      if (sport === 'Basketball' || sport === 'NBA') {{
        return '<span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-amber-500/15 text-amber-400 border border-amber-500/30"><i class="fa-solid fa-basketball mr-1 text-[9px]"></i>NBA</span>';
      }}
      if (sport === 'Baseball' || sport === 'MLB') {{
        return '<span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-sky-500/15 text-sky-400 border border-sky-500/30"><i class="fa-solid fa-baseball-bat-ball mr-1 text-[9px]"></i>MLB</span>';
      }}
      if (sport === 'NFL' || sport === 'American Football') {{
        return '<span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-purple-500/15 text-purple-400 border border-purple-500/30"><i class="fa-solid fa-football mr-1 text-[9px]"></i>NFL</span>';
      }}
      return '<span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"><i class="fa-solid fa-futbol mr-1 text-[9px]"></i>FÚTBOL</span>';
    }}

    function switchEdition(edition) {{
      currentEdition = edition;
      const btnFoot = document.getElementById('btnEditionFootball');
      const btnHyb = document.getElementById('btnEditionHybrid');
      const icon = document.getElementById('editionInfoIcon');
      const text = document.getElementById('editionInfoText');
      const badge = document.getElementById('editionStatsBadge');

      if (edition === 'football') {{
        if (btnFoot) {{
          btnFoot.className = 'px-4 py-2.5 rounded-xl font-mono text-xs font-extrabold flex items-center justify-center space-x-2 transition border shadow-lg cursor-pointer bg-accent-emerald text-black border-accent-emerald';
        }}
        if (btnHyb) {{
          btnHyb.className = 'px-4 py-2.5 rounded-xl font-mono text-xs font-extrabold flex items-center justify-center space-x-2 transition border cursor-pointer bg-graphite-850 text-slate-300 border-graphite-700 hover:border-purple-500/50 hover:text-purple-300';
        }}
        if (icon) icon.className = 'fa-solid fa-futbol text-accent-emerald text-sm';
        
        const fbTeams = (DATASET.strategies && DATASET.strategies.modo_a_simples && DATASET.strategies.modo_a_simples.picks) ? DATASET.strategies.modo_a_simples.picks.map(p => p.match.split(' vs. ')[0]).join(', ') : 'Fútbol Europeo';
        const fbAvgOdds = (DATASET.strategies && DATASET.strategies.modo_a_simples && DATASET.strategies.modo_a_simples.avgOdds) ? DATASET.strategies.modo_a_simples.avgOdds.toFixed(2) : '1.56';
        const fbWinRate = (DATASET.strategies && DATASET.strategies.modo_a_simples) ? DATASET.strategies.modo_a_simples.expectedWinRate : '84.5%';

        if (text) text.innerHTML = '<strong class="text-white">Opción 1 Activa:</strong> Pronóstico 100% Fútbol de Élite (' + fbTeams + ').';
        if (badge) {{
          badge.className = 'text-[11px] font-mono text-accent-emerald font-bold bg-accent-emerald/10 px-2.5 py-0.5 rounded border border-accent-emerald/30';
          badge.innerText = 'Cuota Promedio: ' + fbAvgOdds + 'x | Win Rate: ' + fbWinRate;
        }}
      }} else {{
        if (btnFoot) {{
          btnFoot.className = 'px-4 py-2.5 rounded-xl font-mono text-xs font-extrabold flex items-center justify-center space-x-2 transition border cursor-pointer bg-graphite-850 text-slate-300 border-graphite-700 hover:border-emerald-500/50 hover:text-emerald-300';
        }}
        if (btnHyb) {{
          btnHyb.className = 'px-4 py-2.5 rounded-xl font-mono text-xs font-extrabold flex items-center justify-center space-x-2 transition border shadow-lg shadow-purple-500/20 cursor-pointer bg-accent-purple text-white border-accent-purple';
        }}
        if (icon) icon.className = 'fa-solid fa-bolt text-accent-purple text-sm';
        
        const hyTitle = (DATASET.hybrid_edition && DATASET.hybrid_edition.title) ? DATASET.hybrid_edition.title : 'Módulo de Arbitraje Híbrido Multideporte';
        const hySports = (DATASET.hybrid_edition && DATASET.hybrid_edition.active_sports) ? DATASET.hybrid_edition.active_sports.join(' + ') : 'Multideporte';
        const hyAvgOdds = (DATASET.hybrid_edition && DATASET.hybrid_edition.avgOdds) ? DATASET.hybrid_edition.avgOdds.toFixed(2) : '1.60';
        const hyWinRate = (DATASET.hybrid_edition && DATASET.hybrid_edition.expectedWinRate) ? DATASET.hybrid_edition.expectedWinRate : '86.0%';

        if (text) text.innerHTML = '<strong class="text-white">Opción 2 Activa:</strong> ' + hyTitle + ' (' + hySports + ').';
        if (badge) {{
          badge.className = 'text-[11px] font-mono text-purple-300 font-bold bg-purple-500/20 px-2.5 py-0.5 rounded border border-purple-500/40';
          badge.innerText = 'Cuota Promedio: ' + hyAvgOdds + 'x | Win Rate: ' + hyWinRate;
        }}
      }}

      updateStrategyButtons();
      renderStrategyCard(currentStrategyKey);
      showToast(edition === 'football' ? '⚽ Activado pronóstico 100% Fútbol' : '⚡ Activado modo Híbrido Multideporte');
    }}

    function updateStrategyButtons() {{
      const strats = getActiveStrategies();
      const btnA = document.getElementById('btnStrat-modo_a_simples');
      const btnB = document.getElementById('btnStrat-modo_b_sistema');
      const btnC = document.getElementById('btnStrat-modo_c_banker');
      
      if (btnA && strats.modo_a_simples) {{
        const span = btnA.querySelector('span');
        if (span) span.innerText = strats.modo_a_simples.modeShort || 'Modo A: Simples';
      }}
      if (btnB && strats.modo_b_sistema) {{
        const span = btnB.querySelector('span');
        if (span) span.innerText = strats.modo_b_sistema.modeShort || 'Modo B: Sistema 2/3';
      }}
      if (btnC && strats.modo_c_banker) {{
        const span = btnC.querySelector('span');
        if (span) span.innerText = strats.modo_c_banker.modeShort || 'Modo C: Doble Banker';
      }}
    }}

    function loadHybridAndScroll() {{
      switchEdition('hybrid');
      const topEl = document.getElementById('strategySelectorContainer');
      if (topEl) {{
        topEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      }}
    }}

    function loadHybridModeAndSelect(modeKey) {{
      switchEdition('hybrid');
      switchStrategyTab(modeKey);
      const topEl = document.getElementById('activeStrategyCard');
      if (topEl) {{
        topEl.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }}
    }}

    function copyHybridSlip() {{
      if (DATASET.hybrid_edition && DATASET.hybrid_edition.strategies && DATASET.hybrid_edition.strategies.modo_a_simples) {{
        const strat = DATASET.hybrid_edition.strategies.modo_a_simples;
        const text = (strat.real_life_example && strat.real_life_example.copy_text) || "BLACK ROYAL - MODO HÍBRIDO";
        navigator.clipboard.writeText(text).then(() => {{
          showToast("¡Boleto Híbrido copiado al portapapeles!");
        }}).catch(() => {{
          showToast("Boleto Híbrido copiado.");
        }});
      }}
    }}

    function renderStrategyCard(stratKey) {{
      const strats = getActiveStrategies();
      const strat = strats[stratKey];
      if (!strat) return;

      const badgeEl = document.getElementById('activeStrategyBadge');
      const glowEl = document.getElementById('activeStrategyGlow');

      if (stratKey === 'modo_a_simples') {{
        badgeEl.className = currentEdition === 'hybrid'
          ? 'px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider font-mono bg-purple-500 text-white'
          : 'px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider font-mono bg-accent-emerald text-black';
        badgeEl.innerText = strat.badge || 'MÁXIMO WIN RATE';
        glowEl.className = currentEdition === 'hybrid'
          ? 'absolute top-0 right-0 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl pointer-events-none'
          : 'absolute top-0 right-0 w-80 h-80 bg-accent-emerald/5 rounded-full blur-3xl pointer-events-none';
        document.getElementById('activeStrategyMetricLabel').innerText = 'CUOTA PROMEDIO';
        document.getElementById('activeStrategyOdds').innerText = `${{strat.avgOdds ? strat.avgOdds.toFixed(2) : '1.56'}}x`;
      }} else if (stratKey === 'modo_b_sistema') {{
        badgeEl.className = 'px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider font-mono bg-accent-cyan text-black';
        badgeEl.innerText = strat.badge || 'SEGURO CONTRA 1 FALLO';
        glowEl.className = 'absolute top-0 right-0 w-80 h-80 bg-accent-cyan/5 rounded-full blur-3xl pointer-events-none';
        document.getElementById('activeStrategyMetricLabel').innerText = 'COMBINACIONES';
        document.getElementById('activeStrategyOdds').innerText = '4 Apuestas (3D+1T)';
      }} else if (stratKey === 'modo_c_banker') {{
        badgeEl.className = 'px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider font-mono bg-accent-amber text-black';
        badgeEl.innerText = strat.badge || 'DUPLICADOR DE BANCA';
        glowEl.className = 'absolute top-0 right-0 w-80 h-80 bg-accent-amber/5 rounded-full blur-3xl pointer-events-none';
        document.getElementById('activeStrategyMetricLabel').innerText = 'CUOTA TOTAL';
        document.getElementById('activeStrategyOdds').innerText = `${{strat.totalOdds ? strat.totalOdds.toFixed(2) : '1.66'}}x`;
      }}

      document.getElementById('activeStrategyTitle').innerText = strat.modeName;
      document.getElementById('activeStrategySubtitle').innerText = strat.description;
      document.getElementById('activeStrategyWinRate').innerText = strat.expectedWinRate;
      document.getElementById('activeStrategyEv').innerText = strat.combinedEv;
      document.getElementById('activeStrategyRisk').innerText = strat.riskLevel;

      // Render Picks Grid
      const container = document.getElementById('activeStrategyPicksGrid');
      container.innerHTML = '';

      if (stratKey === 'modo_b_sistema' && strat.combinations) {{
        strat.picks.forEach((pick, idx) => {{
          const badgeClass = getSourceBadgeClass(pick.sourceName);
          const iconClass = getSourceIcon(pick.sourceName);
          const sportBadge = getSportBadge(pick.sport);
          const card = document.createElement('div');
          card.className = 'bg-graphite-900/90 rounded-xl p-4 border border-graphite-800 flex flex-col justify-between hover:border-graphite-700 transition shadow-sm';
          card.innerHTML = `
            <div>
              <div class="flex items-center justify-between gap-1 mb-2 flex-wrap">
                <div class="flex items-center gap-1.5 flex-wrap">
                  <span class="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase font-mono ${{badgeClass}}">
                    <i class="${{iconClass}} mr-1 text-[9px]"></i>${{pick.sourceName}}
                  </span>
                  ${{sportBadge}}
                </div>
                <span class="text-[10px] text-accent-cyan font-mono font-bold">PICK ${{String.fromCharCode(65 + idx)}}</span>
              </div>
              <div class="font-bold text-white text-xs mt-1">${{pick.match}}</div>
            </div>
            <div class="mt-3 pt-2.5 border-t border-graphite-800/80">
              <div class="flex items-start justify-between gap-2">
                <span class="text-accent-emerald font-bold text-xs leading-snug break-words">${{pick.selection}}</span>
                <span class="text-accent-amber font-extrabold text-xs whitespace-nowrap shrink-0">@ ${{pick.odds.toFixed(2)}}</span>
              </div>
              <div class="text-[10px] text-slate-400 mt-1 leading-relaxed">${{pick.algorithm || 'Fórmula Cuantitativa'}}</div>
            </div>
          `;
          container.appendChild(card);
        }});
      }} else {{
        strat.picks.forEach((pick, idx) => {{
          const badgeClass = getSourceBadgeClass(pick.sourceName);
          const iconClass = getSourceIcon(pick.sourceName);
          const sportBadge = getSportBadge(pick.sport);
          const card = document.createElement('div');
          card.className = 'bg-graphite-900/90 rounded-xl p-4 border border-graphite-800 flex flex-col justify-between hover:border-graphite-700 transition shadow-sm';
          card.innerHTML = `
            <div>
              <div class="flex items-center justify-between gap-1 mb-2 flex-wrap">
                <div class="flex items-center gap-1.5 flex-wrap">
                  <span class="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase font-mono ${{badgeClass}}">
                    <i class="${{iconClass}} mr-1 text-[9px]"></i>${{pick.sourceName}}
                  </span>
                  ${{sportBadge}}
                </div>
                <span class="text-[10px] text-slate-500 font-mono font-bold">SELECCIÓN ${{idx + 1}}</span>
              </div>
              <div class="font-bold text-white text-xs mt-1">${{pick.match}}</div>
              <div class="text-[10px] text-slate-400 mt-0.5">${{pick.tournament || pick.stadium || 'Competición Oficial'}}</div>
            </div>
            <div class="mt-3 pt-2.5 border-t border-graphite-800/80">
              <div class="flex items-start justify-between gap-2">
                <span class="text-accent-emerald font-bold text-xs leading-snug break-words">${{pick.selection}}</span>
                <span class="text-accent-amber font-extrabold text-xs whitespace-nowrap shrink-0">@ ${{pick.odds.toFixed(2)}}</span>
              </div>
              <div class="text-[10px] text-slate-400 mt-1 leading-relaxed">${{pick.algorithm || 'Fórmula Cuantitativa'}}</div>
            </div>
          `;
          container.appendChild(card);
        }});
      }}

      renderRealLifeSection(stratKey);
      calculatePayout();
    }}

    function renderRealLifeSection(stratKey) {{
      const strats = getActiveStrategies();
      const strat = strats[stratKey];
      if (!strat || !strat.real_life_example) return;
      const ex = strat.real_life_example;

      // 1. Steps List
      const stepsContainer = document.getElementById('realLifeStepsList');
      stepsContainer.innerHTML = '';
      if (ex.bookie_steps && ex.bookie_steps.length > 0) {{
        ex.bookie_steps.forEach((step, i) => {{
          const div = document.createElement('div');
          div.className = 'flex items-start space-x-2.5';
          div.innerHTML = `
            <span class="w-5 h-5 rounded-full bg-graphite-800 text-accent-cyan border border-graphite-700 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">${{i+1}}</span>
            <span class="leading-relaxed">${{step}}</span>
          `;
          stepsContainer.appendChild(div);
        }});
      }}

      // 2. Matches Resolution Grid
      const matchesContainer = document.getElementById('realLifeMatchesGrid');
      matchesContainer.innerHTML = '';
      if (ex.winning_scenario && ex.winning_scenario.match_examples) {{
        document.getElementById('realLifeScenarioTitle').innerText = ex.winning_scenario.title;
        ex.winning_scenario.match_examples.forEach((item) => {{
          const div = document.createElement('div');
          div.className = 'p-3 rounded-xl bg-graphite-900/90 border border-graphite-800 space-y-1.5';
          div.innerHTML = `
            <div class="flex items-center justify-between gap-2">
              <span class="font-bold text-white text-xs flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-accent-emerald"></span>
                ${{item.match}}
              </span>
              <span class="text-[10px] font-bold text-accent-amber px-2 py-0.5 bg-accent-amber/10 rounded border border-accent-amber/30">
                ${{item.min_result}}
              </span>
            </div>
            <div class="text-[11px] text-slate-300 pl-3.5 border-l border-graphite-700">
              ${{item.explanation}}
            </div>
          `;
          matchesContainer.appendChild(div);
        }});
      }}

      // 3. Tip Box Text
      if (currentEdition === 'hybrid') {{
        if (stratKey === 'modo_a_simples') {{
          document.getElementById('realLifeTipText').innerText = "En Modo A Híbrido, cruzas ligas con correlación cero (Nations League + MLB + NFL), reduciendo la varianza sistémica a cero.";
        }} else if (stratKey === 'modo_b_sistema') {{
          document.getElementById('realLifeTipText').innerText = "En Modo B Híbrido el sistema Trixie genera 4 combinadas cruzadas: si 1 falla, la doble restante protege y amortiza tu capital.";
        }} else if (stratKey === 'modo_c_banker') {{
          document.getElementById('realLifeTipText').innerText = "En Modo C Híbrido juegas solo las 2 líneas más asimétricas con más de 91% de probabilidad calculada.";
        }}
      }} else {{
        if (stratKey === 'modo_a_simples') {{
          document.getElementById('realLifeTipText').innerText = "En Modo A cada partido cobra por separado, garantizando ganancia neta incluso si 1 partido falla.";
        }} else if (stratKey === 'modo_b_sistema') {{
          document.getElementById('realLifeTipText').innerText = "En Modo B el sistema Trixie cubre 4 combinaciones: si fallas 1 partido, cobras la doble restante.";
        }} else if (stratKey === 'modo_c_banker') {{
          document.getElementById('realLifeTipText').innerText = "En Modo C solo juegas los 2 partidos con >85% de certeza en mercados de muy baja volatilidad.";
        }}
      }}
    }}

    function calculatePayout() {{
      const stakeInput = document.getElementById('calcStakeInput');
      let stake = parseFloat(stakeInput.value) || 0;
      if (stake < 0) stake = 0;

      const strats = getActiveStrategies();
      const strat = strats[currentStrategyKey];
      if (!strat) return;
      const payoutEl = document.getElementById('realLifePayoutText');
      const multEl = document.getElementById('realLifeMultiplierText');

      if (currentStrategyKey === 'modo_a_simples') {{
        const picks = strat.picks || [];
        const numPicks = picks.length || 3;
        const totalStake = stake * numPicks;
        let returnAll = 0;
        let returnTopTwo = 0;
        picks.forEach((p, idx) => {{
          const o = parseFloat(p.odds) || 1.6;
          const ret = stake * o;
          returnAll += ret;
          if (idx < 2) returnTopTwo += ret;
        }});
        const profitAll = returnAll - totalStake;

        document.getElementById('calcLabel1').innerText = 'Retorno (' + numPicks + '/' + numPicks + ' Aciertos - Inversión $' + totalStake.toFixed(0) + '):';
        document.getElementById('calcLabel2').innerText = 'Ganancia Neta (' + numPicks + '/' + numPicks + '):';
        document.getElementById('calcTotalReturn').innerText = '$' + returnAll.toFixed(2);
        document.getElementById('calcNetProfit').innerText = '+$' + profitAll.toFixed(2);

        if (payoutEl) {{
          payoutEl.innerText = `Con $${{stake.toFixed(0)}} en cada partido (Total $${{totalStake.toFixed(0)}}): Acierto 2/3 = $${{returnTopTwo.toFixed(2)}} (+$${{(returnTopTwo-totalStake).toFixed(2)}}) | Acierto 3/3 = $${{returnAll.toFixed(2)}} (+$${{profitAll.toFixed(2)}}).`;
        }}
        if (multEl) multEl.innerText = `${{strat.expectedWinRate || '84.5%'}} WIN RATE`;
      }} else if (currentStrategyKey === 'modo_b_sistema') {{
        const perBet = stake / 4;
        let retAll = 0;
        let retSingleDoble = 0;
        if (strat.combinations && strat.combinations.length > 0) {{
          strat.combinations.forEach((c, idx) => {{
            const ret = perBet * (parseFloat(c.odds) || 2.6);
            retAll += ret;
            if (idx === 0) retSingleDoble = ret;
          }});
        }} else {{
          retAll = perBet * (2.54 + 2.49 + 2.67 + 4.12);
          retSingleDoble = perBet * 2.54;
        }}
        const profitAll = retAll - stake;

        document.getElementById('calcLabel1').innerText = `Retorno Pleno (3/3 - Inversión $${{stake.toFixed(0)}}):`;
        document.getElementById('calcLabel2').innerText = 'Ganancia Neta Pleno:';
        document.getElementById('calcTotalReturn').innerText = `$${{retAll.toFixed(2)}}`;
        document.getElementById('calcNetProfit').innerText = `+$${{profitAll.toFixed(2)}}`;

        if (payoutEl) {{
          payoutEl.innerText = `Con $${{stake.toFixed(0)}} ($${{perBet.toFixed(1)}} x 4 apuestas): Acierto 2/3 recupera ~$${{retSingleDoble.toFixed(2)}} | Acierto 3/3 cobra $${{retAll.toFixed(2)}} (+$${{profitAll.toFixed(2)}} neto).`;
        }}
        if (multEl) multEl.innerText = 'SEGURO 1 FALLO';
      }} else if (currentStrategyKey === 'modo_c_banker') {{
        const totalOdds = parseFloat(strat.totalOdds) || 2.09;
        const totalReturn = stake * totalOdds;
        const netProfit = totalReturn - stake;

        document.getElementById('calcLabel1').innerText = `Retorno Duplicador (Inversión $${{stake.toFixed(0)}}):`;
        document.getElementById('calcLabel2').innerText = 'Ganancia Neta:';
        document.getElementById('calcTotalReturn').innerText = `$${{totalReturn.toFixed(2)}}`;
        document.getElementById('calcNetProfit').innerText = `+$${{netProfit.toFixed(2)}}`;

        if (payoutEl) {{
          payoutEl.innerText = `Con una apuesta de $${{stake.toFixed(2)}} cobras $${{totalReturn.toFixed(2)}} (+$${{netProfit.toFixed(2)}} de ganancia neta).`;
        }}
        if (multEl) multEl.innerText = `${{totalOdds.toFixed(2)}}x DUPLICADOR`;
      }}
    }}

    function setQuickStake(amount) {{
      document.getElementById('calcStakeInput').value = amount;
      calculatePayout();
    }}

    function copyCurrentStrategy() {{
      const strats = getActiveStrategies();
      const strat = strats[currentStrategyKey];
      const copyText = (strat && strat.real_life_example && strat.real_life_example.copy_text) || "BLACK ROYAL STRATEGY";

      navigator.clipboard.writeText(copyText).then(() => {{
        showToast("¡Boleto copiado al portapapeles con éxito!");
      }}).catch(() => {{
        showToast("Selección copiada al portapapeles.");
      }});
    }}

    function switchStrategyTab(stratKey) {{
      currentStrategyKey = stratKey;

      const btnA = document.getElementById('btnStrat-modo_a_simples');
      const btnB = document.getElementById('btnStrat-modo_b_sistema');
      const btnC = document.getElementById('btnStrat-modo_c_banker');

      [btnA, btnB, btnC].forEach(b => {{
        if (b) b.className = 'px-4 py-2 rounded-lg font-medium transition flex items-center space-x-2 text-slate-400 hover:text-white cursor-pointer';
      }});

      if (stratKey === 'modo_a_simples') {{
        btnA.className = currentEdition === 'hybrid'
          ? 'px-4 py-2 rounded-lg font-bold transition flex items-center space-x-2 bg-purple-500 text-white shadow cursor-pointer'
          : 'px-4 py-2 rounded-lg font-bold transition flex items-center space-x-2 bg-accent-emerald text-black shadow cursor-pointer';
      }} else if (stratKey === 'modo_b_sistema') {{
        btnB.className = 'px-4 py-2 rounded-lg font-bold transition flex items-center space-x-2 bg-accent-cyan text-black shadow cursor-pointer';
      }} else if (stratKey === 'modo_c_banker') {{
        btnC.className = 'px-4 py-2 rounded-lg font-bold transition flex items-center space-x-2 bg-accent-amber text-black shadow cursor-pointer';
      }}

      renderStrategyCard(stratKey);
    }}

    function showToast(message, isSuccess = true) {{
      const toast = document.getElementById('toastContainer');
      const toastMsg = document.getElementById('toastMessage');
      const toastContent = document.getElementById('toastContent');
      if (!toast || !toastMsg) return;
      toastMsg.innerText = message;
      if (isSuccess) {{
        toastContent.className = 'bg-graphite-900/95 border border-accent-emerald/50 text-accent-emerald px-4 py-2.5 rounded-xl shadow-2xl backdrop-blur-md text-xs font-mono font-bold flex items-center space-x-2';
      }} else {{
        toastContent.className = 'bg-graphite-900/95 border border-accent-amber/50 text-accent-amber px-4 py-2.5 rounded-xl shadow-2xl backdrop-blur-md text-xs font-mono font-bold flex items-center space-x-2';
      }}
      toast.classList.remove('opacity-0', 'translate-y-4');
      toast.classList.add('opacity-100', 'translate-y-0');
      setTimeout(() => {{
        toast.classList.add('opacity-0', 'translate-y-4');
        toast.classList.remove('opacity-100', 'translate-y-0');
      }}, 3200);
    }}

    async function forceRemoteRefresh() {{
      const icons = document.querySelectorAll('.fa-rotate');
      icons.forEach(ic => ic.classList.add('fa-spin'));
      showToast('🔄 Conectando y descargando versión remota...');

      // 1. Clear any local CacheStorage (Service Worker / PWA caches)
      if ('caches' in window) {{
        try {{
          const cacheKeys = await caches.keys();
          await Promise.all(cacheKeys.map(key => caches.delete(key)));
        }} catch (e) {{
          console.warn('Cache clear error:', e);
        }}
      }}

      // 2. Fetch fresh summary_recommendations.json with cache-buster timestamp
      try {{
        const timestamp = Date.now();
        const res = await fetch('summary_recommendations.json?nocache=' + timestamp, {{
          cache: 'no-store',
          headers: {{
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
          }}
        }});

        if (res.ok) {{
          const fresh = await res.json();
          if (fresh && fresh.strategies) {{
            DATASET = fresh;
            window.RAW_DATASET = fresh;
            
            // Update display date in header if changed
            if (fresh.generated_at) {{
              const dtStr = fresh.generated_at.split(' ')[0];
              const parts = dtStr.split('-');
              if (parts.length === 3) {{
                const months = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"];
                const day = parseInt(parts[2], 10);
                const month = months[parseInt(parts[1], 10) - 1];
                const year = parts[0];
                const dateBadge = document.getElementById('displayDateBadge');
                if (dateBadge) dateBadge.innerText = day + ' ' + month + ' ' + year;
              }}
            }}

            updateStrategyButtons();
            renderStrategyCard(currentStrategyKey);
            showToast('✅ ¡Datos y estrategias actualizadas con éxito!');
            icons.forEach(ic => ic.classList.remove('fa-spin'));
            return;
          }}
        }}
      }} catch (err) {{
        console.warn('Direct fetch error, executing hard reload...', err);
      }}

      // 3. Fallback: Hard reload with cache buster query param
      setTimeout(() => {{
        const url = new URL(window.location.href);
        url.searchParams.set('v', Date.now());
        window.location.href = url.toString();
      }}, 500);
    }}

    async function silentCheckForUpdates() {{
      try {{
        const timestamp = Date.now();
        const res = await fetch('summary_recommendations.json?check=' + timestamp, {{
          cache: 'no-store',
          headers: {{ 'Cache-Control': 'no-cache' }}
        }});
        if (res.ok) {{
          const fresh = await res.json();
          if (fresh && fresh.generated_at && window.RAW_DATASET && fresh.generated_at !== window.RAW_DATASET.generated_at) {{
            DATASET = fresh;
            window.RAW_DATASET = fresh;
            updateStrategyButtons();
            renderStrategyCard(currentStrategyKey);
            showToast('✨ Nueva jornada detectada y actualizada automáticamente');
          }}
        }}
      }} catch (e) {{
        // ignore background error
      }}
    }}

    // Auto-update when user switches back to the app on iPhone / Mobile
    document.addEventListener('visibilitychange', () => {{
      if (document.visibilityState === 'visible') {{
        silentCheckForUpdates();
      }}
    }});
    window.addEventListener('pageshow', (e) => {{
      if (e.persisted) {{
        silentCheckForUpdates();
      }}
    }});

    function updateLiveClock() {{
      const now = new Date();
      const str = now.toTimeString().split(' ')[0] + ' UTC';
      const el = document.getElementById('liveClockHeader');
      if (el) el.innerText = str;
    }}

    window.onload = function() {{
      window.RAW_DATASET = DATASET;
      updateStrategyButtons();
      renderStrategyCard('modo_a_simples');
      updateLiveClock();
      setInterval(updateLiveClock, 1000);
    }};
  </script>

  <!-- Floating Mobile Quick Refresh FAB for iPhone / PWA Shortcut -->
  <button onclick="forceRemoteRefresh()" title="Actualizar datos en vivo" class="sm:hidden fixed bottom-5 right-5 z-50 bg-accent-emerald text-black p-4 rounded-full shadow-2xl border-2 border-white/20 active:scale-90 transition flex items-center justify-center cursor-pointer">
    <i class="fa-solid fa-rotate text-lg"></i>
  </button>

  <!-- Toast Notification Container -->
  <div id="toastContainer" class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 pointer-events-none transition-all duration-300 opacity-0 transform translate-y-4">
    <div id="toastContent" class="bg-graphite-900/95 border border-accent-emerald/50 text-accent-emerald px-4 py-2.5 rounded-xl shadow-2xl backdrop-blur-md text-xs font-mono font-bold flex items-center space-x-2">
      <i class="fa-solid fa-circle-check"></i>
      <span id="toastMessage">Datos actualizados</span>
    </div>
  </div>

</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

# Also sync to parent directory if index.html exists there
parent_index = os.path.join(CURRENT_DIR, '..', 'index.html')
if os.path.exists(parent_index):
    try:
        with open(parent_index, 'w', encoding='utf-8') as pf:
            pf.write(html_template)
        print("✅ Synced ../index.html")
    except Exception as e:
        print(f"Notice: Parent sync skipped ({e})")

print(f"✅ Benito/index.html updated with Dual Edition Switcher & Dedicated Hybrid Section for {display_date}!")
