import ctypes
import ipaddress
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

NOME_SERVICO = "SysMonitorAgente"
PORTA_SERVIDOR = 8000

DIRETORIO_INSTALACAO = Path(
    os.environ.get("ProgramFiles", r"C:\Program Files")
) / "SysMonitor"

DIRETORIO_CONFIG = Path(
    os.environ.get("PROGRAMDATA", r"C:\ProgramData")
) / "sysmonitor"

CAMINHO_CONFIG = DIRETORIO_CONFIG / "config.json"
CAMINHO_AGENTE = DIRETORIO_INSTALACAO / "SysMonitorAgente.exe"

def executar_comando(comando):
    # errors="replace": a saída do Windows usa a página de código do console
    # (acentos) e não deve derrubar o instalador.
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        errors="replace",
        shell=True
    )

    if resultado.stdout:
        print(resultado.stdout.strip())

    if resultado.stderr:
        print(resultado.stderr.strip())

    return resultado.returncode

def consultar_servico():
    resultado = subprocess.run(
        f'sc.exe query "{NOME_SERVICO}"',
        capture_output=True,
        text=True,
        errors="replace",
        shell=True
    )

    return resultado.returncode == 0, resultado.stdout

def verificar_administrador():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def obter_ip_servidor():
    while True:
        ip = input(
            "\n Digite o IP do servidor SysMonitor:"
        ).strip()

        if endereco_valido(ip):
            return ip
        
        print("Informe um IP (ex.: 192.168.0.1) ou o nome do computador do servidor.")

def criar_configuracao(ip_servidor):
    DIRETORIO_CONFIG.mkdir(
        parents=True,
        exist_ok=True
    )

    configuracao = {
        "servidor_ip": ip_servidor,
        "servidor_porta": PORTA_SERVIDOR,
        "intervalo": 5,
        "intervalo_pesado": 30
    }

    with open(CAMINHO_CONFIG, "w", encoding="utf-8") as arquivo:
        json.dump(
            configuracao,
            arquivo,
            indent=4,
            ensure_ascii=False
        )

def criar_configuracao(ip_servidor):
    DIRETORIO_CONFIG.mkdir(
        parents=True,
        exist_ok=True
    )

    configuracao = {
        "servidor_ip": ip_servidor,
        "servidor_porta": "8000",
        "intervalo": 5,
        "intervalo_pesado": 30
    }

    with open(CAMINHO_CONFIG,"w", encoding="utf-8") as arquivo:
        json.dump(
            configuracao,
            arquivo,
            indent=4,
            ensure_ascii=False
        )
    
    print(f"Configuração criada em:")
    print(CAMINHO_CONFIG)

def testar_conexao(ip_servidor):
    """Aviso apenas: servidor pode estar desligado, e o agente continua tentando."""
    print("\nTestando comunicação com o servidor...")

    try:
        with urllib.request.urlopen(
            f"http://{ip_servidor}:{PORTA_SERVIDOR}/status", timeout=5
        ) as resposta:
            if resposta.status == 200:
                print("Servidor respondeu corretamente.")
                return True
    except (OSError, ValueError):
        pass

    print(
        "AVISO: o servidor não respondeu. Confira o IP, se o servidor está em execução."
        "e se o firewall libera a porta 8000. O agente continuará tentando."
    )
    return False

def localizar_agente():
    if getattr(sys, "frozen", False):
        diretorio_temporario = Path(sys._MEIPASS)
        
        agente = (
            diretorio_temporario
            / "SysMonitorAgente"
            / "SysMonitorAgente.exe"
        )

        if agente.is_file():
            return agente
    
    caminhos = [
        Path(__file__).resolve().parent.parent
        / "dist"
        / "SysMonitorAgente"
        / "SysMonitorAgente.exe",

        Path.cwd()
        / "dist"
        / "SysMonitorAgente.exe",

        Path.cwd()
        / "dist"
        / "SysMonitorAgente"
        / "SysMonitorAgente.exe",
    ]

    for agente in caminhos:
        if agente.is_file():
            return agente

    return None

def servico_parado(saida):
    saida: saida.upper()
    return "STOPPED" in saida or re.search(r"(STATE|ESTADO)\s*:\s*1\b", saida) is not None

def aguardar_parada(limite_segundos=30):
    for _ in range(limite_segundos):
        existe, saida = consultar_servico()

        if not existe or servico_parado(saida):
            return True
        
        time.sleep(1)
    
    return False

