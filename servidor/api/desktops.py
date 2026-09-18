from fastapi import APIRouter, HTTPException
from datetime import datetime

rota = APIRouter(
    prefix = "/desktops",
    tags=["Desktops"]
)

desktops = []

LIMITE_OFFLINE = 40 # Limite em segundos p/ definir como "Offline" um desktop que não se comunicou recentemente.

def atualizar_status(desktop):
    ultima_atividade = desktop.get("ultima_atividade")
    
    try:
        referencia = datetime.fromisoformat(ultima_atividade)
        segundos = (datetime.now() - referencia).total_seconds()
        desktop["status"] = "Online" if segundos <= LIMITE_OFFLINE else "Offline"
    except (TypeError, ValueError):
        desktop["status"] = "Offline"
    
    return desktop

@rota.get("/")
def listar_desktops():
    for desktop in desktops:
        atualizar_status(desktop)

    return {
        "Desktops": desktops,
    }

@rota.get("/{nome}")
def obter_desktop(nome: str):
    for desktop in desktops:
        atualizar_status(desktop)
        if desktop.get("nome") == nome:
            return {
                "desktop": desktop,
            }

    raise HTTPException(
        status_code=404, 
        detail="Desktop não encontrado.",
        )

@rota.post("/registrar")
def registrar_desktop(informacoes: dict):
    nome = informacoes.get("nome")
    
    if not nome:
        raise HTTPException(
            status_code=400, 
            detail="Nome do desktop não informado.",
            )

    informacoes["ultima_atividade"] = datetime.now().isoformat()
    informacoes["status"] = "Online"

    for indice, desktop in enumerate(desktops):
        if desktop.get("nome") == nome:
            desktop_atualizado = {**desktop, **informacoes}
            desktops[indice] = desktop_atualizado
            return {
                "mensagem": "Desktop registrado com sucesso!",
                "desktop": desktop_atualizado
            }
            
    desktops.append(informacoes)

    return {
        "mensagem": "Desktop registrado com sucesso!",
        "desktop": informacoes
    }