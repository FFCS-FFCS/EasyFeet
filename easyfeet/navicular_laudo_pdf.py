"""Exportacao do laudo clinico do Teste Navicular para PDF."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from easyfeet.models import FichaNavicular, LaudoNavicular
from easyfeet.navicular import NAVICULAR_LIMIAR_MM, rotulo_classificacao
from easyfeet.navicular_laudo import RODAPE_LAUDO_NAVICULAR
from easyfeet.pdf_brand import (
    cabecalho_pdf,
    ensure_pdf_font,
    largura_util_tabela_pdf,
    pdf_page_number_callbacks,
)


def _fmt_mm(valor: float | None) -> str:
    if valor is None:
        return "—"
    if valor == int(valor):
        return str(int(valor))
    return str(valor)


def _styles(font_name: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "EFNavLaudoTitle",
            parent=base["Heading1"],
            fontName=font_name,
            fontSize=16,
            textColor=colors.HexColor("#7c1229"),
            spaceAfter=6,
        ),
        "section": ParagraphStyle(
            "EFNavLaudoSection",
            parent=base["Heading2"],
            fontName=font_name,
            fontSize=12,
            textColor=colors.HexColor("#7c1229"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "EFNavLaudoBody",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=10,
            leading=14,
        ),
        "small": ParagraphStyle(
            "EFNavLaudoSmall",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=8,
            textColor=colors.HexColor("#888888"),
            leading=11,
        ),
    }


def _build_doc(destino: Path, titulo_doc: str):
    font_name = ensure_pdf_font()
    st = _styles(font_name)
    doc = SimpleDocTemplate(
        str(destino),
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.8 * cm,
        title=titulo_doc,
    )
    return doc, st, font_name


def _secao(titulo: str, conteudo: list, st: dict) -> list:
    return [Paragraph(titulo, st["section"]), *conteudo, Spacer(1, 0.15 * cm)]


def _tabela_resultados(font_name: str, ficha: FichaNavicular) -> Table:
    largura = largura_util_tabela_pdf()
    col_widths = [3.2 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, largura - 10.7 * cm]

    def _class_cell(classificacao: str) -> Paragraph:
        txt = rotulo_classificacao(classificacao)
        if classificacao == "alterado":
            return Paragraph(
                f'<font color="#b00020"><b>{txt}</b></font>',
                ParagraphStyle("EFNavLaudoClass", fontName=font_name, fontSize=9, leading=12),
            )
        return Paragraph(txt, ParagraphStyle("EFNavLaudoClassN", fontName=font_name, fontSize=9, leading=12))

    rows = [
        [
            Paragraph("<b>Pé</b>", ParagraphStyle("Hdr", fontName=font_name, fontSize=9)),
            Paragraph("<b>Sentado (mm)</b>", ParagraphStyle("Hdr", fontName=font_name, fontSize=9)),
            Paragraph("<b>Em pé (mm)</b>", ParagraphStyle("Hdr", fontName=font_name, fontSize=9)),
            Paragraph("<b>Queda (mm)</b>", ParagraphStyle("Hdr", fontName=font_name, fontSize=9)),
            Paragraph("<b>Classificação (Modo A)</b>", ParagraphStyle("Hdr", fontName=font_name, fontSize=9)),
        ],
        ["Direito", _fmt_mm(ficha.altura_sentado_d_mm), _fmt_mm(ficha.altura_pe_d_mm), _fmt_mm(ficha.queda_d_mm), _class_cell(ficha.classificacao_d)],
        ["Esquerdo", _fmt_mm(ficha.altura_sentado_e_mm), _fmt_mm(ficha.altura_pe_e_mm), _fmt_mm(ficha.queda_e_mm), _class_cell(ficha.classificacao_e)],
    ]
    t = Table(rows, colWidths=col_widths)
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f5f5f5")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def export_laudo_navicular_pdf(
    destino: Path,
    *,
    laudo: LaudoNavicular,
    ficha: FichaNavicular,
    paciente_nome: str,
) -> None:
    doc, st, font_name = _build_doc(destino, "Laudo Navicular")
    on_first, on_later = pdf_page_number_callbacks(font_name)
    story: list = []

    story.extend(cabecalho_pdf(st, "Laudo — Teste da Queda do Navicular"))
    story.append(Spacer(1, 0.2 * cm))

    ident_rows = [
        ["Paciente", paciente_nome or "—"],
        ["Data da avaliacao", ficha.data_avaliacao.strftime("%d/%m/%Y %H:%M")],
        ["Rotulo do atendimento", ficha.rotulo_atendimento or "—"],
        ["Ficha n.", f"#{ficha.id}"],
        ["Profissional", laudo.profissional_nome or "—"],
        ["Laudo n.", f"#{laudo.id}"],
    ]
    largura = largura_util_tabela_pdf()
    t_id = Table(ident_rows, colWidths=[4.5 * cm, largura - 4.5 * cm])
    t_id.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f5f5f5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.extend(_secao("Identificacao", [t_id], st))

    procedimento = (
        "Procedimento: medicao da altura do navicular em relacao ao solo em duas condicoes — "
        "sentado (subtalar neutro) e em pe (relaxado com carga). A queda (mm) corresponde a "
        "diferenca entre as duas medidas por pe."
    )
    criterio = (
        f"Critério Modo A (Brody): queda ≤ {NAVICULAR_LIMIAR_MM} mm = dentro do esperado; "
        f"> {NAVICULAR_LIMIAR_MM} mm = acima do limiar (alterado)."
    )
    story.extend(
        _secao(
            "Procedimento e criterio",
            [Paragraph(procedimento, st["body"]), Spacer(1, 0.1 * cm), Paragraph(criterio, st["body"])],
            st,
        )
    )
    story.extend(_secao("Resultados", [_tabela_resultados(font_name, ficha)], st))

    def _paragrafo(texto: str) -> Paragraph:
        return Paragraph((texto or "—").replace("\n", "<br/>"), st["body"])

    story.extend(_secao("Interpretacao", [_paragrafo(laudo.interpretacao)], st))
    story.extend(_secao("Conclusao", [_paragrafo(laudo.conclusao)], st))
    story.extend(_secao("Recomendacoes", [_paragrafo(laudo.recomendacoes)], st))

    story.append(Spacer(1, 0.3 * cm))
    story.append(
        KeepTogether(
            [
                Paragraph(f"<i>{RODAPE_LAUDO_NAVICULAR}</i>", st["small"]),
            ]
        )
    )

    doc.build(story, onFirstPage=on_first, onLaterPages=on_later)
