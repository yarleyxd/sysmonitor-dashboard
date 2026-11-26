import logging
import requests
from agente.config import URL_SERVIDOR 

log = logging.getLogger("sysmonitor.agente.enivo")

ENDERECO = f"{URL_SERVIDOR}/desktops/registrar"
TIMEOUT = (5, 10) # Conexão, reposta (segundos)

# A sessão reaproveita a conexão TCP entre envios
_sessao = requests.Session()


def enviar_informacoes(informacoes: dict) -> bool:
    try:
        resposta = _sessao.post(ENDERECO, json=informacoes, timeout=TIMEOUT)
    except requests.exceptions.RequestException as erro:
        log.warning("Falha de comunicação com %s: %s", ENDERECO, erro)
        return False
    
    if resposta.status_code == 200:
        log.debug("Informações enviadas com sucesso.")
        return True
    
    log.warning(
        "O servidor recusou o envio (HTTP %s): %s",
        resposta.status_code,
        resposta.text[:300],
    )
    return False