import os
import shutil
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

LIMITE_REGISTROS = 50


def caminhos_historicos():
    caminhos = []
    home = Path.home()

    if os.name == "nt":
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        roaming = Path(os.environ.get("APPDATA", ""))

        bases_chromium = [
            (local / "Google" / "Chrome" / "User Data", "Chrome"),
            (local / "Microsoft" / "Edge" / "User Data", "Edge"),
            (local / "BraveSoftware" / "Brave-Browser" / "User Data", "Brave"),
            (local / "Vivaldi" / "User Data", "Vivaldi"),
            (local / "Chromium" / "User Data", "Chromium"),
        ]

        for base, navegador in bases_chromium:
            if not base.exists():
                continue
            for perfil in base.iterdir():
                if not perfil.is_dir():
                    continue
                historico = perfil / "History"
                if historico.is_file():
                    caminhos.append((historico, navegador, "chromium"))

        perfis_firefox = roaming / "Mozilla" / "Firefox" / "Profiles"
        if perfis_firefox.exists():
            for perfil in perfis_firefox.iterdir():
                places = perfil / "places.sqlite"
                if places.is_file():
                    caminhos.append((places, "Firefox", "firefox"))

    else:  # Linux/macOS
        bases_chromium = [
            (home / ".config" / "google-chrome", "Chrome"),
            (home / ".config" / "chromium", "Chromium"),
            (home / ".config" / "BraveSoftware" / "Brave-Browser", "Brave"),
            (home / ".config" / "microsoft-edge", "Edge"),
            (home / ".config" / "vivaldi", "Vivaldi"),
        ]

        for base, navegador in bases_chromium:
            if not base.exists():
                continue
            for perfil in base.iterdir():
                if not perfil.is_dir():
                    continue
                historico = perfil / "History"
                if historico.is_file():
                    caminhos.append((historico, navegador, "chromium"))

        perfis_firefox = home / ".mozilla" / "firefox"
        if perfis_firefox.exists():
            for perfil in perfis_firefox.iterdir():
                places = perfil / "places.sqlite"
                if places.is_file():
                    caminhos.append((places, "Firefox", "firefox"))

    return caminhos


def converter_chromium(tempo):
    if not tempo:
        return None
    try:
        return (datetime(1601, 1, 1) + timedelta(microseconds=int(tempo))).isoformat()
    except (TypeError, ValueError, OverflowError):
        return None


def converter_firefox(tempo):
    if not tempo:
        return None
    try:
        return (datetime(1970, 1, 1) + timedelta(microseconds=int(tempo))).isoformat()
    except (TypeError, ValueError, OverflowError):
        return None


def copiar_para_temp(caminho):
    try:
        temporario = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite")
        temporario.close()
        shutil.copy2(caminho, temporario.name)
        return temporario.name
    except Exception:
        return None


def ler_chromium(caminho, navegador):
    registros = []
    copia = copiar_para_temp(caminho)
    if not copia:
        return registros

    try:
        conexao = sqlite3.connect(copia)
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT url, title, last_visit_time FROM urls "
            "ORDER BY last_visit_time DESC LIMIT ?",
            (LIMITE_REGISTROS,),
        )
        for url, titulo, tempo in cursor.fetchall():
            registros.append({
                "url": url,
                "titulo": titulo or "",
                "acessado_em": converter_chromium(tempo),
                "navegador": navegador,
            })
        conexao.close()
    except Exception:
        pass
    finally:
        try:
            os.remove(copia)
        except OSError:
            pass

    return registros


def ler_firefox(caminho, navegador):
    registros = []
    copia = copiar_para_temp(caminho)
    if not copia:
        return registros

    try:
        conexao = sqlite3.connect(copia)
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT url, title, last_visit_date FROM moz_places "
            "WHERE last_visit_date IS NOT NULL "
            "ORDER BY last_visit_date DESC LIMIT ?",
            (LIMITE_REGISTROS,),
        )
        for url, titulo, tempo in cursor.fetchall():
            registros.append({
                "url": url,
                "titulo": titulo or "",
                "acessado_em": converter_firefox(tempo),
                "navegador": navegador,
            })
        conexao.close()
    except Exception:
        pass
    finally:
        try:
            os.remove(copia)
        except OSError:
            pass

    return registros


def obter_historico_navegacao():
    registros = []

    for caminho, navegador, tipo in caminhos_historicos():
        try:
            if tipo == "chromium":
                registros.extend(ler_chromium(caminho, navegador))
            elif tipo == "firefox":
                registros.extend(ler_firefox(caminho, navegador))
        except Exception:
            continue

    registros.sort(
        key=lambda item: item.get("acessado_em") or "",
        reverse=True,
    )

    return registros[:LIMITE_REGISTROS]