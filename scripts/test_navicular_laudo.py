# -*- coding: utf-8 -*-
"""
Teste dos laudos Navicular: textos-modelo, BD e PDF.

Uso: py -3 scripts/test_navicular_laudo.py
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
    from easyfeet.navicular_laudo import gerar_textos_laudo
    from easyfeet.navicular_laudo_pdf import export_laudo_navicular_pdf
    from easyfeet.services import EasyFeetService

    out = ROOT / "data" / "test_pdfs"
    out.mkdir(parents=True, exist_ok=True)
    init_db()
    session = SessionLocal()
    service = EasyFeetService(session)
    errors: list[str] = []

    clientes = service.clientes.listar()
    if not clientes:
        errors.append("nenhum paciente na BD para testar laudo")
    else:
        c = clientes[0]
        fichas = service.fichas_navicular.listar_por_cliente(c.id)
        if fichas:
            ficha_alter_d = fichas[0]
        else:
            ficha_alter_d = service.salvar_ficha_navicular(
                c.id,
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Teste laudo D alterado",
                "",
                "52",
                "40",
                "50",
                "42",
                "",
            )

        textos = gerar_textos_laudo(ficha_alter_d)
        if "direita" not in textos["conclusao"].lower() and "alterado" not in textos["conclusao"].lower():
            errors.append("texto conclusao inesperado para D alterado / E normal")
        if str(NAVICULAR_LIMIAR_MM) not in textos["interpretacao"]:
            errors.append("limiar ausente na interpretacao")

        ficha_normal = service.salvar_ficha_navicular(
            c.id,
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Teste laudo normal",
            "",
            "48",
            "40",
            "47",
            "39",
            "",
        )
        textos_n = gerar_textos_laudo(ficha_normal)
        if "sem alteracao" not in textos_n["conclusao"].lower():
            errors.append("conclusao normal inesperada")

        laudo = service.salvar_laudo_navicular(
            c.id,
            ficha_alter_d.id,
            "Dr. Teste",
            textos["interpretacao"],
            textos["conclusao"],
            textos["recomendacoes"],
        )
        if laudo.id <= 0:
            errors.append("laudo nao persistido")

        pdf_path = out / "Laudo_Navicular_TESTE.pdf"
        export_laudo_navicular_pdf(
            pdf_path,
            laudo=laudo,
            ficha=ficha_alter_d,
            paciente_nome=c.nome,
        )
        txt = _pdf_text(pdf_path)
        if "Laudo" not in txt and "Navicular" not in txt:
            errors.append("titulo ausente no PDF laudo")
        if c.nome and c.nome not in txt:
            errors.append("nome do paciente ausente no PDF laudo")
        if "Interpretacao" not in txt and "Interpretação" not in txt:
            errors.append("secao interpretacao ausente no PDF")

        lista = service.laudos_navicular.listar_por_cliente(c.id)
        if not any(l.id == laudo.id for l in lista):
            errors.append("laudo nao listado por cliente")

    session.close()

    if errors:
        print("FALHOU:")
        for e in errors:
            print(" -", e)
        return 1
    print("OK — laudos Navicular (textos + BD + PDF) em", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
