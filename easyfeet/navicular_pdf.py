"""Exportacao da ficha do Teste Navicular para PDF (branco ou preenchida)."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from easyfeet.models import FichaNavicular
from easyfeet.navicular import NAVICULAR_LIMIAR_MM, rotulo_classificacao
from easyfeet.pdf_brand import (
    cabecalho_pdf,
    col_widths_rotulo_valor,
    ensure_pdf_font,
    pdf_page_number_callbacks,
)

_ROTULOS_TABELA = (
    "Paciente",
    "Data da avaliacao",
    "Rotulo do atendimento",
    "Altura sentado — pe direito",
    "Altura sentado — pe esquerdo",
    "Altura em pe — pe direito",
    "Altura em pe — pe esquerdo",
    "Queda calculada (mm)",
    "Queda calculada",
    f"Modo A — Brody (limiar {NAVICULAR_LIMIAR_MM} mm)",
)


def _larguras_colunas(font_name: str) -> list[float]:
    rotulo_w, valor_w = col_widths_rotulo_valor(font_name, _ROTULOS_TABELA)
    return [rotulo_w, valor_w]


def _styles(font_name: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "EFNavTitle",
            parent=base["Heading1"],
            fontName=font_name,
            fontSize=16,
            textColor=colors.HexColor("#7c1229"),
            spaceAfter=6,
        ),
        "section": ParagraphStyle(
            "EFNavSection",
            parent=base["Heading2"],
            fontName=font_name,
            fontSize=12,
            textColor=colors.HexColor("#7c1229"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "EFNavBody",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=10,
            leading=14,
        ),
        "small": ParagraphStyle(
            "EFNavSmall",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=8,
            textColor=colors.HexColor("#888888"),
        ),
    }


def _table_base(font_name: str, *, valign: str = "MIDDLE", compact: bool = False) -> TableStyle:
    pad = 3 if compact else 6
    hpad = 4 if compact else 8
    style = [
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
        ("VALIGN", (0, 0), (-1, -1), valign),
        ("LEFTPADDING", (0, 0), (-1, -1), hpad),
        ("RIGHTPADDING", (0, 0), (-1, -1), hpad),
        ("TOPPADDING", (0, 0), (-1, -1), pad),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f5f5f5")),
    ]
    if compact:
        style.extend(
            [
                ("RIGHTPADDING", (0, 0), (0, -1), 2),
                ("LEFTPADDING", (1, 0), (1, -1), 2),
            ]
        )
    return TableStyle(style)


def _linha_em_branco(linhas: int = 4) -> Paragraph:
    return Paragraph("<br/>".join(["&nbsp;"] * max(1, linhas)), ParagraphStyle("Blank", fontSize=10, leading=14))


def _campo_data_hora_em_branco(font_name: str) -> Paragraph:
    return Paragraph(
        '<font color="#aaaaaa">DD / MM / AAAA   HH : MM</font>',
        ParagraphStyle("EFNavDataHora", fontName=font_name, fontSize=10, leading=12),
    )


def _celula_rotulo(font_name: str, texto: str, *, compact: bool = False) -> Paragraph:
    html = texto.replace(" — ", "<br/>")
    return Paragraph(
        html,
        ParagraphStyle(
            "EFNavRotulo",
            fontName=font_name,
            fontSize=9,
            leading=10 if compact else 11,
        ),
    )


def _celula_valor_vazio(font_name: str) -> Paragraph:
    return Paragraph(
        "&nbsp;",
        ParagraphStyle("EFNavValorVazio", fontName=font_name, fontSize=10, leading=12),
    )


def _celula_valor(font_name: str, texto: str) -> Paragraph:
    return Paragraph(
        (texto or "—").replace("\n", "<br/>"),
        ParagraphStyle("EFNavValor", fontName=font_name, fontSize=10, leading=13),
    )


def _celula_classificacao(font_name: str, classificacao: str) -> Paragraph:
    if not classificacao:
        return _celula_valor(font_name, "—")
    class_txt = rotulo_classificacao(classificacao)
    if classificacao == "alterado":
        html = f'<font color="#b00020"><b>{class_txt}</b></font>'
        return Paragraph(
            html,
            ParagraphStyle(
                "EFNavClassAlterado",
                fontName=font_name,
                fontSize=10,
                leading=13,
                backColor=colors.HexColor("#fde8e8"),
            ),
        )
    return _celula_valor(font_name, class_txt)


def _fmt_mm(valor: float | None) -> str:
    if valor is None:
        return "—"
    if valor == int(valor):
        return f"{int(valor)} mm"
    return f"{valor} mm"


def _build_doc(destino: Path, titulo_doc: str) -> tuple[SimpleDocTemplate, dict[str, ParagraphStyle], str]:
    font_name = ensure_pdf_font()
    st = _styles(font_name)
    doc = SimpleDocTemplate(
        str(destino),
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=2.3 * cm,
        title=titulo_doc,
    )
    return doc, st, font_name


def _secao(st: dict[str, ParagraphStyle], titulo: str) -> Paragraph:
    return Paragraph(titulo, st["section"])


def _bloco_secao(st: dict[str, ParagraphStyle], titulo: str, conteudo: list) -> KeepTogether:
    return KeepTogether([_secao(st, titulo), *conteudo])


def _build_with_page_numbers(doc: SimpleDocTemplate, story: list, font_name: str) -> None:
    on_page, on_later = pdf_page_number_callbacks(font_name)
    doc.build(story, onFirstPage=on_page, onLaterPages=on_later)


def _bloco_paciente(
    font_name: str,
    paciente_nome: str | None,
    *,
    em_branco: bool,
    col_widths: list[float],
) -> list:
    valor = _celula_valor_vazio(font_name) if em_branco else _celula_valor(font_name, paciente_nome or "—")
    row = [[_celula_rotulo(font_name, "Paciente", compact=em_branco), valor]]
    t = Table(row, colWidths=col_widths)
    t.setStyle(_table_base(font_name, valign="TOP", compact=em_branco))
    return [t]


def _bloco_identificacao_branco(font_name: str, col_widths: list[float]) -> list:
    id_rows = [
        [_celula_rotulo(font_name, "Data da avaliacao", compact=True), _campo_data_hora_em_branco(font_name)],
        [_celula_rotulo(font_name, "Rotulo do atendimento", compact=True), _celula_valor_vazio(font_name)],
    ]
    t_id = Table(id_rows, colWidths=col_widths)
    t_id.setStyle(_table_base(font_name, valign="TOP", compact=True))
    return [t_id]


def _bloco_identificacao_preenchida(
    font_name: str,
    ficha: FichaNavicular,
    col_widths: list[float],
) -> list:
    id_rows = [
        [
            _celula_rotulo(font_name, "Data da avaliacao"),
            _celula_valor(font_name, ficha.data_avaliacao.strftime("%d/%m/%Y %H:%M")),
        ],
        [
            _celula_rotulo(font_name, "Rotulo do atendimento"),
            _celula_valor(font_name, ficha.rotulo_atendimento or ""),
        ],
    ]
    t_id = Table(id_rows, colWidths=col_widths)
    t_id.setStyle(_table_base(font_name, valign="TOP"))
    return [t_id]


def _bloco_medicao_branco(font_name: str, lado: str, col_widths: list[float]) -> Table:
    rows = [
        [_celula_rotulo(font_name, f"Altura sentado — {lado}", compact=True), _celula_valor_vazio(font_name)],
        [_celula_rotulo(font_name, f"Altura em pe — {lado}", compact=True), _celula_valor_vazio(font_name)],
        [_celula_rotulo(font_name, "Queda calculada (mm)", compact=True), _celula_valor_vazio(font_name)],
        [
            _celula_rotulo(font_name, f"Modo A — Brody (limiar {NAVICULAR_LIMIAR_MM} mm)", compact=True),
            _celula_valor_vazio(font_name),
        ],
    ]
    t = Table(rows, colWidths=col_widths)
    t.setStyle(_table_base(font_name, valign="TOP", compact=True))
    return t


def _bloco_medicao_preenchida(
    font_name: str,
    lado: str,
    col_widths: list[float],
    *,
    sentado: float | None,
    pe: float | None,
    queda: float | None,
    classificacao: str,
) -> Table:
    queda_txt = f"{queda} mm" if queda is not None else "—"
    if classificacao == "alterado" and queda is not None:
        queda_cell = Paragraph(
            f'<font color="#b00020"><b>{queda_txt}</b></font>',
            ParagraphStyle("EFNavQuedaAlterado", fontName=font_name, fontSize=10, leading=13),
        )
    else:
        queda_cell = _celula_valor(font_name, queda_txt)

    rows = [
        [_celula_rotulo(font_name, f"Altura sentado — {lado}"), _celula_valor(font_name, _fmt_mm(sentado))],
        [_celula_rotulo(font_name, f"Altura em pe — {lado}"), _celula_valor(font_name, _fmt_mm(pe))],
        [_celula_rotulo(font_name, "Queda calculada"), queda_cell],
        [
            _celula_rotulo(font_name, f"Modo A — Brody (limiar {NAVICULAR_LIMIAR_MM} mm)"),
            _celula_classificacao(font_name, classificacao),
        ],
    ]
    t = Table(rows, colWidths=col_widths)
    style = _table_base(font_name, valign="TOP")
    if classificacao == "alterado":
        style.add("BACKGROUND", (1, 3), (1, 3), colors.HexColor("#fde8e8"))
    t.setStyle(style)
    return t


def _fotos_validas(fotos: Sequence[Path] | None) -> list[Path]:
    if not fotos:
        return []
    return [p for p in fotos if p.is_file()]


def _bloco_fotos(fotos: list[Path]) -> list:
    bloco: list = []
    largura = 14 * cm
    for path in fotos:
        try:
            img = RLImage(str(path))
            ratio = img.imageHeight / img.imageWidth if img.imageWidth else 1
            img.drawWidth = largura
            img.drawHeight = largura * ratio
            bloco.append(img)
            bloco.append(Spacer(1, 0.15 * cm))
        except Exception:
            continue
    return bloco


def export_ficha_navicular_pdf_branco(destino: Path) -> None:
    """PDF para impressao e preenchimento manual."""
    doc, st, font_name = _build_doc(destino, "Ficha Navicular — em branco")
    col_widths = _larguras_colunas(font_name)
    story: list = []

    story.extend(cabecalho_pdf(st, "EasyFeet — Teste Navicular"))
    story.append(
        _bloco_secao(st, "Paciente", _bloco_paciente(font_name, None, em_branco=True, col_widths=col_widths))
    )
    story.append(Spacer(1, 0.15 * cm))
    story.append(
        _bloco_secao(st, "Identificacao da avaliacao", _bloco_identificacao_branco(font_name, col_widths))
    )
    story.append(Spacer(1, 0.15 * cm))
    story.append(_bloco_secao(st, "Queixa / objetivo", [_linha_em_branco(4)]))
    story.append(
        _bloco_secao(
            st,
            "Medicao — pe direito",
            [_bloco_medicao_branco(font_name, "pe direito", col_widths)],
        )
    )
    story.append(
        _bloco_secao(
            st,
            "Medicao — pe esquerdo",
            [_bloco_medicao_branco(font_name, "pe esquerdo", col_widths)],
        )
    )
    story.append(_bloco_secao(st, "Observacoes clinicas", [_linha_em_branco(5)]))

    story.append(Spacer(1, 0.2 * cm))
    story.append(
        KeepTogether(
            [
                Paragraph(
                    "Documento apenas com dados textuais da avaliacao navicular (sem imagens). "
                    "Registro complementar; nao substitui exame clinico completo.",
                    st["small"],
                )
            ]
        )
    )
    _build_with_page_numbers(doc, story, font_name)


def export_ficha_navicular_pdf_preenchida(
    destino: Path,
    *,
    ficha: FichaNavicular,
    paciente_nome: str | None = None,
    fotos: Sequence[Path] | None = None,
) -> None:
    """PDF com os dados gravados na ficha."""
    doc, st, font_name = _build_doc(destino, "Ficha Navicular — preenchida")
    col_widths = _larguras_colunas(font_name)
    story: list = []

    story.extend(cabecalho_pdf(st, "EasyFeet — Teste Navicular"))
    story.append(
        _bloco_secao(
            st,
            "Paciente",
            _bloco_paciente(font_name, paciente_nome, em_branco=False, col_widths=col_widths),
        )
    )
    story.append(Spacer(1, 0.2 * cm))
    story.append(
        _bloco_secao(
            st,
            "Identificacao da avaliacao",
            _bloco_identificacao_preenchida(font_name, ficha, col_widths),
        )
    )
    story.append(Spacer(1, 0.2 * cm))
    story.append(
        _bloco_secao(
            st,
            "Queixa / objetivo",
            [Paragraph((ficha.queixa_objetivo or "—").replace("\n", "<br/>"), st["body"])],
        )
    )
    story.append(
        _bloco_secao(
            st,
            "Medicao — pe direito",
            [
                _bloco_medicao_preenchida(
                    font_name,
                    "pe direito",
                    col_widths,
                    sentado=ficha.altura_sentado_d_mm,
                    pe=ficha.altura_pe_d_mm,
                    queda=ficha.queda_d_mm,
                    classificacao=ficha.classificacao_d or "",
                )
            ],
        )
    )
    story.append(
        _bloco_secao(
            st,
            "Medicao — pe esquerdo",
            [
                _bloco_medicao_preenchida(
                    font_name,
                    "pe esquerdo",
                    col_widths,
                    sentado=ficha.altura_sentado_e_mm,
                    pe=ficha.altura_pe_e_mm,
                    queda=ficha.queda_e_mm,
                    classificacao=ficha.classificacao_e or "",
                )
            ],
        )
    )
    story.append(
        _bloco_secao(
            st,
            "Observacoes clinicas",
            [Paragraph((ficha.observacoes or "—").replace("\n", "<br/>"), st["body"])],
        )
    )

    fotos_ok = _fotos_validas(fotos)
    if fotos_ok:
        story.append(_bloco_secao(st, "Registro fotografico", _bloco_fotos(fotos_ok)))

    story.append(Spacer(1, 0.3 * cm))
    story.append(
        KeepTogether(
            [
                Paragraph(
                    f"EasyFeet — gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}.",
                    st["small"],
                )
            ]
        )
    )
    _build_with_page_numbers(doc, story, font_name)
