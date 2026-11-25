"""Exportacao da ficha tecnica de podoscopio para PDF (branco ou preenchida)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from easyfeet.models import FichaPodoscopio
from easyfeet.pdf_brand import (
    cabecalho_pdf,
    col_widths_rotulo_valor,
    ensure_pdf_font,
    pdf_page_number_callbacks,
)

ARCO_OPCOES = ("Normal", "Plano", "Cavo", "Nao avaliado")
APOIO_OPCOES = ("Neutro", "Pronado", "Supinado", "Misto", "Nao avaliado")
SIMETRIA_OPCOES = ("Simetrica", "Maior a direita", "Maior a esquerda", "Nao avaliado")
HIPER_ZONAS = ("Calcaneo", "Metatarsos", "Halux", "Borda lateral", "Medio-pe")

_ROTULOS_TABELA = (
    "Paciente",
    "Data da avaliacao",
    "Rotulo do atendimento",
    "Arco plantar — pe direito",
    "Arco plantar — pe esquerdo",
    "Apoio predominante — pe direito",
    "Apoio predominante — pe esquerdo",
    "Simetria de carga",
)


def _larguras_colunas(font_name: str) -> list[float]:
    rotulo_w, valor_w = col_widths_rotulo_valor(font_name, _ROTULOS_TABELA)
    return [rotulo_w, valor_w]

_NOTA_CADASTRO = (
    "Dados cadastrais do paciente (nome, contato, nascimento, etc.) constam na ficha de cadastro "
    "exportada em Pacientes — nao neste documento."
)


def _styles(font_name: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "EFTitle",
            parent=base["Heading1"],
            fontName=font_name,
            fontSize=16,
            textColor=colors.HexColor("#7c1229"),
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "EFSubtitle",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=10,
            textColor=colors.HexColor("#666666"),
            spaceAfter=12,
        ),
        "section": ParagraphStyle(
            "EFSection",
            parent=base["Heading2"],
            fontName=font_name,
            fontSize=12,
            textColor=colors.HexColor("#7c1229"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "EFBody",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=10,
            leading=14,
        ),
        "small": ParagraphStyle(
            "EFSmall",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=8,
            textColor=colors.HexColor("#888888"),
        ),
    }


def _table_base(
    font_name: str,
    *,
    header: bool = False,
    valign: str = "MIDDLE",
    compact: bool = False,
) -> TableStyle:
    pad = 3 if compact else 6
    hpad = 6 if compact else 8
    style = [
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
        ("VALIGN", (0, 0), (-1, -1), valign),
        ("LEFTPADDING", (0, 0), (-1, -1), hpad),
        ("RIGHTPADDING", (0, 0), (-1, -1), hpad),
        ("TOPPADDING", (0, 0), (-1, -1), pad),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
    ]
    if header:
        style.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7c1229")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ]
        )
    else:
        style.append(("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f5f5f5")))
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
        ParagraphStyle("EFPodDataHora", fontName=font_name, fontSize=10, leading=12),
    )


def _celula_rotulo(font_name: str, texto: str, *, compact: bool = False) -> Paragraph:
    """Rotulo com quebra de linha (evita invadir a coluna ao lado)."""
    html = texto.replace(" — ", "<br/>")
    return Paragraph(
        html,
        ParagraphStyle(
            "EFPodRotulo",
            fontName=font_name,
            fontSize=9,
            leading=10 if compact else 11,
        ),
    )


def _celula_valor_vazio(font_name: str) -> Paragraph:
    return Paragraph(
        "&nbsp;",
        ParagraphStyle("EFPodValorVazio", fontName=font_name, fontSize=10, leading=12),
    )


def _celula_valor(font_name: str, texto: str) -> Paragraph:
    return Paragraph(
        (texto or "—").replace("\n", "<br/>"),
        ParagraphStyle(
            "EFPodValor",
            fontName=font_name,
            fontSize=10,
            leading=13,
        ),
    )


def _opcoes_celula(
    font_name: str,
    opcoes: tuple[str, ...],
    *,
    valor: str | None = None,
    compact: bool = False,
) -> Paragraph:
    """Opcoes uma por linha (evita texto sobreposto em colunas estreitas)."""
    v = (valor or "").strip()
    lines = [f"({'X' if o == v else ' '}) {o}" for o in opcoes]
    leading = 11 if compact else 13
    size = 8 if compact else 9
    return Paragraph(
        "<br/>".join(lines),
        ParagraphStyle(
            "EFPodOpcoes",
            fontName=font_name,
            fontSize=size,
            leading=leading,
        ),
    )


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
    """Mantem titulo e conteudo na mesma pagina quando couber."""
    return KeepTogether([_secao(st, titulo), *conteudo])


def _build_with_page_numbers(doc: SimpleDocTemplate, story: list, font_name: str) -> None:
    on_page, on_later = pdf_page_number_callbacks(font_name)
    doc.build(story, onFirstPage=on_page, onLaterPages=on_later)


def _bloco_identificacao_branco(font_name: str, col_widths: list[float]) -> list:
    id_rows = [
        [
            _celula_rotulo(font_name, "Data da avaliacao", compact=True),
            _campo_data_hora_em_branco(font_name),
        ],
        [
            _celula_rotulo(font_name, "Rotulo do atendimento", compact=True),
            _celula_valor_vazio(font_name),
        ],
    ]
    t_id = Table(id_rows, colWidths=col_widths)
    t_id.setStyle(_table_base(font_name, valign="TOP", compact=True))
    return [t_id]


def _bloco_identificacao_preenchida(
    font_name: str,
    ficha: FichaPodoscopio,
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


def _bloco_paciente_nome(font_name: str, paciente_nome: str | None, col_widths: list[float]) -> list:
    row = [[_celula_rotulo(font_name, "Paciente"), _celula_valor(font_name, (paciente_nome or "—"))]]
    t = Table(row, colWidths=col_widths)
    t.setStyle(_table_base(font_name, valign="TOP"))
    return [t]


def _bloco_paciente_nome_em_branco(font_name: str, col_widths: list[float]) -> list:
    row = [[_celula_rotulo(font_name, "Paciente", compact=True), _celula_valor_vazio(font_name)]]
    t = Table(row, colWidths=col_widths)
    t.setStyle(_table_base(font_name, valign="TOP", compact=True))
    return [t]


def _bloco_plantar_branco(font_name: str, col_widths: list[float]) -> Table:
    """Uma linha por campo editavel (igual ao modulo), opcoes com quebra de linha."""
    plantar_rows = [
        [
            _celula_rotulo(font_name, "Arco plantar — pe direito", compact=True),
            _opcoes_celula(font_name, ARCO_OPCOES, compact=True),
        ],
        [
            _celula_rotulo(font_name, "Arco plantar — pe esquerdo", compact=True),
            _opcoes_celula(font_name, ARCO_OPCOES, compact=True),
        ],
        [
            _celula_rotulo(font_name, "Apoio predominante — pe direito", compact=True),
            _opcoes_celula(font_name, APOIO_OPCOES, compact=True),
        ],
        [
            _celula_rotulo(font_name, "Apoio predominante — pe esquerdo", compact=True),
            _opcoes_celula(font_name, APOIO_OPCOES, compact=True),
        ],
        [
            _celula_rotulo(font_name, "Simetria de carga", compact=True),
            _opcoes_celula(font_name, SIMETRIA_OPCOES, compact=True),
        ],
    ]
    t_pl = Table(plantar_rows, colWidths=col_widths)
    t_pl.setStyle(_table_base(font_name, valign="TOP", compact=True))
    return t_pl


def _bloco_plantar_preenchida(font_name: str, ficha: FichaPodoscopio, col_widths: list[float]) -> Table:
    plantar_rows = [
        [
            _celula_rotulo(font_name, "Arco plantar — pe direito"),
            _celula_valor(font_name, ficha.arco_pe_direito),
        ],
        [
            _celula_rotulo(font_name, "Arco plantar — pe esquerdo"),
            _celula_valor(font_name, ficha.arco_pe_esquerdo),
        ],
        [
            _celula_rotulo(font_name, "Apoio predominante — pe direito"),
            _celula_valor(font_name, ficha.apoio_pe_direito),
        ],
        [
            _celula_rotulo(font_name, "Apoio predominante — pe esquerdo"),
            _celula_valor(font_name, ficha.apoio_pe_esquerdo),
        ],
        [
            _celula_rotulo(font_name, "Simetria de carga"),
            _celula_valor(font_name, ficha.simetria_carga),
        ],
    ]
    t_pl = Table(plantar_rows, colWidths=col_widths)
    t_pl.setStyle(_table_base(font_name, valign="TOP"))
    return t_pl


def _bloco_hiperpressao_branco(font_name: str) -> Paragraph:
    return _opcoes_celula(font_name, HIPER_ZONAS, compact=True)


def _bloco_hiperpressao_preenchida(font_name: str, ficha: FichaPodoscopio) -> Paragraph:
    zonas_marcadas = {z.strip() for z in (ficha.hiperpressao_zonas or "").split(";") if z.strip()}
    marcadas = tuple(z for z in HIPER_ZONAS if z in zonas_marcadas)
    if not marcadas:
        return Paragraph("Nenhuma zona assinalada", ParagraphStyle("EFPodHip", fontName=font_name, fontSize=9))
    return Paragraph(
        ", ".join(marcadas),
        ParagraphStyle("EFPodHip", fontName=font_name, fontSize=10, leading=14),
    )


def export_ficha_podoscopio_pdf_branco(destino: Path) -> None:
    """PDF para impressao e preenchimento manual (somente campos da ficha tecnica)."""
    doc, st, font_name = _build_doc(destino, "Ficha Podoscopio — em branco")
    col_widths = _larguras_colunas(font_name)
    story: list = []

    story.extend(cabecalho_pdf(st, "EasyFeet — Ficha tecnica de podoscopia"))
    story.append(
        Paragraph(
            "Versao para preenchimento manual. Depois, digite os dados no modulo Podoscopio. "
            + _NOTA_CADASTRO,
            st["subtitle"],
        )
    )

    story.append(_bloco_secao(st, "Paciente", _bloco_paciente_nome_em_branco(font_name, col_widths)))
    story.append(Spacer(1, 0.15 * cm))
    story.append(
        _bloco_secao(st, "Identificacao da avaliacao", _bloco_identificacao_branco(font_name, col_widths))
    )
    story.append(Spacer(1, 0.15 * cm))
    story.append(_bloco_secao(st, "Queixa / objetivo", [_linha_em_branco(4)]))
    story.append(
        _bloco_secao(
            st,
            "Leitura plantar (podoscopio) — marque ( ) a opcao observada",
            [_bloco_plantar_branco(font_name, col_widths)],
        )
    )
    story.append(
        _bloco_secao(
            st,
            "Hiperpressao (marcar com X se observado)",
            [_bloco_hiperpressao_branco(font_name)],
        )
    )
    story.append(_bloco_secao(st, "Observacoes clinicas", [_linha_em_branco(5)]))

    story.append(Spacer(1, 0.3 * cm))
    story.append(
        KeepTogether(
            [
                Paragraph(
                    "Documento apenas com dados textuais da avaliacao podoscopica (sem imagens). "
                    "Registro complementar; nao substitui exame clinico completo.",
                    st["small"],
                )
            ]
        )
    )
    _build_with_page_numbers(doc, story, font_name)


def export_ficha_podoscopio_pdf_preenchida(
    destino: Path,
    *,
    ficha: FichaPodoscopio,
    paciente_nome: str | None = None,
) -> None:
    """PDF com os dados gravados na ficha tecnica (sem dados cadastrais do paciente)."""
    doc, st, font_name = _build_doc(destino, "Ficha Podoscopio — preenchida")
    col_widths = _larguras_colunas(font_name)
    story: list = []

    story.extend(cabecalho_pdf(st, "EasyFeet — Ficha tecnica de podoscopia"))
    story.append(
        Paragraph(
            f"Documento gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} — dados digitados no modulo Podoscopio. "
            + _NOTA_CADASTRO,
            st["subtitle"],
        )
    )

    story.append(_bloco_secao(st, "Paciente", _bloco_paciente_nome(font_name, paciente_nome, col_widths)))
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
            "Leitura plantar (podoscopio)",
            [_bloco_plantar_preenchida(font_name, ficha, col_widths)],
        )
    )
    story.append(
        _bloco_secao(
            st,
            "Hiperpressao observada",
            [_bloco_hiperpressao_preenchida(font_name, ficha)],
        )
    )
    story.append(
        _bloco_secao(
            st,
            "Observacoes clinicas",
            [Paragraph((ficha.observacoes or "—").replace("\n", "<br/>"), st["body"])],
        )
    )

    story.append(Spacer(1, 0.3 * cm))
    story.append(
        KeepTogether(
            [
                Paragraph(
                    "EasyFeet — ficha podoscopica preenchida (somente dados textuais, sem imagens).",
                    st["small"],
                )
            ]
        )
    )
    _build_with_page_numbers(doc, story, font_name)


def export_ficha_podoscopio_pdf(destino: Path, *, ficha: FichaPodoscopio) -> None:
    """Compatibilidade: alias da exportacao preenchida."""
    export_ficha_podoscopio_pdf_preenchida(destino, ficha=ficha, paciente_nome=None)
