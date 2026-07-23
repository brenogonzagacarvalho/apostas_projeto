# brasileirao_predictor.py
"""
Módulo estatístico preditivo para prever Odds Pré-Jogo, Mercado de Gols (Over/Under, Ambas Marcam)
e Placares Exatos do Campeonato Brasileiro utilizando Distribuição de Poisson.
Sincronizado 100% com a Grade Completa da Betano.
"""

import math
import json
import os

DEFAULT_STATS = {
    "Corinthians": {"gols_marcados_casa": 16, "gols_sofridos_casa": 7, "jogos_casa": 9, "gols_marcados_fora": 10, "gols_sofridos_fora": 16, "jogos_fora": 10},
    "Remo": {"gols_marcados_casa": 14, "gols_sofridos_casa": 10, "jogos_casa": 9, "gols_marcados_fora": 8, "gols_sofridos_fora": 18, "jogos_fora": 10},
    "Botafogo-RJ": {"gols_marcados_casa": 19, "gols_sofridos_casa": 8, "jogos_casa": 10, "gols_marcados_fora": 14, "gols_sofridos_fora": 9, "jogos_fora": 9},
    "Vitória": {"gols_marcados_casa": 12, "gols_sofridos_casa": 12, "jogos_casa": 9, "gols_marcados_fora": 8, "gols_sofridos_fora": 18, "jogos_fora": 10},
    "Athletico-PR": {"gols_marcados_casa": 17, "gols_sofridos_casa": 8, "jogos_casa": 10, "gols_marcados_fora": 12, "gols_sofridos_fora": 12, "jogos_fora": 9},
    "Internacional": {"gols_marcados_casa": 16, "gols_sofridos_casa": 6, "jogos_casa": 9, "gols_marcados_fora": 13, "gols_sofridos_fora": 10, "jogos_fora": 10},
    "Santos": {"gols_marcados_casa": 17, "gols_sofridos_casa": 8, "jogos_casa": 10, "gols_marcados_fora": 10, "gols_sofridos_fora": 15, "jogos_fora": 9},
    "Chapecoense": {"gols_marcados_casa": 11, "gols_sofridos_casa": 13, "jogos_casa": 9, "gols_marcados_fora": 7, "gols_sofridos_fora": 19, "jogos_fora": 10},
    "Vasco da Gama": {"gols_marcados_casa": 15, "gols_sofridos_casa": 11, "jogos_casa": 10, "gols_marcados_fora": 9, "gols_sofridos_fora": 16, "jogos_fora": 9},
    "Mirassol": {"gols_marcados_casa": 13, "gols_sofridos_casa": 10, "jogos_casa": 9, "gols_marcados_fora": 9, "gols_sofridos_fora": 15, "jogos_fora": 10},
    "Cruzeiro": {"gols_marcados_casa": 16, "gols_sofridos_casa": 7, "jogos_casa": 9, "gols_marcados_fora": 11, "gols_sofridos_fora": 14, "jogos_fora": 10},
    "Bahia": {"gols_marcados_casa": 18, "gols_sofridos_casa": 9, "jogos_casa": 10, "gols_marcados_fora": 10, "gols_sofridos_fora": 15, "jogos_fora": 9},
    "Grêmio": {"gols_marcados_casa": 14, "gols_sofridos_casa": 10, "jogos_casa": 9, "gols_marcados_fora": 10, "gols_sofridos_fora": 15, "jogos_fora": 10},
    "Fluminense": {"gols_marcados_casa": 16, "gols_sofridos_casa": 9, "jogos_casa": 10, "gols_marcados_fora": 11, "gols_sofridos_fora": 13, "jogos_fora": 9},
    "Flamengo": {"gols_marcados_casa": 20, "gols_sofridos_casa": 5, "jogos_casa": 9, "gols_marcados_fora": 16, "gols_sofridos_fora": 8, "jogos_fora": 9},
    "São Paulo": {"gols_marcados_casa": 18, "gols_sofridos_casa": 7, "jogos_casa": 10, "gols_marcados_fora": 11, "gols_sofridos_fora": 12, "jogos_fora": 9},
    "RB Bragantino": {"gols_marcados_casa": 16, "gols_sofridos_casa": 10, "jogos_casa": 10, "gols_marcados_fora": 11, "gols_sofridos_fora": 13, "jogos_fora": 9},
    "Coritiba": {"gols_marcados_casa": 12, "gols_sofridos_casa": 12, "jogos_casa": 9, "gols_marcados_fora": 8, "gols_sofridos_fora": 18, "jogos_fora": 10},
    "Palmeiras": {"gols_marcados_casa": 20, "gols_sofridos_casa": 6, "jogos_casa": 10, "gols_marcados_fora": 15, "gols_sofridos_fora": 7, "jogos_fora": 9},
    "Atlético-MG": {"gols_marcados_casa": 14, "gols_sofridos_casa": 10, "jogos_casa": 9, "gols_marcados_fora": 11, "gols_sofridos_fora": 16, "jogos_fora": 10}
}

