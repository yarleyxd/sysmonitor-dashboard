from fastapi import FastAPI
from servidor.api.desktops import rota 

aplicacao = FastAPI(
    title="SysMonitor",
    description="Monitoramente de Rede e Desktop",
    version = "1.0.0"
)

aplicacao.include_router(rota)

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