def remover_servico_anterior():
    """Deve rodar antes de copiar os arquivos: com o serviço ativo o Windows bloqueia o exe."""
    print("\nVerificando instalação anterior...")

    existe, _ = consultar_servico()

    if not existe:
        return True
    
    print("Serviço existente encontrado. Parando...")
    executar_comando(f'sc.exe stop "{NOME_SERVICO}"')

    if not aguardar_parada():
        print("O serviço não parou a tempo. Encerrando o processo...")
        executar_comando(f'taskkill /F /T /IM "{CAMINHO_AGENTE.name}"')

        if not aguardar_parada(10):
            print("ERRO: não foi possível parar o serviço anterior.")
            return False
    
    if CAMINHO_AGENTE.is_file():
        executar_comando(f'"{CAMINHO_AGENTE}" remove')
    else:
        executar_comando(f'sc.exe delete "{NOME_SERVICO}"')
    
    return True

def copiar_agente():
    agente_origem = localizar_agente()

    if agente_origem is None:
        print(
            "\nERRO: SysMonitorAgente.exe não foi encontrado."
        )
        return False

    DIRETORIO_INSTALACAO.mkdir(
        parents=True,
        exist_ok=True
    )

    pasta_origem = agente_origem.parent

    try:
        if (pasta_origem / "_internal").is_dir():
            print("\nCopiando arquivos do agente...")

            for item in pasta_origem.iterdir():
                destino = DIRETORIO_INSTALACAO / item.name

                if item.is_dir():
                    shutil.copytree(
                        item,
                        destino,
                        dirs_exist_ok=True
                )
            else:
                shutil.copy2(
                    item,
                    destino
                )
        else:
            shutil.copy2(
                agente_origem, CAMINHO_AGENTE
            )
    except OSError as erro:
        print(f"\nERRO ao copiar os arquivos do agente: {erro}")
        return False

    if not CAMINHO_AGENTE.exists():
        print("\nERRO: SysMonitorAgente.exe não foi copiado corretamente")
        return False

    print(f"Agente instalado em:")
    print(CAMINHO_AGENTE)

    return True


def instalar_servico():
    print("\nInstalando serviço...")

    codigo = executar_comando(
        f'"{CAMINHO_AGENTE}" install'
    )

    if codigo != 0:
        print("Não foi possível instalar o serviço.")
        return False
    
    print("\nConfigurando inicialização automática...")
    
    codigo = executar_comando(
        f'sc.exe config "{NOME_SERVICO}" start= auto'
    )

    if codigo != 0:
        print("Não foi possível configurar a inicialização automática")
        return False
    
    # Se o processo do serviço falhar, o Windows reiniciar (1min)
    codigo = executar_comando(
        f'sc.ex failure "{NOME_SERVICO}" reset = 86400'
        f'actions= restart/60000/restart/60000/restart/6000'
    )

    if codigo != 0:
        print("AVISO: não foi possível condigurar a recuperação automática do serviço.")

    return True


def iniciar_servico():
    print("Iniciando serviço...")

    codigo = executar_comando(
        f'"{CAMINHO_AGENTE}" start'
    )

    if codigo != 0:
        print("Não foi possível iniciar o serviço.")
        return False
    
    print("\nServiço iniciado com sucesso!")
    return True

def verificar_servico():
    print("\nVerificando serviço...")

    existe, saida = consultar_servico()
    print(saida)

    return existe

def pausar():
    input("\nPressione ENTER para sair...")

def instalar():
    print("=" * 50)
    print("     INSTALADOR DO SYSMONITOR")
    print("=" * 50)

    if not verificar_administrador():
        print("\nERRO: Execute o instalador como administrador.")
        pausar()
        return
    
    ip_servidor = obter_ip_servidor()

    print("\nConfigurando SysMonitor...")

    criar_configuracao(ip_servidor)
    testar_conexao(ip_servidor)

    if not remover_servico_anterior():
        pausar()
        return

    if not copiar_agente():
        pausar()
        return

    if not instalar_servico():
        pausar()
        return

    if not iniciar_servico():
        pausar()
        return

    verificar_servico()

    print("\n" + "=" * 50)
    print("     INSTALAÇÃO CONCLUÍDA")
    print("=" * 50)

    print(f"\nServidor: {ip_servidor}:{PORTA_SERVIDOR}")
    print(f"Serviço: {NOME_SERVICO}")
    print("Inicialização: Automática")
    print("Log do agente: C:\\ProgramData\\sysmonitor\\logs\\agente.log")
    print("\nO agente continuará funcionando em segundo plano.")

    pausar()

if __name__ == "__main__":
    instalar()