import time
from datetime import datetime

from agente.envio import enviar_informacoes
from agente.rede import obter_interfaces_rede
from agente.sistema import coletar_informacoes_sistema
from agente.sistema import obter_arquivos_abertos 
from agente.navegacao import obter_historico_navegacao

intervalo = 5
intervalo_pesado = 30
ultimo_pesado = 0.0
cache_navegacao = []
cache_arquivos = []

def iniciar_agente():
    global ultimo_pesado, cache_navegacao, cache_arquivos

    print("Iniciando agente...")
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

            enviar_informacoes(informacoes)

        except Exception as erro:
            print(f"Erro ao coletar informações: {erro}")

        time.sleep(intervalo)

if __name__ == "__main__":
    iniciar_agente()