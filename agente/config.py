import json 
import os
from pathlib import Path

CAMINHO_CONFIG = Path(__file__).resolve().parent / "config.json"

PADRAO = {
    "servidor_ip": "127.0.0.1",
    "servidor_porta": "8000",
    "intervalo": 5,
    "intervalo_pesado": 30,
}

#Sobrepoem o config.json
def sobrescrever_com_variaveis_ambiente(config): 
    mapeamento = {
        "SYSMONITOR_SERVIDOR_IP": ("servidor_ip", str),
        "SYSMONITOR_SERVIDOR_PORTA": ("servidor_porta", int),
        "SYSMONITOR_INTERVALO": ("intervalo", int),
        "SYSMONITOR_INTERVALO_PESADO": ("intervalo_pesado", int),
    }

    for variavel, (chave, tipo) in mapeamento.items():
        valor = os.environ.get(variavel)
        if valor is not None:
            try:
                config[chave] = tipo(valor)
            except ValueError:
                pass
    return config

def carregar_config():
    config = dict(PADRAO)

    if CAMINHO_CONFIG.is_file():
        try:
            with open(CAMINHO_CONFIG, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, dict):
                config.update(dados)
        except (json.JSONDecodeError, OSError) as erro:
            print(f"Aviso: não foi possível ler config.json ({erro}). Usando padrões")
        
    config = sobrescrever_com_variaveis_ambiente(config)

    return config

CONFIG = carregar_config()
URL_SERVIDOR = f"http://{CONFIG['servidor_ip']}:{CONFIG['servidor_porta']}"