import requests

ENDERECO_LOCAL = "http://127.0.0.1:8000" # Localhost para teste, mudar para o endereço do servidor.

def enviar_informacoes(informacoes):
    endereco = ENDERECO_LOCAL + "/desktops/registrar"

    try:
        resposta = requests.post(
            endereco,
            json=informacoes,
            timeout= 5
        )
        
        if resposta.status_code == 200:
            print("Informações do sistema enviadas com sucesso!")
                
        else:
            print(
                f"Falha ao enviar informações do sistema."
                f"Código de status: {resposta.status_code}"
            )
    except requests.exceptions.RequestException as erro:
        print(f"Erro ao enviar informações do sistema: {erro}")