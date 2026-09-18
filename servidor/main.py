from fastapi import FastAPI
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from servidor.api.desktops import rota 

RAIZ = Path(__file__).resolve().parent.parent
PAINEL = RAIZ / "painel"

aplicacao = FastAPI(
    title="SysMonitor",
    description="Monitoramento de Rede e Desktop",
    version = "1.0.0",
)

aplicacao.include_router(rota)

aplicacao.mount(
    "/arquivos",
    StaticFiles(directory= PAINEL / "arquivos"),
    name="arquivos",
)


@aplicacao.get("/")
def inicio():
        return FileResponse(
            PAINEL / "models" / "index.html"
        )     


@aplicacao.get("/status")
def verificar_status():
    return {
        "status": "Online",
    }

@aplicacao.get("/painel")
def abrir_painel():
    return FileResponse(
    PAINEL / "models" / "index.html"
    )