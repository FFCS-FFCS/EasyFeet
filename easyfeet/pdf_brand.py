"""Marca EasyFeet e tipografia partilhada para exportacao PDF."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, Table, TableStyle

from easyfeet.paths import PROJECT_ROOT

_FONT_REGISTERED = False
LOGO_CANDIDATES = (
    "easyfeet_symbol_256.png",
    "easyfeet_symbol_128.png",
    "easyfeet_symbol.png",
)


def ensure_pdf_font() -> str:
    global _FONT_REGISTERED
    font_name = "Helvetica"
    if _FONT_REGISTERED:
        return "EasyFeetUI" if "EasyFeetUI" in pdfmetrics.getRegisteredFontNames() else font_name
    for path in (
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
    ):
        if path.exists():
            try:
                pdfmetrics.registerFont(TTFont("EasyFeetUI", str(path)))
                _FONT_REGISTERED = True
                return "EasyFeetUI"
            except Exception:
                continue
    _FONT_REGISTERED = True
    return font_name


def resolve_logo() -> Path | None:
    base = PROJECT_ROOT / "Imagens" / "EasyFeet"
    for name in LOGO_CANDIDATES:
        path = base / name
        if path.is_file():
            return path
    return None


def cabecalho_pdf(st: dict, titulo: str) -> list:
    """Titulo com logotipo EasyFeet (quando o ficheiro existir em Imagens/EasyFeet)."""
    title_para = Paragraph(titulo, st["title"])
    logo_path = resolve_logo()
    if logo_path is None:
        return [title_para]

    img = RLImage(str(logo_path), width=2.2 * cm, height=2.2 * cm)
    header = Table([[img, title_para]], colWidths=[2.6 * cm, 14 * cm])
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return [header]


def pdf_page_number_callbacks(font_name: str = "Helvetica") -> tuple[Callable, Callable]:
    """Rodape com numero de pagina (mesma funcao na primeira e nas seguintes)."""
    use_font = font_name if font_name in pdfmetrics.getRegisteredFontNames() else "Helvetica"

    def _draw_page(canvas, doc) -> None:
        canvas.saveState()
        canvas.setFont(use_font, 9)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawCentredString(A4[0] / 2.0, 1.05 * cm, f"Pagina {doc.page}")
        canvas.restoreState()

    return _draw_page, _draw_page
