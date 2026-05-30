"""Exportacao da ficha de cadastro de paciente para PDF (branco ou preenchida)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from easyfeet.cliente_dados_corporais import (
    LATERALIDADE_OPCOES,
    calcular_imc,
    formatar_altura,
    formatar_imc,
    formatar_peso,
)
from easyfeet.models import Cliente
from easyfeet.pdf_brand import cabecalho_pdf, ensure_pdf_font

SEXO_OPCOES = ("Masculino", "Feminino")


def _styles(font_name: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "EFCadTitle",
            parent=base["Heading1"],
            fontName=font_name,
            fontSize=16,
            textColor=colors.HexColor("#7c1229"),
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "EFCadSubtitle",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=10,
            textColor=colors.HexColor("#666666"),
            spaceAfter=12,
        ),
        "section": ParagraphStyle(
            "EFCadSection",
            parent=base["Heading2"],
            fontName=font_name,
            fontSize=12,
            textColor=colors.HexColor("#7c1229"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "EFCadBody",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=10,
            leading=14,
        ),
        "small": ParagraphStyle(
            "EFCadSmall",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=8,
            textColor=colors.HexColor("#888888"),
        ),
    }


def _table_base(font_name: str) -> TableStyle:
    return TableStyle(
        [
            ("FONTNAME", (0, 0), (-1, -1), font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f5f5f5")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
    )


def _linha_em_branco(linhas: int = 4) -> Paragraph:
    return Paragraph("<br/>".join(["&nbsp;"] * max(1, linhas)), ParagraphStyle("Blank", fontSize=10, leading=16))


def _marcar_opcoes(opcoes: tuple[str, ...], valor: str | None) -> str:
    v = (valor or "").strip()
    return "    ".join(f"({'X' if o == v else ' '}) {o}" for o in opcoes)


def _campo_data_em_branco(font_name: str) -> Paragraph:
    return Paragraph(
        '<font color="#aaaaaa">DD / MM / AAAA</font>',
        ParagraphStyle("EFCadDataMask", fontName=font_name, fontSize=10, leading=14),
    )


def _build_doc(destino: Path, titulo: str) -> tuple[SimpleDocTemplate, dict[str, ParagraphStyle], str]:
    font_name = ensure_pdf_font()
    st = _styles(font_name)
    doc = SimpleDocTemplate(
        str(destino),
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title=titulo,
    )
    return doc, st, font_name


def export_ficha_cadastro_paciente_pdf_branco(destino: Path) -> None:
    """PDF para preenchimento manual (caneta) com todos os campos do cadastro."""
    doc, st, font_name = _build_doc(destino, "Cadastro paciente — em branco")
    story: list = []

    story.extend(cabecalho_pdf(st, "EasyFeet — Ficha de cadastro de paciente"))
    story.append(
        Paragraph(
            "Versao para preenchimento manual (caneta). Depois, digite os dados no sistema em Pacientes.",
            st["subtitle"],
        )
    )

    t0 = Table([["Nome *", ""]], colWidths=[4.5 * cm, 12 * cm])
    t0.setStyle(_table_base(font_name))
    story.append(t0)
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph("Dados de contato e identificacao", st["section"]))
    contato = [
        ["Telefone", ""],
        ["Email", ""],
        ["Nascimento *", _campo_data_em_branco(font_name)],
        ["Sexo *", _marcar_opcoes(SEXO_OPCOES, None)],
        ["Lateralidade *", _marcar_opcoes(LATERALIDADE_OPCOES, None)],
    ]
    t1 = Table(contato, colWidths=[4.5 * cm, 12 * cm])
    t1.setStyle(_table_base(font_name))
    story.append(t1)

    story.append(Paragraph("Dados corporais", st["section"]))
    corp = [
        ["Altura (m) *", ""],
        ["Peso (kg) *", ""],
        ["IMC (calculado)", ""],
    ]
    t2 = Table(corp, colWidths=[4.5 * cm, 12 * cm])
    t2.setStyle(_table_base(font_name))
    story.append(t2)

    story.append(Paragraph("Observacoes", st["section"]))
    story.append(_linha_em_branco(6))

    story.append(Spacer(1, 0.3 * cm))
    story.append(
        Paragraph(
            "Campos com * sao obrigatorios no cadastro digital do EasyFeet.",
            st["small"],
        )
    )
    doc.build(story)


def export_ficha_cadastro_paciente_pdf_preenchida(
    destino: Path,
    *,
    cliente: Cliente,
) -> None:
    """PDF com dados do paciente gravados no sistema."""
    doc, st, font_name = _build_doc(destino, f"Cadastro — {cliente.nome}")
    story: list = []
    imc_txt = formatar_imc(calcular_imc(cliente.altura_m, cliente.peso_kg))

    story.extend(cabecalho_pdf(st, "EasyFeet — Ficha de cadastro de paciente"))
    story.append(
        Paragraph(
            f"Documento gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} — dados do sistema.",
            st["subtitle"],
        )
    )

    story.append(Paragraph("Identificacao", st["section"]))
    rows = [
        ["ID", f"#{cliente.id}"],
        ["Nome", cliente.nome],
        ["Telefone", cliente.telefone or "—"],
        ["Email", cliente.email or "—"],
        ["Nascimento", cliente.data_nascimento or "—"],
        ["Sexo", cliente.sexo or "—"],
        ["Lateralidade", cliente.lateralidade or "—"],
        ["Cadastrado em", cliente.criado_em.strftime("%d/%m/%Y %H:%M") if cliente.criado_em else "—"],
    ]
    t = Table(rows, colWidths=[4.5 * cm, 12 * cm])
    t.setStyle(_table_base(font_name))
    story.append(t)

    story.append(Paragraph("Dados corporais", st["section"]))
    corp = [
        ["Altura (m)", formatar_altura(cliente.altura_m) or "—"],
        ["Peso (kg)", formatar_peso(cliente.peso_kg) or "—"],
        ["IMC", imc_txt or "—"],
    ]
    t2 = Table(corp, colWidths=[4.5 * cm, 12 * cm])
    t2.setStyle(_table_base(font_name))
    story.append(t2)

    story.append(Paragraph("Observacoes", st["section"]))
    story.append(Paragraph((cliente.observacoes or "—").replace("\n", "<br/>"), st["body"]))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("EasyFeet — ficha de cadastro preenchida.", st["small"]))
    doc.build(story)
