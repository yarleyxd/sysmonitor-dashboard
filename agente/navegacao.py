import logging
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

log = logging.getLogger("sysmonitor.agente.navegacao")

LIMITE_REGISTROS = 50

PERFIS_IGNORADOS = {"public", "default", "default user", "all users", "defaultuser0"}

BASES_CHROMIUM = [
    (("Google", "Chrome", "User Data"), "Chrome"),
    (("Microsoft", "Edge", "User Data"), "Edge"),
    (("BraveSoftware", "Brave-Browser", "User Data"), "Brave"),
    (("Vivaldi", "User Data"), "Vivaldi"),
    (("Chromium", "User Data"), "Chromium"),
]

# Datas guardadas em microssegundos, em UTC, a partir de épocas diferentes.
EPOCA_CHROMIUM = datetime(1601, 1, 1, tzinfo=timezone.utc)
EPOCA_FIREFOX = datetime(1970, 1, 1, tzinfo=timezone.utc)

CONSULTAS = {
    "chromium": (
        "SELECT url, title, last_visit_time FROM urls "
        "ORDER BY last_visit_time DESC LIMIT ?",
        EPOCA_CHROMIUM,
    ),
    "firefox": (
        "SELECT url, title, last_visit_date FROM moz_places "
        "WHERE last_visit_date IS NOT NULL "
        "ORDER BY last_visit_date DESC LIMIT ?",
        EPOCA_FIREFOX,
    ),
}

# Evita repetir o mesmo aviso a cada coleta (ex.: navegador aberto bloqueando o arquivo).
_avisos_emitidos = set()

def avisar_uma_vez(chave, mensagem, *argumentos):
    if chave not in _avisos_emitidos:
        _avisos_emitidos.add(chave)
        log.warning(mensagem, *argumentos)

def pastas_de_usuarios():
    if os.name != "nt":
        return []
    
    raiz = Path(os.environ.get("SystemDrive", "C:") + "\\") / "Users"

    try:
        return [
            pasta for pasta in raiz.iterdir()
            if pasta.is_dir() and pasta.name.lower() not in PERFIS_IGNORADOS
        ]
    except OSError as erro:
        avisar_uma_vez("usuarios", "Não foi possível listar %s: %s", raiz, erro)
        return []

def subpastas(base):
    try:
        return [pasta for pasta in base.iterdir() if pasta.is_dir()]
    except OSError as erro:
        avisar_uma_vez(("subpastas", str(base)), "Não foi possível listar %s: %s", base, erro)
        return []

def caminhos_historicos():
    caminhos = []

    for usuario in pastas_de_usuarios():
        local = usuario / "AppData" / "Local"
        roaming = usuario / "AppData" / "Roaming"

        for partes, navegador in BASES_CHROMIUM:
            base = local.joinpath(*partes)

            if not base.is_dir():
                continue

            for perfil in subpastas(base):
                historico = perfil / "History"
                if historico.is_file():
                    caminhos.append((historico, navegador, "chromium"))
        
        perfis_firefox = roaming / "Mozilla" / "Firefox" / "Profiles"

        if perfis_firefox.is_dir():
            for perfil in subpastas(perfis_firefox):
                places = perfil / "places.sqlite"
                if places.is_file():
                    caminhos.append((places, "Firefox", "firefox"))
    
    return caminhos


def converter_tempo(tempo, epoca):
    if not tempo:
        return None
    try:
        return (epoca + timedelta(microseconds=int(tempo))).isoformat()
    except (TypeError, ValueError, OverflowError):
        return None

def copiar_historico(origem, destino):
    """Copia o banco e o arquivo -wal, quando existir."""
    try:
        shutil.copy2(origem, destino)
    except OSError as erro:
        avisar_uma_vez(("copia", str(origem)), "Não foi possível copiar o histórico %s: %s",origem, erro)
        return False
    
    _avisos_emitidos.discard(("copia", str(origem)))

    wal = origem.with_name(origem.name + "-wal")

    if wal.is_file():
        try:
            shutil.copy2(wal, destino.with_name(destino.name + "-wal"))
        except OSError:
            pass
    return True


def ler_historico(caminho, navegador, tipo):
    consulta, epoca = CONSULTAS[tipo]
    registros = []

    with tempfile.TemporaryDirectory(prefix="sysmonitor-", ignore_cleanup_errors=True) as pasta:
        copia = Path(pasta) / "historico.sqlite"

        if not copiar_historico(caminho, copia):
            return registros
        
        conexao = None

        try:
            conexao = sqlite3.connect(copia)

            for url, titulo, tempo in conexao.execute(consulta, (LIMITE_REGISTROS,)):
                registros.append({
                    "url": url,
                    "titulo": titulo or "",
                    "acessado_em": converter_tempo(tempo, epoca),
                    "navegador": navegador,
                })
        except sqlite3.Error as erro:
            avisar_uma_vez(("leitura", str(caminho)), "Não foi possível ler o histórico %s: %s", caminho, erro)
        finally:
            if conexao is not None:
                conexao.close()

    return registros

def obter_historico_navegacao():
    registros = []

    for caminho, navegador, tipo in caminhos_historicos():
        try:
            registros.extend(ler_historico(caminho, navegador, tipo))
        except Exception:
            log.exception("Erro inesperado ao ler o histórico %s", caminho)
        
    registros.sort(
        key=lambda item: item.get("acessado_em") or "",
        reverse=True
    )

    return registros[:LIMITE_REGISTROS]