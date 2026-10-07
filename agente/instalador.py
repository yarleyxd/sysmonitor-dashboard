import ctypes
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

NOME_SERVICO = "SysMonitorAgente"
NOME_EXIBICAO = "SysMonitor Agente"

DIRETORIO_INSTALACAO = Path(
    os.environ.get("ProgramFiles", r"C:\Program Files")
) / "SysMonitor"

DIRETORIO_CONFIG = Path(
    os.environ.get("PROGRAMDATA", r"C:\ProgramData")
) / "sysmonitor"

CAMINHO_CONFIG = DIRETORIO_CONFIG / "config.json"
CAMINHO_AGENTE = DIRETORIO_INSTALACAO / "SysMonitorAgente.exe"

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

def verificar_administrador():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def obter_ip_servidor():
    while True:
        ip = input(
            "\n Digite o IP do servidor SysMonitor: "
        ).strip()

        if ip:
            return ip
        
        print("O IP não pode ficar vazio.")

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

    if not CAMINHO_AGENTE.exists():
        print("\nERRO: SysMonitorAgente.exe não foi copiado corretamente")

    print(f"Agente instalado em:")
    print(CAMINHO_AGENTE)

    return True

def remover_servico_anterior():
    print("\nVerificando instalação anterior...")

    resultado = subprocess.run(
        f'sc.exe query "{NOME_SERVICO}"',
        capture_output=True,
        text=True,
        shell=True
    )

    if resultado.returncode != 0:
        return
    print("Serviço existente encontrado.")
    
    executar_comando(
        f'"{CAMINHO_AGENTE}" stop'
    )

    executar_comando(
        f'"{CAMINHO_AGENTE}" remove'
    )

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

    resultado = subprocess.run(
        f'sc.exe query "{NOME_SERVICO}"',
        capture_output=True,
        text=True,
        shell=True
    )

    print(resultado.stdout)

    return resultado.returncode == 0

def instalar():
    print("=" * 50)
    print("     INSTALADOR DO SYSMONITOR")
    print("=" * 50)

    if not verificar_administrador():
        print("\nERRO: Execute o instalador como administrador.")

        input("\nPressione ENTER para sair...")
        return
    
    ip_servidor = obter_ip_servidor()

    print("\nConfigurando SysMonitor...")

    criar_configuracao(ip_servidor)

    if not copiar_agente():
        input("\nPressione ENTER para sair...")
        return
    
    remover_servico_anterior()

    if not instalar_servico():
        input("\nPressione ENTER para sair...")
        return

    if not iniciar_servico():
        input("\nPressione ENTER para sair...")
        return
    
    verificar_servico()

    print("\n" + "=" * 50)
    print("     INSTALAÇÃO CONCLUÍDA")
    print("=" * 50)

    print(f"\nServidor: {ip_servidor}:8000")
    print(f"Serviço: {NOME_SERVICO}")
    print("Inicialização: Automática")
    print("\nO agente continuará funcionando em segundo plano.")

    input("\nPressione ENTER para sair...")

if __name__ == "__main__":
    instalar()