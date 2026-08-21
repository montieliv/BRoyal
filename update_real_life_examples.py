import json

with open('summary_recommendations.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

# Add rich real-life betting slip examples for each parlay
real_life_examples = {
    "today_consensus": {
        "bookie_steps": [
            "Abre tu casa de apuestas favorita (Bet365, Caliente, Betano, Pinnacle, etc.).",
            "Busca y selecciona los 3 eventos en el menú de fútbol:",
            "• Benfica vs. Aarhus: Selecciona 'Hándicap Asiático: Benfica -1.5' (o Benfica gana por 2+ goles).",
            "• LDU Quito vs. Mirassol: Selecciona 'Resultado Final: Gana LDU Quito (1)'.",
            "• Corinthians vs. Rosario Central: Selecciona 'Total de Goles: Menos de 2.5 (Under)'.",
            "En tu boleto de apuestas, asegúrate de marcar 'PARLAY / COMBINADA (3 Selecciones)'.",
            "Ingresa tu monto (ej. $100 MXN / USD). La cuota multiplicadora resultante es 4.12x."
        ],
        "winning_scenario": {
            "title": "¿Cómo se gana este boleto en la vida real?",
            "match_examples": [
                {"match": "Benfica vs. Aarhus", "min_result": "Benfica 2 - 0 Aarhus (o 3-0, 3-1, 4-1)", "explanation": "Benfica debe ganar por diferencia de 2 o más goles."},
                {"match": "LDU Quito vs. Mirassol", "min_result": "LDU Quito 1 - 0 Mirassol (o 2-0, 2-1, 3-1)", "explanation": "Cualquier triunfo de LDU Quito en los 90 minutos reglamentarios."},
                {"match": "Corinthians vs. Rosario", "min_result": "Marcadores válidos: 0-0, 1-0, 0-1, 1-1 o 2-0", "explanation": "El partido debe terminar con 2 goles o menos en total."}
            ],
            "payout_example": "Si los 3 partidos cumplen su condición, con una apuesta de $100 cobras $412.00 ($312.00 de ganancia neta)."
        },
        "copy_text": "👑 BLACK ROYAL — COMBINADA #1 (SEGURIDAD)\n1. Benfica (-1.5 Hándicap) @ 1.58\n2. LDU Quito Ganador @ 1.58\n3. Corinthians vs Rosario Central (Menos de 2.5 Goles) @ 1.65\n► Cuota Total: 4.12x | Stake Sugerido: 1.5% - 2.0%"
    },
    "today_highyield": {
        "bookie_steps": [
            "Abre tu casa de apuestas y ve a la sección de torneos europeos (Europa League y Conference League).",
            "Agrega las 3 selecciones ofensivas al boleto:",
            "• Trabzonspor vs. Ferencváros: Selecciona 'Total de Goles: Más de 2.5 (Over)'.",
            "• FC Sion vs. Ajax: Selecciona el mercado combinado 'Resultado y Goles: Gana Ajax + Más de 1.5 Goles'.",
            "• Beşiktaş vs. Kauno Žalgiris: Selecciona 'Resultado y Goles: Gana Beşiktaş + Más de 2.5 Goles'.",
            "Elige la modalidad 'Combinada / Parlay (x3)'.",
            "Ingresa tu monto (ej. $100). La cuota multiplicadora es de 5.11x."
        ],
        "winning_scenario": {
            "title": "¿Cómo se gana este boleto en la vida real?",
            "match_examples": [
                {"match": "Trabzonspor vs. Ferencváros", "min_result": "2-1, 1-2, 3-0, 2-2 o superior", "explanation": "Se necesitan 3 o más goles entre ambos equipos combinados."},
                {"match": "FC Sion vs. Ajax", "min_result": "Sion 0 - 2 Ajax (o 1-2, 0-3, 1-3)", "explanation": "Ajax debe ganar el encuentro y haber 2 o más goles en total."},
                {"match": "Beşiktaş vs. Kauno Žalgiris", "min_result": "Beşiktaş 3 - 0 Kauno (o 2-1, 3-1, 4-0)", "explanation": "Beşiktaş debe ganar y el partido debe registrar al menos 3 goles."}
            ],
            "payout_example": "Si los 3 partidos cumplen su condición, con una apuesta de $100 cobras $511.00 ($411.00 de ganancia neta)."
        },
        "copy_text": "👑 BLACK ROYAL — COMBINADA #2 (RENDIMIENTO & GOLES)\n1. Trabzonspor vs Ferencváros (Más de 2.5 Goles) @ 1.72\n2. FC Sion vs Ajax (Gana Ajax + Más 1.5 Goles) @ 1.65\n3. Beşiktaş vs Kauno Žalgiris (Gana Beşiktaş + Más 2.5 Goles) @ 1.80\n► Cuota Total: 5.11x | Stake Sugerido: 0.75% - 1.0%"
    },
    "today_global_highreturn": {
        "bookie_steps": [
            "Abre tu casa de apuestas e ingresa a los mercados avanzados de hándicaps y especiales.",
            "Añade estas 3 selecciones de alta cuota al boleto:",
            "• Atalanta vs. Hapoel Tel Aviv: Selecciona 'Hándicap Asiático: Atalanta -2.0' (o Atalanta gana por 3+ goles).",
            "• LDU Quito vs. Mirassol: Selecciona 'Ganador a Cero (Win to Nil): LDU Quito gana sin recibir gol'.",
            "• Beşiktaş vs. Kauno Žalgiris: Selecciona 'Hándicap Asiático: Beşiktaş -2.5' (o Beşiktaş gana por 3+ goles).",
            "Selecciona 'PARLAY / COMBINADA (x3)'.",
            "Ingresa un stake medido (ej. $100). La cuota multiplicadora asciende a 16.78x."
        ],
        "winning_scenario": {
            "title": "¿Cómo se gana este boleto en la vida real?",
            "match_examples": [
                {"match": "Atalanta vs. Hapoel Tel Aviv", "min_result": "Atalanta 3 - 0 Hapoel (o 4-0, 4-1, 5-1)", "explanation": "Atalanta debe ganar por 3+ goles para ganar la apuesta (con 2 goles de ventaja se anula/reembolsa el leg)."},
                {"match": "LDU Quito vs. Mirassol", "min_result": "LDU Quito 1 - 0, 2 - 0, 3 - 0 Mirassol", "explanation": "LDU Quito debe ganar el partido y mantener su portería en cero."},
                {"match": "Beşiktaş vs. Kauno Žalgiris", "min_result": "Beşiktaş 3 - 0 Kauno (o 4-0, 4-1, 5-0)", "explanation": "Beşiktaş debe golear ganando por 3 o más goles de diferencia."}
            ],
            "payout_example": "Si los 3 partidos cumplen su condición, con una apuesta de $100 cobras $1,678.00 ($1,578.00 de ganancia neta directa)."
        },
        "copy_text": "👑 BLACK ROYAL — COMBINADA #3 (MEGA RETORNO GLOBAL)\n1. Atalanta (-2.0 Hándicap Asiático) @ 2.35\n2. LDU Quito Ganador a Cero (Win to Nil) @ 2.55\n3. Beşiktaş (-2.5 Hándicap Asiático) @ 2.80\n► Cuota Total: 16.78x | Stake Sugerido: 0.5% Bankroll"
    },
    "tomorrow_consensus": {
        "bookie_steps": [
            "Abre tu casa de apuestas para los partidos del Viernes 21 de Agosto.",
            "Añade las 3 selecciones de Premier League, Liga MX y La Liga:",
            "• Arsenal vs. Coventry: Selecciona 'Hándicap Asiático: Arsenal -1.5'.",
            "• FC Juárez vs. Club América: Selecciona 'Resultado Final: Gana Club América (2)'.",
            "• Real Betis vs. Real Sociedad: Selecciona 'Total de Goles: Menos de 2.5 (Under)'.",
            "Marca 'PARLAY / COMBINADA (3 Selecciones)'.",
            "Ingresa tu apuesta (ej. $100). La cuota combinada es de 4.47x."
        ],
        "winning_scenario": {
            "title": "¿Cómo se gana este boleto en la vida real?",
            "match_examples": [
                {"match": "Arsenal vs. Coventry City", "min_result": "Arsenal 2 - 0 Coventry (o 3-0, 3-1, 4-1)", "explanation": "Arsenal debe ganar el partido inaugural por 2 o más goles."},
                {"match": "FC Juárez vs. Club América", "min_result": "Juárez 0 - 1 América (o 0-2, 1-2, 1-3)", "explanation": "Cualquier triunfo de las Águilas del América como visitante."},
                {"match": "Real Betis vs. Real Sociedad", "min_result": "0-0, 1-0, 0-1, 1-1 o 2-0", "explanation": "Duelo táctico cerrado con un máximo de 2 goles en los 90 minutos."}
            ],
            "payout_example": "Si los 3 partidos se cumplen, con una apuesta de $100 cobras $447.00 ($347.00 de ganancia neta)."
        },
        "copy_text": "👑 BLACK ROYAL — COMBINADA MAÑANA (21 AGOSTO)\n1. Arsenal (-1.5 Hándicap) @ 1.52\n2. Club América Ganador @ 1.75\n3. Real Betis vs Real Sociedad (Menos de 2.5 Goles) @ 1.68\n► Cuota Total: 4.47x | Stake Sugerido: 1.0% - 1.5%"
    }
}

dataset["real_life_examples"] = real_life_examples

with open('summary_recommendations.json', 'w', encoding='utf-8') as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print("✅ Real life examples embedded into summary_recommendations.json!")
