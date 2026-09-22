import requests

from agente.config import URL_SERVIDOR 

def enviar_informacoes(informacoes):
    endereco = URL_SERVIDOR + "/desktops/registrar"

    try:
        resposta = requests.post(
            endereco,
            json=informacoes,
            timeout= 5
        )
        
        if resposta.status_code == 200:
            print("Informações do sistema enviadas com sucesso!")
            return True
                
            print(
                f"Falha ao enviar informações do sistema."
                f"Código de status: {resposta.status_code}"
            )
            return False

    except requests.exceptions.RequestException as erro:
        print(f"Erro ao enviar informações do sistema: {erro}")
        return False