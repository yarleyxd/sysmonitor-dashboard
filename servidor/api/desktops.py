from fastapi import APIRouter

rota = APIRouter(
    prefix = "/desktops",
    tags=["Desktops"]
)

@rota.get("/")
def listar_desktops():
    return {
        "Desktops": []
    }
