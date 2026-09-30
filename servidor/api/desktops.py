import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, status
from servidor.schemas import DesktopRegistroSchema

rota = APIRouter(
    prefix = "/desktops",
    tags=["Desktops"]
)

LIMITE_OFFLINE = 40 # Limite em segundos p/ definir como "Offline" um desktop que não se comunicou recentemente.

CAMINHO_DADOS = Path(__file__).resolve().parent.parent / "dados" / "desktops.json"
CAMINHO_DADOS.parent.mkdir(parents=True, exist_ok=True)

def carregar_desktops() -> List[Dict[str, Any]]:
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

desktops: List[Dict[str, Any]] = carregar_desktops()

def obter_chave(desktop: Dict[str,Any]) -> str:
    return str(desktop.get("identificador") or desktop.get("nome") or "")

def atualizar_status(desktop: Dict[str, Any]) -> Dict[str, Any]:
    ultima_atividade = desktop.get("ultima_atividade")
    
    try:
        if ultima_atividade:
            referencia = datetime.fromisoformat(ultima_atividade)
            segundos = (datetime.now() - referencia).total_seconds()
            desktop["status"] = "Online" if segundos <= LIMITE_OFFLINE else "Offline"
        else: 
            desktop["status"] = "Offline"
    except (TypeError, ValueError):
        desktop["status"] = "Offline"
    
    return desktop

@rota.get("/", status_code=status.HTTP_200_OK)
def listar_desktops():
    for desktop in desktops:
        atualizar_status(desktop)

    return {
        "Desktops": desktops,
    }

@rota.get("/{identificador}", status_code=status.HTTP_200_OK)
def obter_desktop(identificador: str):
    for desktop in desktops:
        atualizar_status(desktop)
        if obter_chave(desktop) == identificador or desktop.get("nome") == identificador:
            return {
                "desktop": desktop,
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Desktop não encontrado.",
    )

@rota.post("/registrar", status_code=status.HTTP_200_OK)
def registrar_desktop(payload: DesktopRegistroSchema):
    informacoes = payload.model_dump()
    
    if not informacoes.get("arquivos") and informacoes.get("arquivos_abertos"):
        informacoes["arquivos"] = informacoes.pop("arquivos_abertos")
    elif "arquivos_abertos" in informacoes:
        informacoes.pop("arquivos_abertos")

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

@rota.delete("/{identificador}", status_code=status.HTTP_200_OK)
def remover_desktop(identificador: str):
    for indice, desktop in enumerate(desktops):
        if obter_chave(desktop) == identificador or desktop.get("nome") == identificador:
            desktops.pop(indice)
            salvar_desktops()
            return {"mensagem": "Desktop removido com sucesso!"}

    raise HTTPException(status_code=404, detail="Desktop não encontrado.")