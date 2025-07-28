from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import json
import os

# Salvar dados em JSON
def salvar_em_json(modelo, condicao, preco):
    dados = {
        "modelo": modelo,
        "marca": modelo.split()[0],
        "condicao": condicao,
        "preco": preco,
        "site": "Doji",
        "data_coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if os.path.exists("preco_temp.json"):
        with open("preco_temp.json", "r", encoding="utf-8") as f:
            try:
                todos_dados = json.load(f)
                if not isinstance(todos_dados, list):
                    todos_dados = [todos_dados]
            except json.JSONDecodeError:
                todos_dados = []
    else:
        todos_dados = []

    todos_dados.append(dados)

    with open("preco_temp.json", "w", encoding="utf-8") as f:
        json.dump(todos_dados, f, ensure_ascii=False, indent=2)

    print(f"[✔️] Dados salvos: {dados}")

# Buscar preço
def buscar_preco_no_doji(modelo_base, condicao, capacidade_esperada):
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    from selenium.webdriver.chrome.options import Options  # no início do arquivo (se ainda não tiver)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    wait = WebDriverWait(driver, 20)
    try:
        driver.get("https://trocaonline.doji.com.br/customer?storeId=67ec3771a94f224bcff23d55")
        time.sleep(1)

        input_busca = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='search-input']")))
        input_busca.send_keys(modelo_base)
        time.sleep(2)

        primeira_opcao = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid^='option-']")))
        primeira_opcao.click()

        capacidades = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid^='answer-']")))
        capacidade_clicada = False
        for c in capacidades:
            texto = c.text.strip().lower()
            if capacidade_esperada and capacidade_esperada.lower() == texto:
                c.click()
                capacidade_clicada = True
                print(f"[✔️] Capacidade encontrada: {texto}")
                break

        if not capacidade_clicada:
            print(f"[⚠️] Capacidade '{capacidade_esperada}' não encontrada. Usando padrão: {capacidades[0].text.strip()}")
            capacidades[0].click()

        cores = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid^='answer-']")))
        cores[-1].click()

        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='continue-button']"))).click()

        try:
            botao_sim = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='answer-Sim']")))
            botao_sim.click()
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='continue-button']"))).click()
        except:
            pass

        for i in range(9):
            try:
                if condicao["nome"] == "Perfeito estado":
                    nenhuma = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Nenhuma das anteriores')]")))
                    botao = nenhuma.find_element(By.XPATH, "./ancestor::*[self::button or self::label]")
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", botao)
                    botao.click()

                elif condicao["nome"] == "Com 1 problema":
                    opcoes = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//label[contains(@data-testid, 'answer-')]")))
                    if opcoes:
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", opcoes[0])
                        opcoes[0].click()

                elif condicao["nome"] == "Com todos os problemas":
                    opcoes = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//label[contains(@data-testid, 'answer-')]")))
                    for opcao in opcoes:
                        texto = opcao.text.strip().lower()
                        if "nenhuma das anteriores" not in texto:
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", opcao)
                            opcao.click()

                continuar = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Continuar')]")))
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", continuar)
                continuar.click()
                time.sleep(0.8)

            except Exception as e:
                print(f"[ERRO] ao responder pergunta {i+2}: {e}")
                break

        valor = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='store-price']"))).text
        valor = float(valor.replace("R$", "").replace(".", "").replace(",", ".").strip())
        print(f"[VALOR FINAL] {modelo_base} {capacidade_esperada} - {condicao['nome']} = R$ {valor:.2f}")
        return valor

    except Exception as e:
        print(f"[ERRO] {modelo_base} => {str(e)}")
    finally:
        driver.quit()

