from flask import Flask, render_template, request, session
import os
from brasileirao_predictor import obter_lista_times, prever_partida, calcular_ev_e_kelly, obter_confrontos_rodada, gerar_multiplas_recomendadas
from scraper_brasileirao import atualizar_estatisticas_web

app = Flask(__name__)
app.secret_key = "chave_secreta_apostas_betano"

@app.route("/", methods=["GET", "POST"])
def index():
    if "analises" not in session:
        session["analises"] = []

    previsao_resultado = None
    erro_msg = None
    sucesso_msg = None
    rodada_atual = 100
    jogos_rodada = []



    times_disponiveis = obter_lista_times()

    if request.method == "POST":
        if "prever" in request.form:
            mandante = request.form.get("mandante")
            visitante = request.form.get("visitante")
            odd_betano_1 = request.form.get("odd_betano_1", "")
            odd_betano_x = request.form.get("odd_betano_x", "")
            odd_betano_2 = request.form.get("odd_betano_2", "")

            if mandante == visitante:
                erro_msg = "Selecione dois times diferentes para o confronto."
            else:
                try:
                    previsao_resultado = prever_partida(mandante, visitante)
                    
                    ev_data = {}
                    if odd_betano_1:
                        o1 = float(odd_betano_1)
                        ev_data["mandante"] = calcular_ev_e_kelly(o1, previsao_resultado["probabilidades"]["mandante"])
                        ev_data["mandante"]["odd_betano"] = o1
                    if odd_betano_x:
                        ox = float(odd_betano_x)
                        ev_data["empate"] = calcular_ev_e_kelly(ox, previsao_resultado["probabilidades"]["empate"])
                        ev_data["empate"]["odd_betano"] = ox
                    if odd_betano_2:
                        o2 = float(odd_betano_2)
                        ev_data["visitante"] = calcular_ev_e_kelly(o2, previsao_resultado["probabilidades"]["visitante"])
                        ev_data["visitante"]["odd_betano"] = o2

                    previsao_resultado["ev"] = ev_data
                except Exception as e:
                    erro_msg = f"Erro ao calcular previsão: {e}"

        elif "carregar_rodada" in request.form:
            try:
                rodada_atual = int(request.form.get("num_rodada", 100))
                jogos_rodada = obter_confrontos_rodada(rodada_atual)
                sucesso_msg = f"Jogos da rodada carregados!"
            except Exception as e:
                erro_msg = f"Erro ao carregar rodada: {e}"

        elif "salvar_analise" in request.form:
            mandante = request.form.get("mandante_salvar")
            visitante = request.form.get("visitante_salvar")
            aposta_recomendada = request.form.get("aposta_recomendada")
            odd_betano = request.form.get("odd_betano_salvar")
            ev_pct = request.form.get("ev_salvar")

            session["analises"].append({
                "confronto": f"{mandante} vs {visitante}",
                "aposta": aposta_recomendada,
                "odd_betano": odd_betano,
                "ev_pct": ev_pct
            })
            session.modified = True
            sucesso_msg = f"Análise salva para a Betano!"

        elif "limpar_analises" in request.form:
            session["analises"] = []
            session.modified = True
            sucesso_msg = "Lista de análises salvas foi limpa."

        elif "atualizar_stats" in request.form:
            ok, msg = atualizar_estatisticas_web()
            if ok:
                sucesso_msg = msg
            else:
                erro_msg = msg

    # Se a rodada não foi selecionada ainda via POST, carregar a rodada 1 por padrão
    if not jogos_rodada:
        jogos_rodada = obter_confrontos_rodada(rodada_atual)

    multiplas = gerar_multiplas_recomendadas(jogos_rodada)

    return render_template(
        "index.html",
        times=times_disponiveis,
        previsao=previsao_resultado,
        jogos_rodada=jogos_rodada,
        rodada_atual=rodada_atual,
        multiplas=multiplas,
        analises=session.get("analises", []),
        error=erro_msg,
        sucesso=sucesso_msg
    )

if __name__ == "__main__":
    app.run(debug=True)
