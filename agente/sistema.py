import platform
import socket
import psutil
import time

def obter_nome_desktop():
    return socket.gethostname()

def obter_sistema_operacional():
    return platform.system() + " " + platform.release()

def obter_ip():
    try:
        conexao = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conexao.connect(("8.8.8.8", 80))
        ip = conexao.getsockname()[0]
        conexao.close()

        return ip

    except Exception:
        return "Não identificado"

def obter_cpu():
    return {
        "uso": psutil.cpu_percent(interval=1),
        "nucleos": psutil.cpu_count(logical=False),
        "threads": psutil.cpu_count(logical=True)
    }

def obter_ram():
    memoria = psutil.virtual_memory()

    return {
        "total_gb": round(memoria.total / (1024 ** 3), 2),
        "uso_percentual": memoria.percent,
        "disponivel_gb": round(memoria.available / (1024 ** 3), 2)
    }

def obter_armazenamento():
    disco = psutil.disk_usage("/")

    return {
        "total_gb": round(disco.total / (1024 ** 3), 2),
        "uso_percentual": disco.percent,
        "livre_gb": round(disco.free / (1024 ** 3), 2)
    }

def obter_tempo_ligado():
    inicio = psutil.boot_time()
    agora = time.time()

    segundos = agora - inicio

    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)

    return {
        "horas": horas,
        "minutos": minutos
    }

def obter_aplicativos():
    aplicativos = []

    for processo in psutil.process_iter(
        ["pid", "name", "username", "exe"]
    ):
        try:
            info = processo.info

            nome = info["name"]
            executavel = info["exe"]

            if not nome or not executavel:
                continue

            caminho = executavel.lower()

            if "\\windows\\" in caminho:
                continue

            if "\\windowapps\\" in caminho:
                continue

            aplicativos.append({
                "pid": info["pid"],
                "nome": nome,
                "usuario": info["username"],
                "caminho_executavel": executavel
            }) 

        except (
            psutil.NoSuchProcess, 
            psutil.AccessDenied, 
            psutil.ZombieProcess
        ):
            continue

        return aplicativos
            
def coletar_informacoes_sistema():
    return {
        "nome": obter_nome_desktop(),
        "ip": obter_ip(),
        "sistema_operacional": obter_sistema_operacional(),
        "cpu": obter_cpu(),
        "ram": obter_ram(),
        "armazenamento": obter_armazenamento(),
        "tempo_ligado": obter_tempo_ligado(),
        "aplicativos": obter_aplicativos()
    }
