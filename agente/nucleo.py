import logging
import time

from agente.config import AVISOS, CAMINHO_CONFIG, CONFIG, URL_SERVIDOR, configurar_logs
from agente.envio import enviar_informacoes
from agente.navegacao import obter_historico_navegacao
from agente.rede import obter_interfaces_rede
from agente.sistema import (
    coletar_informacoes_sistema,
    obter_aplicativos,
    obter_arquivos_abertos,
)

log = logging.getLogger("sysmonitor.agente.nucleo")

intervalo = CONFIG["intervalo"]
intervalo_pesado = CONFIG["intervalo_pesado"]
intervalo_maximo_falha = 60

ultimo_pesado = float("-inf")

cache_aplicativos= []
cache_navegacao = []
cache_arquivos = []

falhas_consecutivas = 0

def calcular_espera(falhas): 
    if falhas <= 0:
        return intervalo

    espera = intervalo * (2 ** min(falhas, 4))

    return min(espera, intervalo_maximo_falha)

def coletar_seguro(nome, funcao, anterior):
    """Uma coleta que falha não pode impedir os envios dos demais dados"""
    try:
        return funcao()
    except Exception:
        log.exception("Falha na coleta de %s; mantendo os dados anteriores.", nome)
        return anterior

def coletar_informacoes():
    global ultimo_pesado
    global cache_aplicativos
    global cache_navegacao
    global cache_arquivos

    agora = time.monotonic()

    if agora - ultimo_pesado >= intervalo_pesado:
        ultimo_pesado = agora

        cache_aplicativos = coletar_seguro("aplicativos", obter_aplicativos, cache_aplicativos)
        cache_navegacao = coletar_seguro("navegação", obter_historico_navegacao, cache_navegacao)
        cache_arquivos = coletar_seguro("arquivos abertos", obter_arquivos_abertos, cache_arquivos)

        log.info(
            "Coleta pesada concluída em %.1fs (aplicativos=%d, navegação=%d, arquivos=%d).",
            time.monotonic() - agora,
            len(cache_aplicativos),
            len(cache_navegacao),
            len(cache_arquivos),
        )
    
    informacoes = coletar_informacoes_sistema()

    informacoes["interfaces_rede"] = obter_interfaces_rede()
    informacoes["aplicativos"] = cache_aplicativos
    informacoes["navegacao"] = cache_navegacao
    informacoes["arquivos"] = cache_arquivos

    return informacoes

def registrar_informacoes(informacoes):
    log.debug(
        "Desktop: %s | IP: %s | CPU: %s%% | Apps: %d | Navegação: %d | Arquivos: %d",
        informacoes.get("nome"),
        informacoes.get("ip"),
        informacoes.get("cpu", {}).get("uso"),
        len(informacoes.get("aplicativos") or []),
        len(informacoes.get("cache_navegacao") or []),
        len(informacoes.get("cache_arquivos") or []),
    )

def aguardar(segundos, deve_parar):
    for _ in range(int(max(1, segundos))):
        
        if deve_parar():
            return False
        
        time.sleep(1)
    
    return True

def iniciar_agente(deve_parar=lambda: False):
    global falhas_consecutivas

    log.info("Iniciando agente. Servidor: %s", URL_SERVIDOR)
    log.info(
        "Configuração: %s | envio a cada %ss | coleta pesada a cada %ss",
        CAMINHO_CONFIG,
        intervalo,
        intervalo_pesado,
    )

    for aviso in AVISOS:
        log.warning(aviso)

    while not deve_parar():

        try:
            informacoes = coletar_informacoes()

            registrar_informacoes(informacoes)

            if enviar_informacoes(informacoes):
                if falhas_consecutivas > 0:
                    print("Comunicação restabelecida com o servidor.")
                    falhas_consecutivas = 0
            else:
                falhas_consecutivas += 1
        
        except Exception:
            print(f"Erro no ciclo de coleta/envio.")
            falhas_consecutivas += 1
        
        espera = calcular_espera(falhas_consecutivas)

        if falhas_consecutivas > 0:
            log.warning("Sem comunicação com o servidor. Nova tentativa em %ss.", espera)

        if not aguardar(espera, deve_parar):
           break
    
    log.info("Sinal de parada recebido. Agente encerrado.")
