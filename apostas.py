# apostas.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from itertools import product
import time
import logging
import os

# Setup do log
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/apostas.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def log(msg):
    print(msg)
    logging.info(msg)

def executar_apostas(jogos, valor, simular=False):
    if not isinstance(jogos, list) or not all("placares" in j and "timeA" in j and "timeB" in j for j in jogos):
        log("⚠️ Parâmetro 'jogos' inválido.")
        return
    if not isinstance(valor, (int, float)) or valor <= 0:
        log("⚠️ Parâmetro 'valor' inválido.")
        return

    log(f"🟡 Iniciando {'simulação' if simular else 'aposta real'} com {len(jogos)} jogos...")

    driver = webdriver.Chrome()  # Ou Edge/Firefox etc.
    try:
        driver.get("https://www.bet365.com/")
        input("🔐 Faça login e pressione ENTER para continuar...")  # Aguarda login manual

        combinacoes = list(product(*[j["placares"] for j in jogos]))
        log(f"🔁 {len(combinacoes)} combinações geradas.")

        for idx, combinacao in enumerate(combinacoes, start=1):
            log(f"🧩 [{idx}/{len(combinacoes)}] {combinacao}")

            for i, placar in enumerate(combinacao):
                jogo = jogos[i]
                time_a, time_b = jogo["timeA"], jogo["timeB"]
                busca = f"{time_a} vs {time_b}"

                try:
                    driver.get("https://www.bet365.com/")
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Buscar"]'))
                    )

                    search_box = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Buscar"]')
                    search_box.clear()
                    search_box.send_keys(busca)
                    search_box.send_keys(Keys.RETURN)

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, time_a))
                    ).click()

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Placar Exato")]'))
                    ).click()

                    opcao = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f'//button[contains(text(), "{placar}")]'))
                    )
                    opcao.click()
                    log(f"➕ {busca} - {placar} adicionado.")

                except Exception as e:
                    log(f"⚠️ Erro em {busca} com placar {placar}: {e}")
                    continue  # Continua para a próxima combinação

            try:
                if simular:
                    log("✅ Simulação concluída. Cupom montado.")
                    continue  # Não confirmar

                valor_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Valor"]'))
                )
                valor_input.clear()
                valor_input.send_keys(str(valor))

                confirmar = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Confirmar")]'))
                )
                confirmar.click()
                log("🎯 Aposta confirmada!\n")
                time.sleep(3)

            except Exception as e:
                log(f"⚠️ Erro ao finalizar aposta: {e}")
                continue  # Continua para a próxima combinação

    except Exception as e:
        log(f"⚠️ Erro geral: {e}")

    finally:
        driver.quit()
        log("✅ Todas as combinações processadas.")
