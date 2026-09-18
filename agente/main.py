import time
from datetime import datetime
from agente.sistema import coletar_informacoes_sistema
from agente.rede import obter_interfaces_rede
from agente.envio import enviar_informacoes

intervalo = 5

def iniciar_agente():
    print("Iniciando agente...")
    print(f"Enviando informações a cada {intervalo} segundos.")

    while True:
        try:
            informacoes = coletar_informacoes_sistema()
            informacoes["interfaces_rede"] = obter_interfaces_rede()
            informacoes["ultima_comunicacao"] = datetime.now().isoformat()

            print("Informações coletadas:")
            print(
                f"  Desktop: {informacoes.get('nome')}, | "
                f"IP: {informacoes.get('ip')} | "
                f"CPU: {informacoes.get('cpu')} | "
                f"Apps: {len(informacoes.get('aplicativos') or [])}"
            )

            enviar_informacoes(informacoes)

        except Exception as erro:
            print(f"Erro ao coletar informações: {erro}")

        time.sleep(intervalo)

if __name__ == "__main__":
    iniciar_agente()