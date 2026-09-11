from fastapi import APIRouter

rota = APIRouter(
    prefix = "/desktops",
    tags=["Desktops"]
)

desktops = []

@rota.get("/")
def listar_desktops():
    return {
        "Desktops": desktops
    }

@rota.post("/registrar")
def registrar_desktop(informacoes: dict):
    nome = informacoes.get("nome")
    desktop_existente = None
    for desktop in desktops:
        if desktop["nome"] == nome:
            desktop_existente = desktop
            break

    if desktop_existente:
        desktop_existente.update(informacoes)
        desktop_existente["status"] = "online"

    else: 
        informacoes["status"] = "online"
        desktops.append(informacoes)
    
    return {
        "mensagem": "Desktop registrado com sucesso!",
        "desktop": informacoes
        }
