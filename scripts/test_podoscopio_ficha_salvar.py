# -*- coding: utf-8 -*-
"""Testa gravacao e listagem de fichas podoscopio no banco."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from easyfeet.db import SessionLocal, init_db
    from easyfeet.services import EasyFeetService

    init_db()
    session = SessionLocal()
    service = EasyFeetService(session)
    clientes = service.clientes.listar()
    if not clientes:
        print("SKIP: sem pacientes")
        session.close()
        return 0

    c = clientes[0]
    ficha = service.salvar_ficha_podoscopio(
        c.id,
        datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Teste auto",
        "Dor nas costas",
        "Normal",
        "Plano",
        "Neutro",
        "Neutro",
        "Simetrica",
        ["Halux"],
        "Pe de garra",
    )
    lista = service.fichas_podoscopio.listar_por_cliente(c.id)
    session.close()

    if not lista or lista[0].id != ficha.id:
        print("FALHOU: ficha nao listada apos salvar")
        return 1
    if lista[0].queixa_objetivo != "Dor nas costas":
        print("FALHOU: dados nao persistidos")
        return 1
    service.excluir_ficha_podoscopio(ficha.id, cliente_id=c.id)
    if service.fichas_podoscopio.obter_por_id(ficha.id) is not None:
        print("FALHOU: ficha nao removida apos excluir")
        return 1
    print(f"OK: ficha #{ficha.id} salva, listada e excluida para cliente #{c.id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
