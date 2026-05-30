# -*- coding: utf-8 -*-
"""
Teste dos PDFs do Podoscopio (layout e ficha em branco sem nome de paciente).

Uso: py -3 scripts/test_podoscopio_pdf.py
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
    from easyfeet.paciente_cadastro_pdf import export_ficha_cadastro_paciente_pdf_branco
    from easyfeet.podoscopio_pdf import export_ficha_podoscopio_pdf_branco, export_ficha_podoscopio_pdf_preenchida
    from easyfeet.services import EasyFeetService

    out = ROOT / "data" / "test_pdfs"
    out.mkdir(parents=True, exist_ok=True)
    init_db()
    session = SessionLocal()
    service = EasyFeetService(session)
    errors: list[str] = []

    pod_branco = out / "Ficha_Podoscopio_EM_BRANCO.pdf"
    export_ficha_podoscopio_pdf_branco(pod_branco)
    txt_b = _pdf_text(pod_branco)

    if txt_b.count("Arco plantar") < 2:
        errors.append("faltam linhas de arco plantar (layout por pe)")
    if "( ) Normal" not in txt_b:
        errors.append("falta opcoes de marcacao no PDF em branco")

    clientes = service.clientes.listar()
    if clientes:
        c = clientes[0]
        nome = c.nome
        if nome and nome in txt_b:
            errors.append(f"PDF em branco nao deve conter nome do paciente ({nome!r})")

        cad = out / "Cadastro_Paciente_EM_BRANCO.pdf"
        export_ficha_cadastro_paciente_pdf_branco(cad)
        txt_cad = _pdf_text(cad)
        if nome and nome in txt_cad:
            errors.append(f"cadastro em branco nao deve conter nome ({nome!r})")

        fichas = service.fichas_podoscopio.listar_por_cliente(c.id)
        if fichas:
            ficha = fichas[0]
        else:
            ficha = service.salvar_ficha_podoscopio(
                c.id,
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Teste PDF",
                "Queixa automatizada",
                "Normal",
                "Plano",
                "Neutro",
                "Pronado",
                "Simetrica",
                ["Calcaneo", "Metatarsos"],
                "Observacao de teste",
            )
        pod_p = out / "Ficha_Podoscopio_PREENCHIDA.pdf"
        export_ficha_podoscopio_pdf_preenchida(pod_p, ficha=ficha)
        txt_p = _pdf_text(pod_p)
        if txt_p.count("Arco plantar") < 2:
            errors.append("ficha preenchida sem campos plantares esperados")
        if nome and nome in txt_p:
            errors.append(f"PDF preenchido nao deve conter nome cadastral ({nome!r})")

    session.close()

    if errors:
        print("FALHOU:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("OK: PDFs Podoscopio gerados em data/test_pdfs/")
    print(f"    - {pod_branco.name}")
    if clientes:
        print("    - Cadastro_Paciente_EM_BRANCO.pdf")
        print("    - Ficha_Podoscopio_PREENCHIDA.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
