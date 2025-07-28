import MySQLdb
import json
from datetime import datetime
import os
import sys

# Configurações do banco remoto
DB_CONFIG = {
    'host': '########', #name of the server
    'user': '#######', #username
    'passwd': '#######',  #password
    'db': '#######', #name of the database
    'charset': '###' #charset
}

JSON_FILE = "preco_temp.json"

# Verifica se o arquivo existe
if not os.path.exists(JSON_FILE):
    print("❌ Arquivo preco_temp.json não encontrado.")
    sys.exit(1)

# Lê os dados do JSON
try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        dados = json.load(f)
except Exception as e:
    print(f"❌ Erro ao carregar JSON: {e}")
    sys.exit(1)

if not isinstance(dados, list) or not dados:
    print("⚠️ Nenhum dado válido para inserir.")
    sys.exit(0)

# Conecta ao banco
try:
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
except Exception as e:
    print(f"❌ Erro ao conectar no banco: {e}")
    sys.exit(1)

# Query de inserção
query = """
INSERT INTO precos_celulares_doji (marca, modelo, condicao, preco, site, data_coleta)
VALUES (%s, %s, %s, %s, %s, %s)
"""

# Insere todos os itens
registros_inseridos = 0
for item in dados:
    try:
        data_coleta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(query, (
            item.get("marca"),
            item.get("modelo"),
            item.get("condicao"),
            item.get("preco"),
            item.get("site"),
            data_coleta
        ))
        registros_inseridos += 1
    except Exception as e:
        print(f"❌ Erro ao inserir registro: {item} → {e}")

# Finaliza
conn.commit()
cursor.close()
conn.close()
print(f"[✔️] {registros_inseridos} registros inseridos com sucesso.")
