# -*- coding: utf-8 -*-
"""Testa gravacao, calculo e listagem de fichas navicular no banco."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from easyfeet.db import SessionLocal, init_db
    from easyfeet.navicular import NAVICULAR_LIMIAR_MM
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
    ficha = service.salvar_ficha_navicular(
        c.id,
        datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Teste auto navicular",
        "Desconforto medial",
        "52",
        "42",
        "50",
        "38",
        "Obs teste",
    )
    lista = service.fichas_navicular.listar_por_cliente(c.id)
    session.close()

    if not lista or lista[0].id != ficha.id:
        print("FALHOU: ficha nao listada apos salvar")
        return 1
    if ficha.queda_d_mm != 10.0 or ficha.classificacao_d != "normal":
        print(f"FALHOU: pe D esperado queda=10 normal, obteve {ficha.queda_d_mm} {ficha.classificacao_d}")
        return 1
    if ficha.queda_e_mm != 12.0 or ficha.classificacao_e != "alterado":
        print(f"FALHOU: pe E esperado queda=12 alterado, obteve {ficha.queda_e_mm} {ficha.classificacao_e}")
        return 1
    if NAVICULAR_LIMIAR_MM != 10:
        print("FALHOU: limiar Modo A deve ser 10 mm")
        return 1
    service.excluir_ficha_navicular(ficha.id, cliente_id=c.id)
    if service.fichas_navicular.obter_por_id(ficha.id) is not None:
        print("FALHOU: ficha nao removida apos excluir")
        return 1
    print(
        f"OK: ficha #{ficha.id} salva — D queda={ficha.queda_d_mm:g}mm ({ficha.classificacao_d}), "
        f"E queda={ficha.queda_e_mm:g}mm ({ficha.classificacao_e})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
