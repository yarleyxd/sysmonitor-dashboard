from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from servidor.api.desktops import rota 

aplicacao = FastAPI(
    title="SysMonitor",
    description="Monitoramente de Rede e Desktop",
    version = "1.0.0"
)

aplicacao.include_router(rota)

aplicacao.mount(
    "/arquivos",
    StaticFiles(directory="painel/arquivos"),
    name="arquivos"
)

@aplicacao.get("/")
def inicio():
    return {
        "status": "Online",
        "mensagem": "Bem-vindo ao SysMonitor!"
        }

@aplicacao.get("/status")
def verificar_status():
    return {
        "status": "Online",
    }

@aplicacao.get("/painel")
def abrir_painel():
    return FileResponse(
    "painel/models/index.html"
    )