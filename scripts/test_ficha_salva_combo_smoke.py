# -*- coding: utf-8 -*-
"""Smoke: combo «Ficha salva» deve recarregar o formulario (Navicular + Podoscopio)."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _iter_widgets(parent):
    for child in parent.winfo_children():
        yield child
        yield from _iter_widgets(child)


def _find_comboboxes(parent):
    import customtkinter as ctk

    return [w for w in _iter_widgets(parent) if isinstance(w, ctk.CTkComboBox)]


def _find_ctk_entries(parent):
    import customtkinter as ctk

    return [w for w in _iter_widgets(parent) if isinstance(w, ctk.CTkEntry)]


def _combo_select(combo, value: str) -> None:
    """Simula escolha no dropdown (dispara command como o CTkComboBox)."""
    combo._dropdown_callback(value)


def _ctx_ficha_id(app, ctx_attr: str) -> int | None:
    return getattr(app, ctx_attr).get("ficha_id")


def _test_modulo_ficha(
    app,
    service,
    *,
    module_id: str,
    ctx_attr: str,
    salvar_a,
    salvar_b,
    rotulo_esperado,
) -> list[str]:
    errors: list[str] = []
    clientes = service.clientes.listar()
    if not clientes:
        return ["sem pacientes no banco"]

    c = clientes[0]
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    fa = salvar_a(c.id, now)
    fb = salvar_b(c.id, now)
    if fa.id == fb.id:
        errors.append(f"{module_id}: duas fichas de teste colidiram no mesmo id")
        return errors

    app._show_module(module_id)
    app.update_idletasks()
    app.update()

    combos = _find_comboboxes(app.content)
    if len(combos) < 2:
        errors.append(f"{module_id}: esperava 2 combos (paciente + ficha), achou {len(combos)}")
        return errors

    paciente_combo, ficha_combo = combos[0], combos[1]
    pl = f"#{c.id} — {c.nome}"
    _combo_select(paciente_combo, pl)
    app.update_idletasks()
    app.update()

    values = list(ficha_combo.cget("values"))
    labels = [v for v in values if v != "— Nova ficha —"]
    if len(labels) < 2:
        errors.append(f"{module_id}: paciente precisa de >=2 fichas salvas para o teste")
        return errors

    label_a = next(l for l in labels if l.startswith(f"#{fa.id} —"))
    label_b = next(l for l in labels if l.startswith(f"#{fb.id} —"))

    _combo_select(ficha_combo, label_a)
    app.update_idletasks()
    app.update()
    if _ctx_ficha_id(app, ctx_attr) != fa.id:
        errors.append(
            f"{module_id}: apos selecionar ficha A, ctx={_ctx_ficha_id(app, ctx_attr)} esperado={fa.id}"
        )
    entries = _find_ctk_entries(app.content)
    if len(entries) < 2:
        errors.append(f"{module_id}: nao encontrou campos CTkEntry do formulario")
    else:
        rotulo_tela = entries[1].get().strip()
        esperado_a = rotulo_esperado(fa)
        if rotulo_tela != esperado_a:
            errors.append(
                f"{module_id}: rotulo na tela apos ficha A = {rotulo_tela!r}, esperado {esperado_a!r}"
            )

    _combo_select(ficha_combo, label_b)
    app.update_idletasks()
    app.update()
    if _ctx_ficha_id(app, ctx_attr) != fb.id:
        errors.append(
            f"{module_id}: apos trocar para ficha B, ctx={_ctx_ficha_id(app, ctx_attr)} esperado={fb.id}"
        )
    rotulo_tela_b = entries[1].get().strip()
    esperado_b = rotulo_esperado(fb)
    if rotulo_tela_b != esperado_b:
        errors.append(
            f"{module_id}: rotulo na tela apos ficha B = {rotulo_tela_b!r}, esperado {esperado_b!r}"
        )

    return errors


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

    errors.extend(
        _test_modulo_ficha(
            app,
            service,
            module_id="navicular_ficha_tecnica",
            ctx_attr="_navicular_ctx",
            salvar_a=lambda cid, dt: service.salvar_ficha_navicular(
                cid, dt, "Combo smoke A", "Q A", "50", "40", "48", "38", "obs A"
            ),
            salvar_b=lambda cid, dt: service.salvar_ficha_navicular(
                cid, dt, "Combo smoke B", "Q B", "55", "42", "52", "40", "obs B"
            ),
            rotulo_esperado=lambda f: (f.rotulo_atendimento or "").strip(),
        )
    )

    errors.extend(
        _test_modulo_ficha(
            app,
            service,
            module_id="podoscopio_ficha_tecnica",
            ctx_attr="_podoscopio_ctx",
            salvar_a=lambda cid, dt: service.salvar_ficha_podoscopio(
                cid, dt, "Combo smoke A", "Queixa A", "Normal", "Plano", "Neutro", "Neutro", "Simetrica", [], "Obs A"
            ),
            salvar_b=lambda cid, dt: service.salvar_ficha_podoscopio(
                cid, dt, "Combo smoke B", "Queixa B", "Cavo", "Cavo", "Supinado", "Supinado", "Maior a direita", ["Halux"], "Obs B"
            ),
            rotulo_esperado=lambda f: (f.rotulo_atendimento or "").strip(),
        )
    )

    session.close()
    app.destroy()

    if errors:
        for e in errors:
            print(f"FALHA: {e}")
        return 1
    print("OK: combo Ficha salva recarrega Navicular e Podoscopio (ctx + rotulo na tela)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
