import json
import logging
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, status

from servidor.schemas import DesktopRegistroSchema

log = logging.getLogger("sysmonitor.servidor.desktops")

rota = APIRouter(
    prefix = "/desktops",
    tags=["Desktops"]
)

LIMITE_OFFLINE = 40 # Limite em segundos p/ definir como "Offline" um desktop que não se comunicou recentemente.
INTERVALO_SALVAR = 30 # Segundos entre gravações no disco (dados fica sempre atualizado na memória)

def diretorio_dados() -> Path:
    """Dados ficam fora da pasta do projeto."""
    ambiente = os.environ.get("SYSMONITOR_DADOS")
    if ambiente:
        return Path(ambiente)

    if os.name == "nt":
        base = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData"))
    else:
        base = Path.home() / ".local" / "share"
    
    return base / "sysmonitor" / "dados"

CAMINHO_DADOS = Path(__file__).resolve().parent.parent / "dados" / "desktops.json"
CAMINHO_DADOS.parent.mkdir(parents=True, exist_ok=True)

trava = threading.Lock() # protege a lista 'desktops' e os marcadores abaixo
trava_arquivo = threading.Lock() # garante uma gravação em disco por vez

_alterado = False # dados na memória que ainda não foram gravados
_ultimo_salvamento = float("-inf") # momento da ultima gravação

def preservar_arquivo_corrompido() -> None:
    destino = CAMINHO_DADOS.with_name(
        f"{CAMINHO_DADOS.name}.corrompido-{datetime.now():%Y%m%d-%H%M%S}"
    )

    try:
        CAMINHO_DADOS.replace(destino)
        log.error("Arquivo de dados inválido. Cópia preservada em %s", destino)
    except OSError as erro:
        log.error("Arquivo de dados inválido e não foi possível preservá-lo:  %s", erro)

def carregar_desktops() -> List[Dict[str, Any]]:
    if not CAMINHO_DADOS.is_file():
        return []

        try:
            with open(CAMINHO_DADOS, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except ValueError:
            preservar_arquivo_corrompido()
            return []
        except OSError as erro:
            log.erro("Não foi possível ler %s: %s", CAMINHO_DADOS, erro)
            return []

        if not isinstance(dados, list):
            preservar_arquivo_corrompido()
            return []

def salvar_desktops() -> bool:
    "Grava o arquivo de forma atômica"
    global _alterado, _ultimo_salvamento

    temporario = CAMINHO_DADOS.with_name(CAMINHO_DADOS.name + ".tmp")
    
    with trava_arquivo:
        with trava:
            copia = [dict(desktop) for desktop in desktops]
            _alterado = False
            _ultimo_salvamento = time.monotonic()
        try:
            with open(temporario, "w", encoding="utf-8") as arquivo:
                json.dump (copia, arquivo, ensure_ascii=False, separators=(",", ":"))
                arquivo.flush()
                os.fsync(arquivo.fileno())
            os.replace(temporario, CAMINHO_DADOS)
            return True
        
        except (OSError, TypeError, ValueError) as erro:
            log.error("Erro ao salvar %s: %s", CAMINHO_DADOS, erro)

            with trava:
                _alterado = True
            
            return False

def salvar_pendencias() -> None:
    """Chamada ao encerrar o servidor: grava o que não foi para o disco"""
    if _alterado:
        salvar_desktops()

def marcar_alterado_e_verificar_salvamento() -> bool:
    """Chamar com 'trava' adquirida."""
    global _alterado, _ultimo_salvamento

    _alterado = True
    agora = time.monotonic

    if agora - _ultimo_salvamento >= INTERVALO_SALVAR:
        _ultimo_salvamento = agora
        return True
    
    return False

desktops: List[Dict[str, Any]] = carregar_desktops()
log.info("%d desktop(s) carregado(s) de %s", len (desktops), CAMINHO_DADOS)

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
    with trava:
        for desktop in desktops:
            atualizar_status(desktop)
        
        resultado = [dict(desktop) for desktop in desktops]
            
    return {"Desktops": resultado}

@rota.get("/{identificador}", status_code=status.HTTP_200_OK)
def obter_desktop(identificador: str):
    with trava:
        for desktop in desktops:
            atualizar_status(desktop)
            if obter_chave(desktop) == identificador or desktop.get("nome") == identificador:
                return {"desktop": dict(desktop)}

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

    with trava:
        for indice, desktop in enumerate(desktops):
            if obter_chave(desktop) == chave_recebida:
                desktops[indice] = {**desktops, **informacoes}
                break
        else:
            desktops.append(informacoes)
            log.info("Novo desktop registrado: %s", chave_recebida)
            
        deve_salvar = marcar_alterado_e_verificar_salvamento()

    if deve_salvar:
        salvar_desktops()

    return {"mensagem": "Desktop registrado com sucesso!"}

@rota.delete("/{identificador}", status_code=status.HTTP_200_OK)
def remover_desktop(identificador: str):
    global _alterado
    
    removido = False

    with trava:
        for indice, desktop in enumerate(desktops):
            if obter_chave(desktop) == identificador or desktop.get("nome") == identificador:
                desktops.pop(indice)
                _alterado = True
                removido = True
                break
    if not removido:
        raise HTTPException(status_code=404, detail="Desktop não encontrado.")

    log.info("Desktop removido: %s", identificador)
    salvar_desktops()

    return {"mensagem": "Desktop removido com sucesso!"}