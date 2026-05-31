"""
Smoke: sidebar render, botao Abrir ficha clinica, Hub v0.

Uso: py -3 scripts/test_hub_smoke.py
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


def _find_widget_text_contains(parent, fragment: str):
    for child in parent.winfo_children():
        try:
            if fragment in str(child.cget("text")):
                return child
        except Exception:
            pass
        found = _find_widget_text_contains(child, fragment)
        if found is not None:
            return found
    return None


def main() -> int:
    from easyfeet.db import SessionLocal, init_db
    from easyfeet.gui import EasyFeetApp
    from easyfeet.services import EasyFeetService

    init_db()
    session = SessionLocal()
    service = EasyFeetService(session)
    errors: list[str] = []

    app = EasyFeetApp(service)
    app.geometry("1280x800")
    app.update_idletasks()
    app.update()

    # Sidebar com accordions (onde falhou btn_h)
    if not app._sidebar_menu_host.winfo_children():
        errors.append("sidebar sem itens de menu")

    app._show_module("pacientes")
    app.update_idletasks()
    app.update()

    if _find_widget_by_text(app.content, "Historico de marcacoes") is not None:
        errors.append("Pacientes ainda exibe historico de marcacoes (M3 migrou para Hub)")

    ficha_btn = _find_widget_by_text(app.content, "Abrir ficha clinica")
    if ficha_btn is None:
        errors.append("botao 'Abrir ficha clinica' nao encontrado em Pacientes")

    app._show_module("efm_marcadores")
    app.update_idletasks()
    app.update()
    if _find_widget_by_text(app.content, "Ir para Pacientes") is None:
        errors.append("Plantigrafo Analise sem ecrã Hub-first (M4)")

    clientes = service.clientes.listar()
    if not clientes:
        errors.append("sem pacientes no banco para testar Hub")
    else:
        app._open_paciente_hub(clientes[0].id, section="timeline")
        app.update_idletasks()
        app.update()
        if app.menu_state.current_module != "paciente_hub":
            errors.append("Hub nao activou modulo paciente_hub")
        if app._hub_cliente_id != clientes[0].id:
            errors.append("Hub com cliente_id incorrecto")
        if _find_widget_by_text(app.content, "Linha do tempo") is None:
            errors.append("Hub timeline sem titulo Linha do tempo")
        regs = service.marcacoes.listar_marcacoes_por_cliente(clientes[0].id)
        if regs and _find_widget_by_text(app.content, "Plantigrafo") is None:
            errors.append("Timeline sem bloco Plantigrafo apesar de haver marcacoes")
        if regs and _find_widget_by_text(app.content, "Linhas") is None:
            errors.append("Timeline Plantigrafo sem agrupamento por imagem (botoes Linhas/Pontos)")
        momentos = service.marcacoes.listar_momentos_por_cliente(clientes[0].id)
        if momentos:
            cabecalho_dia = _find_widget_by_text(app.content, " momentos") or _find_widget_by_text(
                app.content, " momento"
            )
            if cabecalho_dia is None:
                errors.append("Timeline sem cabecalho de agrupamento por dia")
        if _find_widget_by_text(app.content, "Historico de marcacoes") is not None:
            errors.append("Historico de marcacoes ainda visivel em Pacientes (deveria estar no Hub)")

    session.close()
    app.destroy()

    if errors:
        for e in errors:
            print(f"FALHA: {e}")
        return 1
    print("OK: sidebar, Hub, Plantigrafo M4 (Hub-first + timeline por imagem)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