# Grade Completa de Jogos e Odds da Betano para a Rodada
GRADE_BETANO_RODADA = [
    {"data_hora": "23/07 19:30", "mandante": "Corinthians", "visitante": "Remo", "odd_1": 1.55, "odd_x": 4.05, "odd_2": 7.30},
    {"data_hora": "23/07 19:30", "mandante": "Botafogo-RJ", "visitante": "Vitória", "odd_1": 1.78, "odd_x": 3.75, "odd_2": 5.00},
    {"data_hora": "25/07 18:30", "mandante": "Athletico-PR", "visitante": "Internacional", "odd_1": 2.05, "odd_x": 3.25, "odd_2": 3.95},
    {"data_hora": "25/07 18:30", "mandante": "Santos", "visitante": "Chapecoense", "odd_1": 1.44, "odd_x": 4.45, "odd_2": 7.90},
    {"data_hora": "25/07 20:30", "mandante": "Vasco da Gama", "visitante": "Mirassol", "odd_1": 2.05, "odd_x": 3.35, "odd_2": 3.85},
    {"data_hora": "26/07 16:00", "mandante": "Cruzeiro", "visitante": "Botafogo-RJ", "odd_1": 1.78, "odd_x": 3.65, "odd_2": 4.75},
    {"data_hora": "26/07 16:00", "mandante": "Bahia", "visitante": "Corinthians", "odd_1": 2.15, "odd_x": 3.35, "odd_2": 3.50},
    {"data_hora": "26/07 18:30", "mandante": "Grêmio", "visitante": "Fluminense", "odd_1": 2.65, "odd_x": 3.30, "odd_2": 2.70},
    {"data_hora": "26/07 18:30", "mandante": "Flamengo", "visitante": "São Paulo", "odd_1": 1.50, "odd_x": 4.25, "odd_2": 6.80},
    {"data_hora": "26/07 18:30", "mandante": "RB Bragantino", "visitante": "Coritiba", "odd_1": 1.62, "odd_x": 3.90, "odd_2": 5.80},
    {"data_hora": "26/07 19:30", "mandante": "Remo", "visitante": "Vitória", "odd_1": 2.20, "odd_x": 3.30, "odd_2": 3.40},
    {"data_hora": "26/07 19:30", "mandante": "Palmeiras", "visitante": "Atlético-MG", "odd_1": 1.67, "odd_x": 3.70, "odd_2": 5.60}
]

STATS_FILE = os.path.join(os.path.dirname(__file__), "brasileirao_stats.json")

def carregar_estatisticas():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_STATS

