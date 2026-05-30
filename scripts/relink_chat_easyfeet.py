#!/usr/bin/env python3
"""
Religa o chat Composer "EasyFeet" (29b7169a-...) ao workspace OneDrive,
sem precisar da pasta C:\\Cursor_Projetos\\EasyFeet.

IMPORTANTE: feche o Cursor completamente antes de executar.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

COMPOSER_ID = "29b7169a-0a59-4c09-bc15-2f4fc0a180eb"
OLD_WS_ID = "8d2bd14e226b556880a9e4a0f5100cac"
NEW_WS_ID = "248783461dff914aa952cd8fcdeffabe"

NEW_URI = {
    "$mid": 1,
    "fsPath": r"c:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet",
    "_sep": 1,
    "external": "file:///c%3A/Users/flavi/OneDrive/Documentos/Ideias_Projetos/Cursor_Projetos/EasyFeet",
    "path": "/c:/Users/flavi/OneDrive/Documentos/Ideias_Projetos/Cursor_Projetos/EasyFeet",
    "scheme": "file",
}

APP_DATA = Path.home() / "AppData" / "Roaming" / "Cursor" / "User"
GLOBAL_DB = APP_DATA / "globalStorage" / "state.vscdb"
OLD_WS_DB = APP_DATA / "workspaceStorage" / OLD_WS_ID / "state.vscdb"
NEW_WS_DB = APP_DATA / "workspaceStorage" / NEW_WS_ID / "state.vscdb"
GLASS_PROJECT_ID = "816871ca-f4d2-4302-934f-6d083697be1d"


def backup(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = path.with_suffix(path.suffix + f".backup-{stamp}")
    shutil.copy2(path, dest)
    return dest


def get_json(con: sqlite3.Connection, key: str):
    row = con.execute("SELECT value FROM ItemTable WHERE key=?", (key,)).fetchone()
    if not row:
        return None
    val = row[0]
    if isinstance(val, bytes):
        val = val.decode("utf-8")
    return json.loads(val)


def set_json(con: sqlite3.Connection, key: str, data) -> None:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    con.execute(
        "INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)",
        (key, payload),
    )


def patch_composer_headers(con: sqlite3.Connection) -> bool:
    data = get_json(con, "composer.composerHeaders")
    if not data:
        print("ERRO: composer.composerHeaders não encontrado.")
        return False

    composers = data.get("allComposers", [])
    found = False
    for c in composers:
        if c.get("composerId") == COMPOSER_ID:
            c["name"] = c.get("name") or "EasyFeet"
            c["workspaceIdentifier"] = {"id": NEW_WS_ID, "uri": NEW_URI}
            found = True
            break

    if not found:
        print(f"ERRO: chat {COMPOSER_ID} não está em composer.composerHeaders.")
        return False

    set_json(con, "composer.composerHeaders", data)
    print("OK: composer.composerHeaders — EasyFeet ligado ao workspace OneDrive.")
    return True


def patch_glass_projects(con: sqlite3.Connection) -> None:
    data = get_json(con, "glass.localAgentProjects.v1")
    if not isinstance(data, list):
        return
    for p in data:
        if p.get("id") == GLASS_PROJECT_ID:
            p["name"] = "EasyFeet"
            p["workspace"] = {"id": NEW_WS_ID, "uri": NEW_URI}
            break
    set_json(con, "glass.localAgentProjects.v1", data)
    print("OK: glass.localAgentProjects.v1 — projeto EasyFeet atualizado.")


def patch_new_workspace_composer(con: sqlite3.Connection) -> None:
    data = get_json(con, "composer.composerData") or {}
    ids = list(data.get("selectedComposerIds") or [])
    focused = list(data.get("lastFocusedComposerIds") or [])
    for cid in (COMPOSER_ID,):
        if cid not in ids:
            ids.insert(0, cid)
        if cid not in focused:
            focused.insert(0, cid)
    data["selectedComposerIds"] = ids
    data["lastFocusedComposerIds"] = focused
    data["hasMigratedComposerData"] = True
    data["hasMigratedMultipleComposers"] = True
    set_json(con, "composer.composerData", data)
    print("OK: workspace OneDrive — EasyFeet na lista de compositors.")


def copy_workspace_keys() -> None:
    if not OLD_WS_DB.exists() or not NEW_WS_DB.exists():
        print("AVISO: state.vscdb antigo/novo ausente; pulando cópia de aiService.")
        return
    keys = ("aiService.generations", "aiService.prompts")
    old = sqlite3.connect(OLD_WS_DB)
    new = sqlite3.connect(NEW_WS_DB)
    for key in keys:
        row = old.execute("SELECT value FROM ItemTable WHERE key=?", (key,)).fetchone()
        if row:
            new.execute(
                "INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)",
                (key, row[0]),
            )
            print(f"OK: copiado {key} do workspace antigo para o novo.")
    new.commit()
    new.close()
    old.close()


def main() -> int:
    if not GLOBAL_DB.exists():
        print(f"ERRO: não achei {GLOBAL_DB}")
        return 1
    if not NEW_WS_DB.exists():
        print(
            "ERRO: workspace OneDrive ainda não existe no Cursor. "
            "Abra a pasta OneDrive no Cursor uma vez, feche de novo e repita."
        )
        return 1

    for db in (GLOBAL_DB, NEW_WS_DB):
        try:
            test = sqlite3.connect(db, timeout=2)
            test.execute("BEGIN IMMEDIATE")
            test.rollback()
            test.close()
        except sqlite3.OperationalError:
            print(
                f"ERRO: {db} está bloqueado. Feche o Cursor por completo e execute de novo."
            )
            return 1

    print("Criando backups...")
    backup(GLOBAL_DB)
    if NEW_WS_DB.exists():
        backup(NEW_WS_DB)

    g = sqlite3.connect(GLOBAL_DB)
    if not patch_composer_headers(g):
        g.close()
        return 1
    patch_glass_projects(g)
    g.commit()
    g.close()

    n = sqlite3.connect(NEW_WS_DB)
    patch_new_workspace_composer(n)
    n.commit()
    n.close()

    copy_workspace_keys()

    print()
    print("Concluído. Próximos passos:")
    print("  1. Abra o Cursor em:")
    print(r"     C:\Users\flavi\OneDrive\Documentos\Ideias_Projetos\Cursor_Projetos\EasyFeet")
    print("  2. No histórico de chats, abra «EasyFeet».")
    print("  3. Pode apagar C:\\Cursor_Projetos\\EasyFeet_OLD (com Cursor fechado).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
