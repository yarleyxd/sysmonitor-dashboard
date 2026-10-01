import time
from datetime import datetime

from agente.config import CONFIG, URL_SERVIDOR
from agente.envio import enviar_informacoes
from agente.rede import obter_interfaces_rede
from agente.sistema import coletar_informacoes_sistema, obter_arquivos_abertos
from agente.navegacao import obter_historico_navegacao

intervalo = CONFIG["intervalo"]
intervalo_pesado = CONFIG["intervalo_pesado"]
intervalo_maximo_falha = 60

ultimo_pesado = 0.0

cache_navegacao = []
cache_arquivos = []

falhas_consecutivas = 0

def calcular_espera(falhas): 
    if falhas <= 0:
        return intervalo

    espera = intervalo * (2 ** min(falhas, 4))

    return min(espera, intervalo_maximo_falha)

def coletar_informacoes():
    global ultimo_pesado
    global cache_navegacao
    global cache_arquivos

    agora = time.time()

    if agora - ultimo_pesado >= intervalo_pesado:
        cache_navegacao = obter_historico_navegacao()
        cache_arquivos = obter_arquivos_abertos()
        ultimo_pesado = agora
    
    informacoes = coletar_informacoes_sistema()

    informacoes["interfaces_rede"] = obter_interfaces_rede()
    informacoes["navegacao"] = cache_navegacao
    informacoes["arquivos"] = cache_arquivos
    informacoes["ultima_comunicacao"] = datetime.now().isoformat()

    return informacoes

def registrar_informacoes(informacoes):
    print(
            f"  Desktop: {informacoes.get('nome')}, | "
            f"IP: {informacoes.get('ip')} | "
            f"CPU: {informacoes.get('cpu', {}).get('uso')}% | "
            f"Apps: {len(informacoes.get('aplicativos') or [])} | "
            f"Navegacao: {len(cache_navegacao)} | "
            f"Arquivos: {len(cache_arquivos)} | " 
    )

def aguardar(segundos, deve_parar):
    for _ in range(int(max(1, segundos))):
        
        if deve_parar():
            return False
        
        time.sleep(1)
    
    return True

def iniciar_agente(deve_parar=lambda: False):
    global falhas_consecutivas

    print("Iniciando agente...")
    print(f"Servidor configurado: {URL_SERVIDOR}")
    print(f"Enviando informações a cada {intervalo} segundos.")

    while not deve_parar():

        try:
            informacoes = coletar_informacoes()

            registrar_informacoes(informacoes)

            sucesso = enviar_informacoes(informacoes)

            if sucesso:
                if falhas_consecutivas > 0:
                    print("Comunicação restabelecida com o servidor.")

                    falhas_consecutivas = 0
            else:
                falhas_consecutivas += 1
        
        except Exception as erro:
            print(f"Erro ao coletar informações: {erro}")
            falhas_consecutivas += 1
        
        espera = calcular_espera(falhas_consecutivas)

        if falhas_consecutivas > 0:
            print(
                f"Sem comunicação com o servidor. "
                f"Nova tentativa em {espera}s."
            )

        if not aguardar(espera, deve_parar):
            print("Sinal de parada recebido. Encerrando agente.")
            return
