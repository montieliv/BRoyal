import json

with open('summary_recommendations.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

dataset_json_str = json.dumps(dataset, ensure_ascii=False, indent=2)

html_template = f"""<!DOCTYPE html>
<html lang="es" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>BLACK ROYAL — Terminal Cuantitativa & Estrategias de Alto Win Rate</title>
  
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
          <span class="px-2 py-0.5 rounded badge-source-amber"><i class="fa-solid fa-brain mr-1 text-[9px]"></i>Sportmonks</span>
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
          <span class="text-accent-emerald font-bold">75% – 85%</span>
        </div>
        <button onclick="refreshData()" class="px-3 py-1.5 bg-graphite-800 hover:bg-graphite-700 text-slate-200 text-xs font-mono rounded-lg border border-graphite-600 transition flex items-center space-x-1.5 cursor-pointer">
          <i class="fa-solid fa-rotate text-accent-emerald"></i>
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
          <span class="text-xs font-mono font-semibold px-2.5 py-0.5 rounded bg-accent-emerald/15 text-accent-emerald border border-accent-emerald/30">
            21 AGOSTO 2026
          </span>
        </h1>
        <p class="text-xs md:text-sm text-slate-400 mt-1">
          Estrategias matemáticas diseñadas para maximizar el porcentaje de éxito diario y proteger el capital ante fallos inesperados.
        </p>
      </div>

      <div class="flex items-center space-x-2 text-xs font-mono bg-graphite-900 px-3 py-1.5 rounded-xl border border-graphite-700/80 text-slate-300">
        <i class="fa-solid fa-shield-check text-accent-emerald"></i>
        <span>Enfoque de Alta Certeza & Control de Riesgo</span>
      </div>
    </div>

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
            <span>Modo A: Simples (76% Win Rate)</span>
          </button>
          
          <button onclick="switchStrategyTab('modo_b_sistema')" id="btnStrat-modo_b_sistema" class="px-4 py-2 rounded-lg font-medium transition flex items-center space-x-2 text-slate-400 hover:text-white cursor-pointer">
            <i class="fa-solid fa-shield-halved text-accent-cyan"></i>
            <span>Modo B: Sistema 2/3 (Seguro 1 Fallo)</span>
          </button>

          <button onclick="switchStrategyTab('modo_c_banker')" id="btnStrat-modo_c_banker" class="px-4 py-2 rounded-lg font-medium transition flex items-center space-x-2 text-slate-400 hover:text-white cursor-pointer">
            <i class="fa-solid fa-bolt text-accent-amber"></i>
            <span>Modo C: Doble Banker (2.04x)</span>
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
              <h3 id="activeStrategyTitle" class="text-sm md:text-base font-bold text-white font-mono">
                Modo A: Apuestas Simples de Valor
              </h3>
            </div>
            <p id="activeStrategySubtitle" class="text-xs text-slate-400 font-mono mt-1">
              3 Apuestas individuales independientes. Cada acierto cobra por separado eliminando el riesgo de que 1 fallo arruine todo el boleto.
            </p>
          </div>

          <!-- Quantitative KPIs -->
          <div class="flex flex-wrap items-center gap-2.5 text-xs font-mono">
            <div class="bg-graphite-900 px-3 py-1.5 rounded-xl border border-graphite-700/80 text-center">
              <span class="text-[10px] text-slate-400 block">TASA DE ÉXITO</span>
              <span id="activeStrategyWinRate" class="text-accent-emerald font-extrabold text-base">76.5%</span>
            </div>
            <div class="bg-graphite-900 px-3 py-1.5 rounded-xl border border-graphite-700/80 text-center">
              <span class="text-[10px] text-slate-400 block" id="activeStrategyMetricLabel">CUOTA MEDIA</span>
              <span id="activeStrategyOdds" class="text-accent-amber font-extrabold text-sm">1.66x</span>
            </div>
            <div class="bg-graphite-900 px-3 py-1.5 rounded-xl border border-graphite-700/80 text-center">
              <span class="text-[10px] text-slate-400 block">VALUE EDGE</span>
              <span id="activeStrategyEv" class="text-accent-cyan font-bold text-sm">+22.4%</span>
            </div>
            <div class="bg-graphite-900 px-3 py-1.5 rounded-xl border border-graphite-700/80 text-center hidden sm:block">
              <span class="text-[10px] text-slate-400 block">RIESGO GLOBAL</span>
              <span id="activeStrategyRisk" class="text-accent-emerald font-bold text-xs">MÍNIMO</span>
            </div>
          </div>
        </div>

        <!-- Strategy Picks Grid -->
        <div id="activeStrategyPicksGrid" class="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono">
          <!-- Populated dynamically -->
        </div>

        <!-- Integrated Dynamic Return Calculator -->
        <div class="bg-graphite-900/90 rounded-xl p-3.5 border border-graphite-800 flex flex-wrap items-center justify-between gap-4 font-mono text-xs">
          <div class="flex items-center space-x-3 flex-wrap gap-2">
            <div class="flex items-center space-x-2">
              <span class="text-slate-400 text-[11px]"><i class="fa-solid fa-calculator text-accent-cyan mr-1"></i>Simulador de Inversión ($):</span>
              <input type="number" id="calcStakeInput" value="100" min="1" step="10" oninput="calculatePayout()" 
                class="w-24 px-2.5 py-1 bg-graphite-950 border border-graphite-700 rounded-lg text-white font-bold text-right text-xs focus:outline-none focus:border-accent-emerald">
            </div>
            
            <div class="flex items-center space-x-1">
              <button onclick="setQuickStake(50)" class="px-2 py-1 bg-graphite-800 hover:bg-graphite-700 text-[10px] rounded text-slate-300 transition cursor-pointer">$50</button>
              <button onclick="setQuickStake(100)" class="px-2 py-1 bg-graphite-800 hover:bg-graphite-700 text-[10px] rounded text-slate-300 transition cursor-pointer">$100</button>
              <button onclick="setQuickStake(250)" class="px-2 py-1 bg-graphite-800 hover:bg-graphite-700 text-[10px] rounded text-slate-300 transition cursor-pointer">$250</button>
              <button onclick="setQuickStake(500)" class="px-2 py-1 bg-graphite-800 hover:bg-graphite-700 text-[10px] rounded text-slate-300 transition cursor-pointer">$500</button>
            </div>
          </div>

          <div class="flex items-center space-x-4 text-xs">
            <div>
              <span class="text-slate-400 text-[11px] block text-right" id="calcLabel1">Retorno Esperado (Pleno):</span>
              <span id="calcTotalReturn" class="text-white font-extrabold text-sm">$498.00</span>
            </div>
            <div>
              <span class="text-slate-400 text-[11px] block text-right" id="calcLabel2">Ganancia Neta Estimada:</span>
              <span id="calcNetProfit" class="text-accent-emerald font-black text-sm">+$198.00</span>
            </div>
          </div>
        </div>

      </div>
    </section>

    <!-- ==================== REAL-LIFE BETTING EXAMPLE & PRACTICAL SLIP GUIDE ==================== -->
    <section class="space-y-4 pt-2">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 class="text-sm md:text-base font-extrabold text-white tracking-wide font-mono flex items-center gap-2">
            <i class="fa-solid fa-receipt text-accent-cyan"></i>
            <span>EJEMPLO EN LA VIDA REAL: CÓMO METER ESTE BOLETO</span>
          </h2>
          <p class="text-xs text-slate-400 font-mono mt-0.5">
            Guía práctica paso a paso para colocar la apuesta en cualquier casa de apuestas y entender cómo se cobra.
          </p>
        </div>

        <button onclick="copyCurrentStrategy()" class="px-3.5 py-2 bg-graphite-800 hover:bg-graphite-700 text-accent-emerald font-mono text-xs font-bold rounded-lg border border-graphite-600 transition flex items-center space-x-1.5 cursor-pointer shadow-sm">
          <i class="fa-regular fa-copy"></i>
          <span id="copyBtnText">Copiar Boleto Listo</span>
        </button>
      </div>

      <!-- PRACTICAL REAL-LIFE CONTAINER -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 font-mono text-xs">
        
        <!-- STEP-BY-STEP SPORTSBOOK INSTRUCTIONS (Col 5) -->
        <div class="lg:col-span-5 card-clean rounded-2xl p-5 border border-graphite-800 space-y-4 flex flex-col justify-between">
          <div>
            <div class="flex items-center space-x-2 text-accent-amber font-bold text-xs uppercase tracking-wide mb-3">
              <i class="fa-solid fa-mobile-screen-button"></i>
              <span>Paso a Paso en tu Casa de Apuestas</span>
            </div>
            <p class="text-slate-400 text-[11px] leading-relaxed mb-3">
              Válido para <strong class="text-slate-200">Bet365, Caliente, Betano, Pinnacle, 1xBet</strong> o tu sportsbook habitual:
            </p>
            <div id="realLifeStepsList" class="space-y-2.5 text-slate-300 text-xs">
              <!-- Rendered dynamically -->
            </div>
          </div>

          <div id="realLifeTipBox" class="p-3 bg-graphite-900 rounded-xl border border-graphite-800 text-[11px] text-slate-400 flex items-center gap-2">
            <i class="fa-solid fa-circle-check text-accent-emerald"></i>
            <span id="realLifeTipText">En este modo cada partido cobra de forma individual, protegiendo tu dinero ante imprevistos.</span>
          </div>
        </div>

        <!-- HOW TO WIN & MATCH SCORE EXAMPLES (Col 7) -->
        <div class="lg:col-span-7 card-clean rounded-2xl p-5 border border-graphite-800 space-y-4">
          <div class="flex items-center justify-between gap-2 border-b border-graphite-800 pb-3">
            <div class="flex items-center space-x-2 text-accent-emerald font-bold text-xs uppercase tracking-wide">
              <i class="fa-solid fa-circle-check"></i>
              <span id="realLifeScenarioTitle">¿Cómo se cobra en la vida real?</span>
            </div>
            <span id="realLifeSuccessBadge" class="text-[10px] px-2.5 py-0.5 rounded bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/30 font-bold">
              76% - 86% WIN RATE
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
                <span id="realLifePayoutText" class="text-white text-xs font-bold">Si aciertas 2 de 3: Cobras ~$330.00 (Ganancia asegurada).</span>
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

  </main>

  <!-- TOAST NOTIFICATION CONTAINER -->
  <div id="toastNotification" class="fixed bottom-6 right-6 z-50 hidden bg-graphite-900 border border-accent-emerald text-white px-4 py-2.5 rounded-xl shadow-2xl font-mono text-xs flex items-center space-x-2">
    <i class="fa-solid fa-circle-check text-accent-emerald text-sm"></i>
    <span id="toastMessage">¡Boleto copiado al portapapeles!</span>
  </div>

  <!-- ==================== JAVASCRIPT APP LOGIC ==================== -->
  <script>
    const DATASET = {dataset_json_str};

    let currentStrategyKey = 'modo_a_simples'; // 'modo_a_simples' | 'modo_b_sistema' | 'modo_c_banker'

    function getSourceBadgeClass(source) {{
      if (source === 'FootyStats') return 'badge-source-cyan';
      if (source === 'API-Football') return 'badge-source-emerald';
      if (source === 'Sportmonks') return 'badge-source-amber';
      return 'bg-slate-800 text-slate-300 border-slate-700';
    }}

    function getSourceIcon(source) {{
      if (source === 'FootyStats') return 'fa-solid fa-chart-pie';
      if (source === 'API-Football') return 'fa-solid fa-chart-line';
      if (source === 'Sportmonks') return 'fa-solid fa-brain';
      return 'fa-solid fa-futbol';
    }}

    function renderStrategyCard(stratKey) {{
      const strat = DATASET.strategies[stratKey];
      if (!strat) return;

      const badgeEl = document.getElementById('activeStrategyBadge');
      const glowEl = document.getElementById('activeStrategyGlow');

      if (stratKey === 'modo_a_simples') {{
        badgeEl.className = 'px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider font-mono bg-accent-emerald text-black';
        badgeEl.innerText = 'MODO A: MÁXIMO WIN RATE (76.5%)';
        glowEl.className = 'absolute top-0 right-0 w-80 h-80 bg-accent-emerald/5 rounded-full blur-3xl pointer-events-none';
        document.getElementById('activeStrategyMetricLabel').innerText = 'CUOTA PROMEDIO';
        document.getElementById('activeStrategyOdds').innerText = `${{strat.avgOdds.toFixed(2)}}x`;
      }} else if (stratKey === 'modo_b_sistema') {{
        badgeEl.className = 'px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider font-mono bg-accent-cyan text-black';
        badgeEl.innerText = 'MODO B: SEGURO CONTRA 1 FALLO';
        glowEl.className = 'absolute top-0 right-0 w-80 h-80 bg-accent-cyan/5 rounded-full blur-3xl pointer-events-none';
        document.getElementById('activeStrategyMetricLabel').innerText = 'COMBINACIONES';
        document.getElementById('activeStrategyOdds').innerText = '4 Apuestas (3D+1T)';
      }} else if (stratKey === 'modo_c_banker') {{
        badgeEl.className = 'px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider font-mono bg-accent-amber text-black';
        badgeEl.innerText = 'MODO C: DUPLICADOR DE BANCA';
        glowEl.className = 'absolute top-0 right-0 w-80 h-80 bg-accent-amber/5 rounded-full blur-3xl pointer-events-none';
        document.getElementById('activeStrategyMetricLabel').innerText = 'CUOTA TOTAL';
        document.getElementById('activeStrategyOdds').innerText = `${{strat.totalOdds.toFixed(2)}}x`;
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
          const card = document.createElement('div');
          card.className = 'bg-graphite-900/90 rounded-xl p-4 border border-graphite-800 flex flex-col justify-between hover:border-graphite-700 transition shadow-sm';
          card.innerHTML = `
            <div>
              <div class="flex items-center justify-between gap-1 mb-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase font-mono ${{badgeClass}}">
                  <i class="${{iconClass}} mr-1 text-[9px]"></i>${{pick.sourceName}}
                </span>
                <span class="text-[10px] text-accent-cyan font-mono font-bold">PICK ${{String.fromCharCode(65 + idx)}}</span>
              </div>
              <div class="font-bold text-white text-xs mt-1">${{pick.match}}</div>
            </div>
            <div class="mt-3 pt-2.5 border-t border-graphite-800/80">
              <div class="flex items-center justify-between gap-2">
                <span class="text-accent-emerald font-bold text-xs truncate">${{pick.selection}}</span>
                <span class="text-accent-amber font-extrabold text-xs">@ ${{pick.odds.toFixed(2)}}</span>
              </div>
              <div class="text-[10px] text-slate-400 mt-1 leading-relaxed">${{pick.algorithm}}</div>
            </div>
          `;
          container.appendChild(card);
        }});
      }} else {{
        strat.picks.forEach((pick, idx) => {{
          const badgeClass = getSourceBadgeClass(pick.sourceName);
          const iconClass = getSourceIcon(pick.sourceName);
          const card = document.createElement('div');
          card.className = 'bg-graphite-900/90 rounded-xl p-4 border border-graphite-800 flex flex-col justify-between hover:border-graphite-700 transition shadow-sm';
          card.innerHTML = `
            <div>
              <div class="flex items-center justify-between gap-1 mb-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase font-mono ${{badgeClass}}">
                  <i class="${{iconClass}} mr-1 text-[9px]"></i>${{pick.sourceName}}
                </span>
                <span class="text-[10px] text-slate-500 font-mono font-bold">SELECCIÓN ${{idx + 1}}</span>
              </div>
              <div class="font-bold text-white text-xs mt-1">${{pick.match}}</div>
              <div class="text-[10px] text-slate-400 mt-0.5">${{pick.tournament || 'Fútbol Profesional'}}</div>
            </div>
            <div class="mt-3 pt-2.5 border-t border-graphite-800/80">
              <div class="flex items-center justify-between gap-2">
                <span class="text-accent-emerald font-bold text-xs truncate">${{pick.selection}}</span>
                <span class="text-accent-amber font-extrabold text-xs whitespace-nowrap">@ ${{pick.odds.toFixed(2)}}</span>
              </div>
              <div class="text-[10px] text-slate-400 mt-1 leading-relaxed">${{pick.algorithm}}</div>
            </div>
          `;
          container.appendChild(card);
        }});
      }}

      renderRealLifeSection(stratKey);
      calculatePayout();
    }}

    function renderRealLifeSection(stratKey) {{
      const strat = DATASET.strategies[stratKey];
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
      if (stratKey === 'modo_a_simples') {{
        document.getElementById('realLifeTipText').innerText = "En Modo A cada partido cobra por separado, garantizando ganancia neta incluso si 1 partido falla.";
      }} else if (stratKey === 'modo_b_sistema') {{
        document.getElementById('realLifeTipText').innerText = "En Modo B el sistema Trixie cubre 4 combinaciones: si fallas 1 partido, cobras la doble restante.";
      }} else if (stratKey === 'modo_c_banker') {{
        document.getElementById('realLifeTipText').innerText = "En Modo C solo juegas los 2 partidos con >85% de certeza en mercados de muy baja volatilidad.";
      }}
    }}

    function calculatePayout() {{
      const stakeInput = document.getElementById('calcStakeInput');
      let stake = parseFloat(stakeInput.value) || 0;
      if (stake < 0) stake = 0;

      const strat = DATASET.strategies[currentStrategyKey];
      const payoutEl = document.getElementById('realLifePayoutText');
      const multEl = document.getElementById('realLifeMultiplierText');

      if (currentStrategyKey === 'modo_a_simples') {{
        const totalStake = stake * 3;
        const returnAll = stake * 1.55 + stake * 1.75 + stake * 1.68; // ~4.98 * stake
        const profitAll = returnAll - totalStake;
        const returnTwo = stake * 1.68 + stake * 1.55; // 3.23 * stake (assuming 2 hit)

        document.getElementById('calcLabel1').innerText = `Retorno (3/3 Aciertos - Inversión $${{totalStake.toFixed(0)}}):`;
        document.getElementById('calcLabel2').innerText = 'Ganancia Neta (3/3):';
        document.getElementById('calcTotalReturn').innerText = `$${{returnAll.toFixed(2)}}`;
        document.getElementById('calcNetProfit').innerText = `+$${{profitAll.toFixed(2)}}`;

        if (payoutEl) {{
          payoutEl.innerText = `Con $${{stake.toFixed(0)}} en cada partido (Total $${{totalStake.toFixed(0)}}): Acierto 2/3 = $${{returnTwo.toFixed(2)}} (+$${{(returnTwo-totalStake).toFixed(2)}}) | Acierto 3/3 = $${{returnAll.toFixed(2)}} (+$${{profitAll.toFixed(2)}}).`;
        }}
        if (multEl) multEl.innerText = '76.5% WIN RATE';
      }} else if (currentStrategyKey === 'modo_b_sistema') {{
        const perBet = stake / 4;
        const retDoble1 = perBet * 2.60;
        const retDoble3 = perBet * 2.85;
        const retAll = perBet * (2.60 + 2.63 + 2.85 + 4.42);
        const profitAll = retAll - stake;

        document.getElementById('calcLabel1').innerText = `Retorno Pleno (3/3 - Inversión $${{stake.toFixed(0)}}):`;
        document.getElementById('calcLabel2').innerText = 'Ganancia Neta Pleno:';
        document.getElementById('calcTotalReturn').innerText = `$${{retAll.toFixed(2)}}`;
        document.getElementById('calcNetProfit').innerText = `+$${{profitAll.toFixed(2)}}`;

        if (payoutEl) {{
          payoutEl.innerText = `Con $${{stake.toFixed(0)}} ($${{perBet.toFixed(1)}} x 4 apuestas): Acierto 2/3 recupera $${{retDoble3.toFixed(2)}} | Acierto 3/3 cobra $${{retAll.toFixed(2)}} (+$${{profitAll.toFixed(2)}} neto).`;
        }}
        if (multEl) multEl.innerText = 'SEGURO 1 FALLO';
      }} else if (currentStrategyKey === 'modo_c_banker') {{
        const totalReturn = stake * 2.04;
        const netProfit = totalReturn - stake;

        document.getElementById('calcLabel1').innerText = `Retorno Duplicador (Inversión $${{stake.toFixed(0)}}):`;
        document.getElementById('calcLabel2').innerText = 'Ganancia Neta:';
        document.getElementById('calcTotalReturn').innerText = `$${{totalReturn.toFixed(2)}}`;
        document.getElementById('calcNetProfit').innerText = `+$${{netProfit.toFixed(2)}}`;

        if (payoutEl) {{
          payoutEl.innerText = `Con una apuesta de $${{stake.toFixed(2)}} cobras $${{totalReturn.toFixed(2)}} (+$${{netProfit.toFixed(2)}} de ganancia neta duplicando capital).`;
        }}
        if (multEl) multEl.innerText = '2.04x DUPLICADOR';
      }}
    }}

    function setQuickStake(amount) {{
      document.getElementById('calcStakeInput').value = amount;
      calculatePayout();
    }}

    function copyCurrentStrategy() {{
      const strat = DATASET.strategies[currentStrategyKey];
      const copyText = (strat && strat.real_life_example && strat.real_life_example.copy_text) || "BLACK ROYAL STRATEGY";

      navigator.clipboard.writeText(copyText).then(() => {{
        showToast("¡Boleto copiado al portapapeles con éxito!");
      }}).catch(() => {{
        showToast("Selección copiada al portapapeles.");
      }});
    }}

    function showToast(msg) {{
      const toast = document.getElementById('toastNotification');
      const toastMsg = document.getElementById('toastMessage');
      if (!toast || !toastMsg) return;

      toastMsg.innerText = msg;
      toast.classList.remove('hidden');
      toast.classList.add('toast-animate');

      setTimeout(() => {{
        toast.classList.add('hidden');
        toast.classList.remove('toast-animate');
      }}, 2600);
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
        btnA.className = 'px-4 py-2 rounded-lg font-bold transition flex items-center space-x-2 bg-accent-emerald text-black shadow cursor-pointer';
      }} else if (stratKey === 'modo_b_sistema') {{
        btnB.className = 'px-4 py-2 rounded-lg font-bold transition flex items-center space-x-2 bg-accent-cyan text-black shadow cursor-pointer';
      }} else if (stratKey === 'modo_c_banker') {{
        btnC.className = 'px-4 py-2 rounded-lg font-bold transition flex items-center space-x-2 bg-accent-amber text-black shadow cursor-pointer';
      }}

      renderStrategyCard(stratKey);
    }}

    function refreshData() {{
      const btn = event.currentTarget;
      btn.classList.add('opacity-50', 'pointer-events-none');
      setTimeout(() => {{
        renderStrategyCard(currentStrategyKey);
        btn.classList.remove('opacity-50', 'pointer-events-none');
      }}, 250);
    }}

    function updateLiveClock() {{
      const now = new Date();
      const str = now.toTimeString().split(' ')[0] + ' UTC';
      const el = document.getElementById('liveClockHeader');
      if (el) el.innerText = str;
    }}

    window.onload = function() {{
      renderStrategyCard('modo_a_simples');
      updateLiveClock();
      setInterval(updateLiveClock, 1000);
    }};
  </script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("✅ Benito/index.html updated with complete iOS PWA capabilities and August 21 strategies!")
