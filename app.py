
from flask import Flask, render_template, request, redirect, url_for, session
from threading import Thread
import json
import os
from apostas import executar_apostas

app = Flask(__name__)
app.secret_key = "chave_secreta_simples"

@app.route("/", methods=["GET", "POST"])
def index():
    if "jogos" not in session:
        session["jogos"] = []

    if request.method == "POST":
        if "add_jogo" in request.form:
            time_a = request.form.get("timeA")
            time_b = request.form.get("timeB")
            placares = request.form.get("placares")
            try:
                placares_list = [p.strip() for p in placares.split(",") if p.strip()]
                session["jogos"].append({"timeA": time_a, "timeB": time_b, "placares": placares_list})
                session.modified = True
            except Exception as e:
                return render_template("index.html", error="Erro ao adicionar jogo: " + str(e), jogos=session["jogos"])

        elif "executar" in request.form:
            valor = float(request.form.get("valor"))
            simular = request.form.get("simular") == "on"
            jogos = session.get("jogos", [])
            session.pop("jogos", None)

            thread = Thread(target=executar_apostas, args=(jogos, valor, simular))
            thread.start()
            return redirect(url_for("index"))

    logs = []
    if os.path.exists("logs/apostas.log"):
        with open("logs/apostas.log") as f:
            logs = f.readlines()[-30:]

    return render_template("index.html", logs=logs, jogos=session.get("jogos", []))

if __name__ == "__main__":
    app.run(debug=True)
