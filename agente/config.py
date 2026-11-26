import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
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
#Os avisos ficam guardados e o agente os registra no log assim que ele é iniciado.
AVISOS = []

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
                AVISOS.append(f"Variável {nome} inválida ({valor!r}); ignorada.")

    return config

def carregar_config():
    config = dict(PADRAO)

    if CAMINHO_CONFIG.is_file():
        try:
            with open(CAMINHO_CONFIG, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, dict):
                config.update(dados)
            else:
                AVISOS.append(f"{CAMINHO_CONFIG} não contém um objeto JSON; usando valores padrão.")
        except (json.JSONDecodeError, OSError) as erro:
            print(f"Não foi possível ler {CAMINHO_CONFIG} ({erro}); usando valores padrão.")
    elif "SYSMONITOR_SERVIDOR_IP" not in os.environ:
        AVISOS.append(
            f"Arquivo de configuração não encontrado ({CAMINHO_CONFIG}); "
            f"usando o servidor padrão {PADRAO['servidor_ip']}."
        )
        
    config = aplicar_variaveis_ambiente(config)

    for chave in ("servidor_porta", "intervalo", "intervalo_pesado"):
        try:
            config[chave] = int(config[chave])
            if config[chave] < 1:
                raise ValueError
        except (TypeError, ValueError):
            AVISOS.append(f"Valor inválido para '{chave}' ({config[chave]!r}); usando {PADRAO[chave]}.")

    return config


CONFIG = carregar_config()
URL_SERVIDOR = f"http://{CONFIG['servidor_ip']}:{CONFIG['servidor_porta']}"

def configurar_logs():
    "Log em arquivo: (C:\\ProgramData\\sysmonitor\\logs\\agente.log)."
    log = logging.getLogger("sysmonitor.agente")

    if log.handlers:
        return log
    
    log.setLevel(logging.INFO)
    log.propagate = False

    formato = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # Como serviço (ou sem o console) não existe stderr.
    if sys.stderr is not None:
        console = logging.StreamHandler()
        console.setFormatter(formato)
        log.addHandler(console)

    try:
        pasta = diretorio_programdata() / "logs"
        pasta.mkdir(parents=True, exist_ok=True)

        arquivo = RotatingFileHandler(
            pasta / "agente.log",
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        arquivo.setFormatter(formato)
        log.addHandler(arquivo)
    except OSError:
        pass
    
    return log