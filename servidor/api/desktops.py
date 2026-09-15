from fastapi import APIRouter, HTTPException
from datetime import datetime

rota = APIRouter(
    prefix = "/desktops",
    tags=["Desktops"]
)

desktops = []

@rota.get("/")
def listar_desktops():

    agora = datetime.now()

    for desktop in desktops:
        ultima_atividade = datetime.fromisoformat(
            desktop["ultima_atividade"]
        )

        segundos_desde_ultima_atividade = (agora - ultima_atividade).total_seconds()

        if segundos_desde_ultima_atividade > 40:
            desktop["status"] = "Offline"
        else:
            desktop["status"] = "Online"

    return {
        "Desktops": desktops
    }

@rota.get("/{nome}")
def obter_desktop(nome: str):
    for desktop in desktops:
        if desktop["nome"] == nome:
            return {
                "desktop": desktop
            }
    raise HTTPException(
        status_code=404, 
        detail="Desktop não encontrado."
        )

@rota.post("/registrar")
def registrar_desktop(informacoes: dict):
    nome = informacoes.get("nome")
    
    if not nome:
        raise HTTPException(
            status_code=400, 
            detail="Nome do desktop não informado."
            )

    informacoes["ultima_atividade"] = datetime.now().isoformat()
    
    desktop_existente = None

    for desktop in desktops:
        if desktop["nome"] == nome:
            desktop_existente = desktop
            break

    if desktop_existente:
        desktop_existente.update(informacoes)
        desktop_existente["status"] = "Online"

    else: 
        informacoes["status"] = "Online"
        desktops.append(informacoes)
    
    return {
        "mensagem": "Desktop registrado com sucesso!",
        "desktop": informacoes
        }