# Modelos e condições
modelos = [
    "SAMSUNG GALAXY S24 ULTRA 512GB",
    "SAMSUNG GALAXY S23 ULTRA 512GB",
    "APPLE IPHONE 11 64GB",
    "SAMSUNG GALAXY S22 ULTRA 256GB",
    "APPLE IPHONE 11 128GB",
    "SAMSUNG GALAXY S22 128GB",
    "SAMSUNG GALAXY S20 FE 128GB",
    "SAMSUNG GALAXY S21 5G 128GB",
    "SAMSUNG GALAXY S24 PLUS 512GB",
    "SAMSUNG GALAXY S21 FE 5G 128GB",
    "SAMSUNG GALAXY S23 ULTRA 256GB",
    "APPLE IPHONE 13 128GB",
    "SAMSUNG GALAXY S22 256GB",
    "APPLE IPHONE 12 128GB",
    "SAMSUNG GALAXY S10 128GB",
    "SAMSUNG GALAXY S23 PLUS 256GB",
    "SAMSUNG GALAXY S23 256GB",
    "APPLE IPHONE 12 64GB",
    "APPLE IPHONE XR 64GB",
    "SAMSUNG GALAXY S23 PLUS 512GB",
    "SAMSUNG GALAXY S20 128GB",
    "APPLE IPHONE XR 128GB",
    "SAMSUNG GALAXY S24 256GB",
    "SAMSUNG GALAXY S20 PLUS 128GB",
    "SAMSUNG GALAXY S23 128GB",
    "SAMSUNG GALAXY A54 5G 256GB",
    "SAMSUNG GALAXY A71 128GB",
    "SAMSUNG GALAXY NOTE 20 5G ULTRA 256GB",
    "SAMSUNG GALAXY S24 ULTRA 256GB",
    "SAMSUNG GALAXY A53 5G 128GB",
    "SAMSUNG GALAXY S21 PLUS 5G 128GB",
    "SAMSUNG GALAXY S21 PLUS 5G 256GB",
    "SAMSUNG GALAXY A32 5G 128GB",
    "SAMSUNG GALAXY S21 ULTRA 5G 256GB",
    "SAMSUNG GALAXY NOTE 20 5G 256GB",
    "SAMSUNG GALAXY Z FLIP 5 512GB",
    "SAMSUNG GALAXY S10 PLUS 128GB",
    "APPLE IPHONE 13 256GB",
    "SAMSUNG GALAXY S22 PLUS 128GB",
    "SAMSUNG GALAXY S24 PLUS 256GB",
    "SAMSUNG GALAXY J7 PRIME 32GB",
    "SAMSUNG GALAXY A52S 5G 128GB",
    "SAMSUNG GALAXY S23 FE 256GB",
    "SAMSUNG GALAXY S9 128GB",
    "SAMSUNG GALAXY A31 128GB",
    "SAMSUNG GALAXY S24 ULTRA 1000GB",
    "SAMSUNG GALAXY J5 PRIME 16GB",
    "SAMSUNG GALAXY S22 PLUS 256GB",
    "SAMSUNG GALAXY A10S 32GB",
    "SAMSUNG GALAXY A10 32GB",
    "SAMSUNG GALAXY A51 128GB",
    "APPLE IPHONE 11 256GB",
    "SAMSUNG GALAXY A14 5G 128GB",
    "SAMSUNG GALAXY NOTE 10 PLUS 256GB",
    "APPLE IPHONE 14 128GB",
    "SAMSUNG GALAXY A12 64GB",
    "SAMSUNG GALAXY A30S 64GB",
    "APPLE IPHONE 8 64GB",
    "SAMSUNG GALAXY S9 PLUS 128GB",
    "SAMSUNG GALAXY Z FLIP 4 128GB",
    "SAMSUNG GALAXY S8 DUOS 64GB",
    "SAMSUNG GALAXY A01 32GB",
    "SAMSUNG GALAXY A73 5G 128GB",
    "SAMSUNG GALAXY Z FLIP 3 128GB",
    "SAMSUNG GALAXY A30 64GB",
    "SAMSUNG GALAXY NOTE 10 256GB",
    "SAMSUNG GALAXY S22 ULTRA 512GB",
    "SAMSUNG GALAXY A50 128GB",
    "APPLE IPHONE 11 PRO MAX 256GB",
    "SAMSUNG GALAXY S24 ULTRA EXCLUSIVE 512GB",
    "APPLE IPHONE 13 INT 128GB",
    "SAMSUNG GALAXY S21 FE 5G 256GB",
    "SAMSUNG GALAXY A22 128GB",
    "SAMSUNG GALAXY J8 64GB",
    "SAMSUNG GALAXY A23 128GB",
    "SAMSUNG GALAXY A20 32GB",
    "APPLE IPHONE 8 PLUS 64GB",
    "APPLE IPHONE 11 PRO 256GB",
    "SAMSUNG GALAXY J5 16GB",
    "SAMSUNG GALAXY J6 32GB",
    "APPLE IPHONE 7 32GB",
    "SAMSUNG GALAXY Z FLIP 4 256GB",
    "APPLE IPHONE 13 PRO MAX 256GB",
    "SAMSUNG GALAXY S8 PLUS DUOS 64GB",
    "SAMSUNG GALAXY ZFLIP 6 256GB",
    "SAMSUNG GALAXY A21S 64GB",
    "SAMSUNG GALAXY A03 CORE 32GB",
    "APPLE IPHONE 13 MINI 128GB",
    "SAMSUNG GALAXY S23 FE 128GB",
    "SAMSUNG GALAXY A11 64GB",
    "SAMSUNG GALAXY A13 128GB",
    "MOTOROLA EDGE 20 PRO 256GB",
    "SAMSUNG GALAXY A20S 32GB",
    "APPLE IPHONE 12 PRO MAX 128GB",
    "MOTOROLA MOTO G7 PLAY 32GB",
    "MOTOROLA G6 PLAY 32GB",
    "SAMSUNG GALAXY S24 FE 256GB",
    "SAMSUNG GALAXY S20 FE 256GB",
    "SAMSUNG GALAXY A54 5G 128GB"
]


condicoes = [
    {"nome": "Perfeito estado", "defeitos": []},
    {"nome": "Com 1 problema", "defeitos": ["aleatorio"]},
    {"nome": "Com todos os problemas", "defeitos": "todos"}
]

# Loop principal
for modelo_completo in modelos:
    partes = modelo_completo.strip().split()
    capacidade_esperada = None
    if partes[-1].endswith("GB") or partes[-1].endswith("TB"):
        capacidade_esperada = partes[-1]
        modelo_base = " ".join(partes[:-1])
    else:
        modelo_base = modelo_completo

    for condicao in condicoes:
        print(f"[INFO] Buscando: {modelo_base} ({capacidade_esperada}) - {condicao['nome']}")
        preco = buscar_preco_no_doji(modelo_base, condicao, capacidade_esperada)
        if preco:
            salvar_em_json(modelo_completo, condicao["nome"], preco)
