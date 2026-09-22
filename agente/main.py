import time
from datetime import datetime

from agente.config import CONFIG, URL_SERVIDOR
from agente.envio import enviar_informacoes
from agente.rede import obter_interfaces_rede
from agente.sistema import coletar_informacoes_sistema
from agente.sistema import obter_arquivos_abertos 
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

def iniciar_agente():
    global ultimo_pesado, cache_navegacao, cache_arquivos, falhas_consecutivas

    print("Iniciando agente...")
    print(f"Servidor configurado: {URL_SERVIDOR}")
    print(f"Enviando informações a cada {intervalo} segundos.")

    while True:
        try:
            agora = time.time()

            if agora - ultimo_pesado >= intervalo_pesado:
                cache_navegacao = obter_historico_navegacao()
                cache_arquivos = obter_arquivos_abertos()
                ultimo_pesado = agora

            informacoes = coletar_informacoes_sistema()
            informacoes["interfaces_rede"] = obter_interfaces_rede()
            informacoes["navegacao"] = cache_navegacao
            informacoes["arquivos_abertos"] = cache_arquivos
            informacoes["ultima_comunicacao"] = datetime.now().isoformat()

            print("Informações coletadas:")
            print(
                f"  Desktop: {informacoes.get('nome')}, | "
                f"IP: {informacoes.get('ip')} | "
                f"CPU: {informacoes.get('cpu', {}).get('uso')}% | "
                f"Apps: {len(informacoes.get('aplicativos') or [])}"
                f"Navegacao: {len(cache_navegacao)} | "
                f"Arquivos: {len(cache_arquivos)} | " 
            )

            sucesso = enviar_informacoes(informacoes)
            falhas_consecutivas = 0 if sucesso else falhas_consecutivas + 1

        except Exception as erro:
            print(f"Erro ao coletar informações: {erro}")
            falhas_consecutivas += 1

        espera = calcular_espera(falhas_consecutivas)
        if falhas_consecutivas > 0:
            print(f"Sem comunicação com o servidor. Nova tentativa em {espera}s.")
        time.sleep(espera)

if __name__ == "__main__":
    iniciar_agente()