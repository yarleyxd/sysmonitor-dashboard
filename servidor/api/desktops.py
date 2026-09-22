import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException

rota = APIRouter(
    prefix = "/desktops",
    tags=["Desktops"]
)

desktops = []

LIMITE_OFFLINE = 40 # Limite em segundos p/ definir como "Offline" um desktop que não se comunicou recentemente.

CAMINHO_DADOS = Path(__file__).resolve().parent.parent / "dados" / "desktops.json"
CAMINHO_DADOS.parent.mkdir(parents=True, exist_ok=True)

def carregar_desktops():
    if CAMINHO_DADOS.is_file():
        try:
            with open(CAMINHO_DADOS, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, list):
                return dados
        except (json.JSONDecodeError, OSError) as erro:
            print(f"Aviso: não foi possível ler desktops.json ({erro}).")
    return []

def salvar_desktops():
    try: 
        with open(CAMINHO_DADOS, "w", encoding="utf-8") as arquivo:
            json.dump(desktops, arquivo, ensure_ascii=False, indent=2)
    except OSError as erro:
        print(f"Erro ao salvar desktops.json: {erro}")

desktops = carregar_desktops()

def obter_chave(desktop):
    return desktop.get("identificador") or desktop.get("nome")

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

@rota.get("/{identificador}")
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

    chave_recebida = obter_chave(informacoes)

    for indice, desktop in enumerate(desktops):
        if obter_chave(desktop) == chave_recebida:
            desktop_atualizado = {**desktop, **informacoes}
            desktops[indice] = desktop_atualizado
            salvar_desktops()
            return {
                "mensagem": "Desktop registrado com sucesso!",
                "desktop": desktop_atualizado
            }
            
    desktops.append(informacoes)
    salvar_desktops()

    return {
        "mensagem": "Desktop registrado com sucesso!",
        "desktop": informacoes,
    }

@rota.delete("/{identificador}")
def remover_desktop(identificador: str):
    for indice, desktop in enumerate(desktops):
        if obter_chave(desktop) == identificador or desktop.get("nome") == identificador:
            desktops.pop(indice)
            salvar_desktops
            return {"mensagem": "Desktop removido com sucesso!"}

    raise HTTPException(status_code=404, detail="Desktop não encontrado.")