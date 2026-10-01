import json 
import os
import sys
from pathlib import Path

def diretorio_programdata():
    if os.name == "nt":
        base = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData"))
    else:
        base = Path("/etc")
    return base / "sysmonitor"

def caminhos_possiveis():
    caminhos = []

    ambiente = os.environ.get("SYSMONITOR_CONFIG")
    if ambiente:
        caminhos.append(Path(ambiente))

    caminhos.append(diretorio_programdata() / "config.json")

    if getattr(sys, "frozen", False):
        caminhos.append(Path(sys.executable).resolve().parent / "config.json")
    
    caminhos.append(Path(__file__).resolve().parent / "config.json")
    return caminhos

def encontrar_config():
    for caminho in caminhos_possiveis():
        if caminho.is_file():
            return caminho
    return diretorio_programdata() / "config.json"


CAMINHO_CONFIG = encontrar_config()

PADRAO = {
    "servidor_ip": "127.0.0.1",
    "servidor_porta": "8000",
    "intervalo": 5,
    "intervalo_pesado": 30,
}

def aplicar_variaveis_ambiente(config): 
    variaveis = {
        "SYSMONITOR_SERVIDOR_IP": ("servidor_ip", str),
        "SYSMONITOR_SERVIDOR_PORTA": ("servidor_porta", int),
        "SYSMONITOR_INTERVALO": ("intervalo", int),
        "SYSMONITOR_INTERVALO_PESADO": ("intervalo_pesado", int),
    }

    for nome, (chave, tipo) in variaveis.items():
        valor = os.environ.get(nome)
        
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
            print(f"Aviso: não foi possível ler {CAMINHO_CONFIG}. ({erro}).")
        
    config = aplicar_variaveis_ambiente(config)

    try:
        config["servidor_porta"] = int(config["servidor_porta"])
    except (TypeError, ValueError):
        config["servidor_porta"] = PADRAO["servidor_porta"]
    return config


CONFIG = carregar_config()
URL_SERVIDOR = f"http://{CONFIG['servidor_ip']}:{CONFIG['servidor_porta']}"