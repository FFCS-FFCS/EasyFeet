"""
Teste automatico do layout do modulo Pacientes (altura da tabela visivel).

Uso: py -3 scripts/test_pacientes_layout.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _find_widget_by_text(parent, text: str):
    for child in parent.winfo_children():
        try:
            if str(child.cget("text")) == text:
                return child
        except Exception:
            pass
        found = _find_widget_by_text(child, text)
        if found is not None:
            return found
    return None


def _find_treeview(parent):
    import tkinter as tk
    from tkinter import ttk

    for child in parent.winfo_children():
        if isinstance(child, ttk.Treeview):
            return child
        found = _find_treeview(child)
        if found is not None:
            return found
    return None


def main() -> int:
    import customtkinter as ctk

    from easyfeet.db import SessionLocal, init_db
    from easyfeet.gui import EasyFeetApp
    from easyfeet.services import EasyFeetService

    init_db()
    session = SessionLocal()
    service = EasyFeetService(session)
    errors: list[str] = []

    app = EasyFeetApp(service)
    app.geometry("1280x800")
    app._show_module("pacientes")
    app.update_idletasks()
    app.update()
    app.after(300, app.update_idletasks)
    app.update()

    tree = None
    content_children = app.content.winfo_children()
    if not content_children:
        errors.append("content sem filhos apos abrir Pacientes")
    else:
        root = content_children[0]
        root_h = root.winfo_height()
        table_label = _find_widget_by_text(root, "Pacientes cadastrados")
        tree = _find_treeview(root)

        if table_label is None:
            errors.append("rotulo 'Pacientes cadastrados' nao encontrado")
        if tree is None:
            errors.append("ttk.Treeview da lista de pacientes nao encontrado")
        else:
            tree_h = tree.winfo_height()
            tree_rows = len(tree.get_children())
            if tree_h < 80:
                errors.append(f"altura da tabela muito pequena: {tree_h}px (esperado >= 80)")
            if tree_rows < 1 and len(service.clientes.listar()) > 0:
                errors.append("tabela sem linhas mas ha pacientes no banco")

        if root_h < 200:
            errors.append(f"altura total do modulo pacientes baixa: {root_h}px")

    if errors:
        session.close()
        app.destroy()
        print("FALHOU:")
        for e in errors:
            print(f"  - {e}")
        return 1

    tree_h = tree.winfo_height() if tree is not None else 0
    tree_rows = len(tree.get_children()) if tree is not None else 0
    session.close()
    app.destroy()

    print("OK: layout Pacientes — tabela presente e com altura utilizavel.")
    print(f"    Treeview: {tree_h}px, {tree_rows} linha(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
