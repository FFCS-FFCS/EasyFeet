"""Gera PDF visual com tabela de limiares — Teste da Queda do Navicular."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from easyfeet.pdf_brand import cabecalho_pdf, ensure_pdf_font, pdf_page_number_callbacks

OUT = ROOT / "Documentos de Apoio" / "EF - Navicular mm x percentual - limiares.pdf"

BORDO = colors.HexColor("#7c1229")
FUNDO_HEADER = colors.HexColor("#7c1229")
FUNDO_ZEBRA = colors.HexColor("#f7eef1")
FUNDO_LOCAL = colors.HexColor("#fff8e8")
TEXTO_HEADER = colors.white
TEXTO_CORPO = colors.HexColor("#333333")

ROWS = [
    ("Brody (1982)", "> 10 mm (1 cm)", "Pronação excessiva", False),
    ("Mueller et al. (1993)", "≥ 10 mm", "Limite superior «normal»", False),
    ("Physiopedia / várias fontes", "< 5 mm", "Supinado / rígido", False),
    ("Physiopedia / várias fontes", "5–9 mm", "Neutro", False),
    ("Physiopedia / várias fontes", "≥ 10 mm", "Pronado", False),
    ("Clínicas / resumos", "6–10 mm", "Faixa «normal»", False),
    (
        "Regra local EasyFeet (consultório)",
        "até 10 mm",
        "Variante permissiva — Modo A na app",
        True,
    ),
]


def _styles(font: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "NavTitle",
            parent=base["Heading1"],
            fontName=font,
            fontSize=17,
            textColor=BORDO,
            spaceAfter=8,
        ),
        "sub": ParagraphStyle(
            "NavSub",
            parent=base["Normal"],
            fontName=font,
            fontSize=10,
            textColor=colors.HexColor("#555555"),
            spaceAfter=14,
        ),
        "body": ParagraphStyle(
            "NavBody",
            parent=base["Normal"],
            fontName=font,
            fontSize=10,
            textColor=TEXTO_CORPO,
            leading=14,
        ),
        "cell": ParagraphStyle(
            "NavCell",
            parent=base["Normal"],
            fontName=font,
            fontSize=9.5,
            textColor=TEXTO_CORPO,
            leading=13,
        ),
        "cell_bold": ParagraphStyle(
            "NavCellBold",
            parent=base["Normal"],
            fontName=font,
            fontSize=9.5,
            textColor=BORDO,
            leading=13,
        ),
        "foot": ParagraphStyle(
            "NavFoot",
            parent=base["Normal"],
            fontName=font,
            fontSize=9,
            textColor=colors.HexColor("#666666"),
            leading=13,
            spaceBefore=12,
        ),
    }


def main() -> None:
    font = ensure_pdf_font()
    st = _styles(font)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.8 * cm,
        title="EF — Navicular — Limiares clínicos",
    )

    story: list = []
    story.extend(cabecalho_pdf(st, "Teste da Queda do Navicular"))
    story.append(Paragraph("Como o «normal vs. alterado» é definido hoje", st["title"]))
    story.append(
        Paragraph(
            "Na prática clínica e na fisioterapia predomina <b>limiar fixo em milímetros</b> "
            "(queda = diferença entre altura sentado/neutro e em pé/relaxado).",
            st["sub"],
        )
    )

    header = [
        Paragraph("<b>Fonte / uso</b>", st["cell_bold"]),
        Paragraph("<b>Limiar (queda)</b>", st["cell_bold"]),
        Paragraph("<b>Interpretação</b>", st["cell_bold"]),
    ]
    data = [header]
    for fonte, limiar, interp, destaque in ROWS:
        data.append(
            [
                Paragraph(fonte, st["cell_bold"] if destaque else st["cell"]),
                Paragraph(f"<b>{limiar}</b>" if destaque else limiar, st["cell"]),
                Paragraph(interp.replace("**", ""), st["cell"]),
            ]
        )

    col_w = [5.8 * cm, 4.2 * cm, 6.5 * cm]
    table = Table(data, colWidths=col_w, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), FUNDO_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), TEXTO_HEADER),
        ("FONTNAME", (0, 0), (-1, 0), font),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FUNDO_ZEBRA]),
    ]
    for i, (_, _, _, destaque) in enumerate(ROWS, start=1):
        if destaque:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), FUNDO_LOCAL))
            style_cmds.append(("BOX", (0, i), (-1, i), 1.2, BORDO))
    table.setStyle(TableStyle(style_cmds))
    story.append(table)

    story.append(Spacer(1, 0.4 * cm))
    story.append(
        Paragraph(
            "<b>Modo A (EasyFeet):</b> queda <b>até 10 mm</b> = normal (Brody); acima = alterado. "
            "Modos B (percentual) e C (ajuste por comprimento do pé) ficam registados para evolução futura.",
            st["foot"],
        )
    )
    story.append(
        Paragraph(
            "Documento de apoio EasyFeet · 2026-06-01 · Ver também "
            "<i>EF - Navicular mm x percentual.md</i>",
            st["foot"],
        )
    )

    on_first, on_later = pdf_page_number_callbacks(font)
    doc.build(story, onFirstPage=on_first, onLaterPages=on_later)
    print(f"PDF gerado: {OUT}")


if __name__ == "__main__":
    main()