def salvar_estatisticas(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

def poisson_pmf(k, mu):
    if mu <= 0 or k < 0:
        return 0.0
    return (math.pow(mu, k) * math.exp(-mu)) / math.factorial(k)

def calcular_medias_liga(stats):
    total_gols_casa = sum(s["gols_marcados_casa"] for s in stats.values())
    total_jogos_casa = sum(s["jogos_casa"] for s in stats.values())
    total_gols_fora = sum(s["gols_marcados_fora"] for s in stats.values())
    total_jogos_fora = sum(s["jogos_fora"] for s in stats.values())

    media_gols_casa = total_gols_casa / total_jogos_casa if total_jogos_casa > 0 else 1.4
    media_gols_fora = total_gols_fora / total_jogos_fora if total_jogos_fora > 0 else 1.0

    return media_gols_casa, media_gols_fora

def prever_partida(time_mandante, time_visitante, max_gols=6):
    stats = carregar_estatisticas()
    
    if time_mandante not in stats or time_visitante not in stats:
        # Fallback de estatísticas genéricas caso um time não esteja cadastrado
        default_team_stat = {"gols_marcados_casa": 15, "gols_sofridos_casa": 10, "jogos_casa": 10, "gols_marcados_fora": 10, "gols_sofridos_fora": 15, "jogos_fora": 10}
        mandante_st = stats.get(time_mandante, default_team_stat)
        visitante_st = stats.get(time_visitante, default_team_stat)
    else:
        mandante_st = stats[time_mandante]
        visitante_st = stats[time_visitante]

    media_liga_casa, media_liga_fora = calcular_medias_liga(stats)

    med_gols_pro_mandante = mandante_st["gols_marcados_casa"] / mandante_st["jogos_casa"] if mandante_st["jogos_casa"] > 0 else media_liga_casa
    med_gols_contra_mandante = mandante_st["gols_sofridos_casa"] / mandante_st["jogos_casa"] if mandante_st["jogos_casa"] > 0 else media_liga_fora

    med_gols_pro_visitante = visitante_st["gols_marcados_fora"] / visitante_st["jogos_fora"] if visitante_st["jogos_fora"] > 0 else media_liga_fora
    med_gols_contra_visitante = visitante_st["gols_sofridos_fora"] / visitante_st["jogos_fora"] if visitante_st["jogos_fora"] > 0 else media_liga_casa

    forca_ataque_mandante = med_gols_pro_mandante / media_liga_casa
    forca_defesa_mandante = med_gols_contra_mandante / media_liga_fora

    forca_ataque_visitante = med_gols_pro_visitante / media_liga_fora
    forca_defesa_visitante = med_gols_contra_visitante / media_liga_casa

    xg_mandante = forca_ataque_mandante * forca_defesa_visitante * media_liga_casa
    xg_visitante = forca_ataque_visitante * forca_defesa_mandante * media_liga_fora

    prob_vitoria_mandante = 0.0
    prob_empate = 0.0
    prob_vitoria_visitante = 0.0
    prob_over_15 = 0.0
    prob_over_25 = 0.0
    prob_over_35 = 0.0
    prob_btts_sim = 0.0

    placares = []

    for g_home in range(max_gols + 1):
        p_home = poisson_pmf(g_home, xg_mandante)
        for g_away in range(max_gols + 1):
            p_away = poisson_pmf(g_away, xg_visitante)
            prob_placar = p_home * p_away
            total_gols = g_home + g_away

            placar_str = f"{g_home}-{g_away}"
            odd_placar = round(1.0 / prob_placar, 2) if prob_placar > 0 else 999.0

            placares.append({
                "placar": placar_str,
                "gols_mandante": g_home,
                "gols_visitante": g_away,
                "probabilidade": round(prob_placar * 100, 2),
                "odd_justa": odd_placar
            })

            if g_home > g_away:
                prob_vitoria_mandante += prob_placar
            elif g_home == g_away:
                prob_empate += prob_placar
            else:
                prob_vitoria_visitante += prob_placar

            if total_gols > 1.5:
                prob_over_15 += prob_placar
            if total_gols > 2.5:
                prob_over_25 += prob_placar
            if total_gols > 3.5:
                prob_over_35 += prob_placar
            if g_home > 0 and g_away > 0:
                prob_btts_sim += prob_placar

    placares_ordenados = sorted(placares, key=lambda x: x["probabilidade"], reverse=True)

    odd_mandante = round(1.0 / prob_vitoria_mandante, 2) if prob_vitoria_mandante > 0 else 99.0
    odd_empate = round(1.0 / prob_empate, 2) if prob_empate > 0 else 99.0
    odd_visitante = round(1.0 / prob_vitoria_visitante, 2) if prob_vitoria_visitante > 0 else 99.0

    prob_under_15 = max(0.0, 1.0 - prob_over_15)
    prob_under_25 = max(0.0, 1.0 - prob_over_25)
    prob_under_35 = max(0.0, 1.0 - prob_over_35)
    prob_btts_nao = max(0.0, 1.0 - prob_btts_sim)

    odds_gols = {
        "over_15": {"prob": round(prob_over_15 * 100, 1), "odd": round(1.0 / prob_over_15, 2) if prob_over_15 > 0 else 99.0},
        "under_15": {"prob": round(prob_under_15 * 100, 1), "odd": round(1.0 / prob_under_15, 2) if prob_under_15 > 0 else 99.0},
        "over_25": {"prob": round(prob_over_25 * 100, 1), "odd": round(1.0 / prob_over_25, 2) if prob_over_25 > 0 else 99.0},
        "under_25": {"prob": round(prob_under_25 * 100, 1), "odd": round(1.0 / prob_under_25, 2) if prob_under_25 > 0 else 99.0},
        "over_35": {"prob": round(prob_over_35 * 100, 1), "odd": round(1.0 / prob_over_35, 2) if prob_over_35 > 0 else 99.0},
        "under_35": {"prob": round(prob_under_35 * 100, 1), "odd": round(1.0 / prob_under_35, 2) if prob_under_35 > 0 else 99.0},
        "btts_sim": {"prob": round(prob_btts_sim * 100, 1), "odd": round(1.0 / prob_btts_sim, 2) if prob_btts_sim > 0 else 99.0},
        "btts_nao": {"prob": round(prob_btts_nao * 100, 1), "odd": round(1.0 / prob_btts_nao, 2) if prob_btts_nao > 0 else 99.0},
    }

    return {
        "time_mandante": time_mandante,
        "time_visitante": time_visitante,
        "xg_mandante": round(xg_mandante, 2),
        "xg_visitante": round(xg_visitante, 2),
        "total_xg": round(xg_mandante + xg_visitante, 2),
        "probabilidades": {
            "mandante": round(prob_vitoria_mandante * 100, 1),
            "empate": round(prob_empate * 100, 1),
            "visitante": round(prob_vitoria_visitante * 100, 1)
        },
        "odds_justas": {
            "mandante": odd_mandante,
            "empate": odd_empate,
            "visitante": odd_visitante
        },
        "odds_gols": odds_gols,
        "top_placares": placares_ordenados[:10]
    }

def calcular_ev_e_kelly(odd_casa, probabilidade_pct):
    """
    Calcula o Valor Esperado (EV%) e a indicação de banca via Critério de Kelly.
    - Se a odd for muito alta (zebra > 4.00), classifica como Zebra de EV.
    """
    if odd_casa <= 1.0 or probabilidade_pct <= 0:
        return {"ev_pct": 0.0, "tem_valor": False, "kelly_pct": 0.0, "categoria": "Sem Valor"}

    p = probabilidade_pct / 100.0
    ev = (odd_casa * p) - 1.0
    ev_pct = round(ev * 100, 2)

    # Classificação de Confiança
    if odd_casa > 4.0:
        categoria = "Zebra (+EV)"
    elif odd_casa >= 2.0:
        categoria = "Média Confiança"
    else:
        categoria = "Alta Confiança"

    # Kelly Fracionado (1/4 Kelly)
    b = odd_casa - 1.0
    f_kelly = (p * b - (1.0 - p)) / b if b > 0 else 0.0
    kelly_recomendado = max(0.0, round((f_kelly / 4.0) * 100, 2))

    return {
        "ev_pct": ev_pct,
        "tem_valor": ev_pct > 0,
        "kelly_pct": kelly_recomendado,
        "categoria": categoria
    }


def obter_lista_times():
    stats = carregar_estatisticas()
    return sorted(list(stats.keys()))

def obter_confrontos_rodada(num_rodada=100):
    """Calcula a análise estatística completa e compara com as odds da Betano para todos os jogos da rodada."""
    resultados = []
    for jogo in GRADE_BETANO_RODADA:
        home = jogo["mandante"]
        away = jogo["visitante"]
        data_hora = jogo.get("data_hora", "")
        odd_1 = jogo.get("odd_1", 0.0)
        odd_x = jogo.get("odd_x", 0.0)
        odd_2 = jogo.get("odd_2", 0.0)

        try:
            prev = prever_partida(home, away)
            prev["data_hora"] = data_hora
            prev["odd_betano_1"] = odd_1
            prev["odd_betano_x"] = odd_x
            prev["odd_betano_2"] = odd_2

            # Análise de EV para os 3 mercados
            prev["ev_1"] = calcular_ev_e_kelly(odd_1, prev["probabilidades"]["mandante"])
            prev["ev_x"] = calcular_ev_e_kelly(odd_x, prev["probabilidades"]["empate"])
            prev["ev_2"] = calcular_ev_e_kelly(odd_2, prev["probabilidades"]["visitante"])

            # Encontrar o maior EV deste confronto
            maior_ev = max(prev["ev_1"]["ev_pct"], prev["ev_x"]["ev_pct"], prev["ev_2"]["ev_pct"])
            prev["maior_ev"] = maior_ev
            prev["is_melhor_da_rodada"] = False

            resultados.append(prev)
        except Exception:
            pass

    # Marcar o(s) Top 3 melhores jogos da rodada com a tag 'Melhor da Rodada'
    resultados_ordenados = sorted(resultados, key=lambda x: x["maior_ev"], reverse=True)
    for idx, item in enumerate(resultados_ordenados):
        if idx < 3 and item["maior_ev"] > 5.0:
            item["is_melhor_da_rodada"] = True

    return resultados

def gerar_multiplas_recomendadas(resultados):
    """
    Gera combinações automáticas de múltiplas para a Betano com 3, 5 e 7 jogos,
    selecionando sempre as melhores apostas com +EV da rodada.
    """
    if not resultados:
        return {}

    # Extrair a melhor opção de aposta (+EV) de cada jogo
    apostas_otimizadas = []
    for j in resultados:
        melhor_opcao = None
        best_ev = -999.0

        if j["ev_1"]["ev_pct"] > best_ev and j["odd_betano_1"] <= 2.50:
            best_ev = j["ev_1"]["ev_pct"]
            melhor_opcao = {
                "confronto": f"{j['time_mandante']} vs {j['time_visitante']}",
                "selecao": f"Vitória {j['time_mandante']}",
                "odd_betano": j["odd_betano_1"],
                "ev_pct": j["ev_1"]["ev_pct"]
            }
        if j["ev_2"]["ev_pct"] > best_ev and j["odd_betano_2"] <= 3.50:
            best_ev = j["ev_2"]["ev_pct"]
            melhor_opcao = {
                "confronto": f"{j['time_mandante']} vs {j['time_visitante']}",
                "selecao": f"Vitória {j['time_visitante']}",
                "odd_betano": j["odd_betano_2"],
                "ev_pct": j["ev_2"]["ev_pct"]
            }

        if not melhor_opcao:
            # Fallback para vitória do mandante se for a opção mais segura
            melhor_opcao = {
                "confronto": f"{j['time_mandante']} vs {j['time_visitante']}",
                "selecao": f"Vitória {j['time_mandante']}",
                "odd_betano": j["odd_betano_1"],
                "ev_pct": j["ev_1"]["ev_pct"]
            }

        apostas_otimizadas.append(melhor_opcao)

    # Ordenar apostas pela maior vantagem +EV
    apostas_otimizadas = sorted(apostas_otimizadas, key=lambda x: x["ev_pct"], reverse=True)

    def montar_multipla(qtd):
        itens = apostas_otimizadas[:qtd]
        odd_total = 1.0
        for i in itens:
            odd_total *= i["odd_betano"]
        return {
            "qtd": qtd,
            "itens": itens,
            "odd_total": round(odd_total, 2)
        }

    return {
        "multipla_3": montar_multipla(min(3, len(apostas_otimizadas))),
        "multipla_5": montar_multipla(min(5, len(apostas_otimizadas))),
        "multipla_7": montar_multipla(min(7, len(apostas_otimizadas)))
    }


if __name__ == "__main__":
    res = obter_confrontos_rodada()
    print(f"\n--- Grade Completa Betano ({len(res)} jogos processados) ---")
    for r in res[:3]:
        print(f"[{r['data_hora']}] {r['time_mandante']} vs {r['time_visitante']}")
        print(f"   Betano: 1={r['odd_betano_1']} | X={r['odd_betano_x']} | 2={r['odd_betano_2']}")
        print(f"   Odd Justa Modelo: 1={r['odds_justas']['mandante']} | X={r['odds_justas']['empate']} | 2={r['odds_justas']['visitante']}")
        print(f"   EV 1: {r['ev_1']['ev_pct']}% | EV X: {r['ev_x']['ev_pct']}% | EV 2: {r['ev_2']['ev_pct']}%")
