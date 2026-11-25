# -*- coding: utf-8 -*-
"""
Teste dos PDFs do Teste Navicular (layout e ficha em branco sem nome de paciente).

Uso: py -3 scripts/test_navicular_pdf.py
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return path.read_bytes().decode("latin-1", errors="ignore")
    return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)


def main() -> int:
    from easyfeet.db import SessionLocal, init_db
    from easyfeet.navicular import NAVICULAR_LIMIAR_MM
    from easyfeet.navicular_pdf import export_ficha_navicular_pdf_branco, export_ficha_navicular_pdf_preenchida
    from easyfeet.services import EasyFeetService

    out = ROOT / "data" / "test_pdfs"
    out.mkdir(parents=True, exist_ok=True)
    init_db()
    session = SessionLocal()
    service = EasyFeetService(session)
    errors: list[str] = []

    nav_branco = out / "Ficha_Navicular_EM_BRANCO.pdf"
    export_ficha_navicular_pdf_branco(nav_branco)
    txt_b = _pdf_text(nav_branco)

    if "Teste Navicular" not in txt_b:
        errors.append("titulo Teste Navicular ausente no PDF em branco")
    if "pe direito" not in txt_b.lower() and "pe direito" not in txt_b:
        errors.append("falta secao pe direito")
    if str(NAVICULAR_LIMIAR_MM) not in txt_b:
        errors.append(f"limiar {NAVICULAR_LIMIAR_MM} mm ausente")
    if "Registro fotografico" in txt_b:
        errors.append("PDF em branco nao deve ter secao Registro fotografico")
    if "caneta" in txt_b.lower():
        errors.append("PDF em branco nao deve mencionar caneta")
    if "Dados cadastrais do paciente" in txt_b:
        errors.append("PDF em branco nao deve ter nota de cadastro no cabecalho")

    clientes = service.clientes.listar()
    if clientes:
        c = clientes[0]
        nome = c.nome
        if nome and nome in txt_b:
            errors.append(f"PDF em branco nao deve conter nome do paciente ({nome!r})")

        fichas = service.fichas_navicular.listar_por_cliente(c.id)
        if fichas:
            ficha = fichas[0]
        else:
            ficha = service.salvar_ficha_navicular(
                c.id,
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Teste PDF",
                "Queixa automatizada",
                "45",
                "35",
                "44",
                "33",
                "Observacao de teste",
            )
        nav_p = out / "Ficha_Navicular_PREENCHIDA.pdf"
        export_ficha_navicular_pdf_preenchida(nav_p, ficha=ficha, paciente_nome=c.nome)
        txt_p = _pdf_text(nav_p)
        if nome and nome not in txt_p:
            errors.append(f"PDF preenchido deve conter nome do paciente ({nome!r})")
        if "10" not in txt_p:
            errors.append("classificacao/limiar esperada no PDF preenchido")

    session.close()

    if errors:
        print("FALHOU:")
        for e in errors:
            print(" -", e)
        return 1
    print("OK — PDFs Navicular gerados em", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
