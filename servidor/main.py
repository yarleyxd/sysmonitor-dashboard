import logging
import os
import sys
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import FastAPI, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

def diretorio_logs() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData"))
    else:
        base = Path.home() / ".local" / "share"

    return base / "sysmonitor" / "logs"

def configurar_logs() -> logging.Logger:
    log = logging.getLogger("sysmonitor.servidor")

    if log.handlers:
        return log

    log.setLevel(logging.INFO)
    log.propagate = False

    formato = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(formato)
    log.addHandler(console)

    try: 
        pasta = diretorio_logs()
        pasta.mkdir(parents=True, exist_ok= True)

        arquivo = RotatingFileHandler(
            pasta / "servidor.log",
            maxBytes=1_000_000,
            backupCount=5,
            encoding="utf-8",
        )
        arquivo.setFormatter(formato)
        log.addHandler(arquivo)
    except OSError as erro:
        log.warning("Não foi possível criar o arquivo de log (%s). Usando apenas o console.", erro)

    return log

log = configurar_logs() # antes dos imports, para registrar o carregamento de dados.

from servidor.api.desktops import CAMINHO_DADOS, rota, salvar_pendencias

PAINEL = RAIZ / "painel"
PAGINA_INICIAL = PAINEL / "models" / "index.html"

@asynccontextmanager
async def ciclo_de_vida(_aplicacao: FastAPI):
    log.info("Servidor iniciado. Dados em: %s", CAMINHO_DADOS)
    yield
    salvar_pendencias()
    log.info("Servidor encerrado.")

aplicacao = FastAPI(
    title="SysMonitor",
    description="Monitoramento de Rede e Desktop",
    version= "1.0.0",
    lifespan=ciclo_de_vida,
)

aplicacao.include_router(rota)

aplicacao.mount(
    "/arquivos",
    StaticFiles(directory=str(PAINEL / "arquivos")),
    name="arquivos",
)


@aplicacao.get("/", status_code=status.HTTP_200_OK)
def inicio():
    return FileResponse(PAGINA_INICIAL)    


@aplicacao.get("/status", status_code=status.HTTP_200_OK)
def verificar_status():
    return {
        "status": "Online",
    }

@aplicacao.get("/painel", status_code=status.HTTP_200_OK)
def abrir_painel():
    return FileResponse(PAGINA_INICIAL)