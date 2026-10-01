import subprocess
import sys

NOME_SERVICO = "SysMonitorAgente"
NOME_EXIBICAO = "SysMonitor Agente"

def executar_comando(comando):
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        shell=True
    )

    if resultado.stdout:
        print(resultado.stdout.strip())

    if resultado.stderr:
        print(resultado.stderr.strip())

    return resultado.returncode

def instalar():
    print("Instalando serviço...")

    codigo = executar_comando(
        f'sc create "{NOME_SERVICO}" '
        f'binPath= "{sys.executable} -m agente.servico" '
        f'DisplayName= "{NOME_EXIBICAO}" '
        f'start= auto'
    )

    if codigo != 0:
        print("Não foi possível instalar o serviço.")
        return

    executar_comando(
        f'sc description "{NOME_SERVICO}" '
        f'"Agente responsável pelo monitoramento do computador."'
    )

    if codigo == 0:
        print("Serviço instalado com sucesso.")
    else: 
        print("Serviço instalado, mas não foi possível definir a descrição!")

def iniciar():
    print("Iniciando serviço...")

    codigo = executar_comando(
        f'sc start "{NOME_SERVICO}"'
    )

    if codigo == 0:
        print("Serviço iniciado.")
    else:
        print("Não foi possível iniciar o serviço.")

def parar():
    print("Parando serviço...")

    codigo = executar_comando(
        f'sc stop "{NOME_SERVICO}"'
    )

    if codigo == 0:
        print("Serviço parado.")
    else:
        print("Não foi possível parar o serviço.")

def remover():
    print("Removendo serviço...")

    executar_comando(
        f'sc stop "{NOME_SERVICO}"'
    )

    codigo = executar_comando(
        f'sc delete "{NOME_SERVICO}"'
    )

    if codigo == 0:
        print("Serviço removido.")
    else:
        print("Não foi possível remover o serviço.")

def status():
    executar_comando(
        f'sc query "{NOME_SERVICO}"'
    )

def mostrar_ajuda():
    print()
    print("SysMonitor Agente - Instalador")
    print()
    print("Comandos:")
    print(" instalar - Instala o serviço")
    print(" iniciar - Inicia o serviço")
    print(" parar - Para o serviço")
    print(" remover - Remove o serviço")
    print(" status - Mostra o status do serviço")
    print()

def main():
    if len(sys.argv) < 2:
        mostrar_ajuda()
        return

    comando = sys.argv[1].lower()

    if comando == "instalar":
        instalar()
    
    elif comando == "iniciar":
        iniciar()

    elif comando == "parar":
        parar()

    elif comando == "remover":
        remover()

    elif comando == "status":
        status()

    else: 
        mostrar_ajuda()

if __name__ == "__main__":
    main()