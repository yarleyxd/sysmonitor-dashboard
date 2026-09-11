from agente.sistema import coletar_informacoes_sistema
from agente.rede import obter_interfaces_rede
from agente.envio import enviar_informacoes


def iniciar_agente():

    informacoes = coletar_informacoes_sistema()
    informacoes["interfaces_rede"] = obter_interfaces_rede()

    print("Informações coletadas:")
    print(informacoes)

    enviar_informacoes(informacoes)


if __name__ == "__main__":
    iniciar_agente()