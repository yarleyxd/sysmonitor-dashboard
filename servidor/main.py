import sys
from pathlib import Path
from fastapi import FastAPI, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from servidor.api.desktops import rota 

PAINEL = RAIZ / "painel"

aplicacao = FastAPI(
    title="SysMonitor",
    description="Monitoramento de Rede e Desktop",
    version = "1.0.0",
)

aplicacao.include_router(rota)

aplicacao.mount(
    "/arquivos",
    StaticFiles(directory=str(PAINEL / "arquivos")),
    name="arquivos",
)


@aplicacao.get("/", status_code=status.HTTP_200_OK)
def inicio():
        return FileResponse(PAINEL / "models" / "index.html")     


@aplicacao.get("/status", status_code=status.HTTP_200_OK)
def verificar_status():
    return {
        "status": "Online",
    }

@aplicacao.get("/painel", status_code=status.HTTP_200_OK)
def abrir_painel():
    return FileResponse(PAINEL / "models" / "index.html")