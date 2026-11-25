"""Textos-modelo do laudo Navicular (PEND-NAV-LAUDO-001) — Modo A / Brody."""

from __future__ import annotations

from easyfeet.models import FichaNavicular
from easyfeet.navicular import NAVICULAR_LIMIAR_MM

RODAPE_LAUDO_NAVICULAR = (
    "Classificacao Modo A (EasyFeet): limiar Brody — queda navicular "
    f"≤ {NAVICULAR_LIMIAR_MM} mm = normal; > {NAVICULAR_LIMIAR_MM} mm = alterado. "
    "Este laudo reflecte a avaliacao objectiva registada na ficha clinica e nao substitui "
    "julgamento medico integral."
)

RECOMENDACOES_PADRAO_ALTERADO = """\
- Correlacionar achados com queixa, exame postural, marcha e, se disponivel, plantigrafo/podoscopio.
- Orientar fortalecimento/estabilizacao do complexo medial do pe e cadeia posterior, conforme avaliacao global.
- Considerar palmilha de suporte medial / controle de pronacao se houver sintomatologia ou sobrecarga compativel.
- Reavaliar em 3–6 meses ou apos intervencao, repetindo o teste nas mesmas condicoes.
- Encaminhar a ortopedia/podologia se dor persistente, assimetria marcada ou suspeita de patologia estrutural.

Evitar diagnostico de «pe plano» apenas com este teste — preferir «compativel com…» / «sugere…».\
"""

RECOMENDACOES_PADRAO_NORMAL = """\
- Manter acompanhamento clinico conforme queixa e exame global.
- Repetir o teste se houver mudanca de sintomas ou apos intervencao, nas mesmas condicoes.\
"""


def _fmt_mm(valor: float | None) -> str:
    if valor is None:
        return "—"
    if valor == int(valor):
        return str(int(valor))
    return str(valor)


def _pe_alterado(classificacao: str) -> bool:
    return (classificacao or "").strip().lower() == "alterado"


def ficha_pronta_para_laudo(ficha: FichaNavicular) -> bool:
    return (
        ficha.queda_d_mm is not None
        and ficha.queda_e_mm is not None
        and bool(ficha.classificacao_d)
        and bool(ficha.classificacao_e)
    )


def gerar_textos_laudo(ficha: FichaNavicular) -> dict[str, str]:
    """Retorna interpretacao, conclusao e recomendacoes conforme §4 do MD de textos modelo."""
    if not ficha_pronta_para_laudo(ficha):
        raise ValueError(
            "Ficha incompleta: preencha medicoes e classificacao de ambos os pes antes de gerar o laudo."
        )

    xd = ficha.queda_d_mm
    xe = ficha.queda_e_mm
    assert xd is not None and xe is not None
    xs = _fmt_mm(xd)
    ys = _fmt_mm(xe)
    alt_d = _pe_alterado(ficha.classificacao_d)
    alt_e = _pe_alterado(ficha.classificacao_e)

    if alt_d and not alt_e:
        interpretacao = (
            f"No teste da queda do navicular (protocolo sentado → em pe), o pe direito apresentou queda de "
            f"{xs} mm, superior a {NAVICULAR_LIMIAR_MM} mm (criterio Brody / Modo A EasyFeet). "
            f"O pe esquerdo manteve queda de {ys} mm, dentro do limiar (≤ {NAVICULAR_LIMIAR_MM} mm). "
            "O achado a direita sugere maior mobilidade/pronacao desse segmento na passagem de descarga parcial "
            "para carga completa, sem caracterizar, isoladamente, patologia especifica."
        )
        conclusao = "Teste navicular alterado a direita; normal a esquerda — assimetria entre membros."
        recomendacoes = RECOMENDACOES_PADRAO_ALTERADO
    elif alt_e and not alt_d:
        interpretacao = (
            f"No teste da queda do navicular, o pe esquerdo apresentou queda de {ys} mm (> {NAVICULAR_LIMIAR_MM} mm). "
            f"O pe direito apresentou queda de {xs} mm (≤ {NAVICULAR_LIMIAR_MM} mm). "
            "O resultado a esquerda indica queda navicular acima do limiar de referencia, compativel com maior "
            "flexibilidade/pronacao desse lado na avaliacao realizada."
        )
        conclusao = "Teste navicular alterado a esquerda; normal a direita."
        recomendacoes = RECOMENDACOES_PADRAO_ALTERADO
    elif alt_d and alt_e:
        interpretacao = (
            f"Em ambos os pes, a queda navicular foi superior a {NAVICULAR_LIMIAR_MM} mm "
            f"(pe direito: {xs} mm; pe esquerdo: {ys} mm), ultrapassando o limiar Brody (Modo A). "
            "O padrao e compativel com arco plantar mais flexivel e/ou pronacao funcional bilateral na transicao "
            "sentado → ortostase. A magnitude da queda (e eventual diferenca entre lados) deve ser integrada a "
            "queixa e ao exame clinico global."
        )
        conclusao = f"Teste da queda do navicular alterado bilateralmente (D: {xs} mm; E: {ys} mm)."
        recomendacoes = RECOMENDACOES_PADRAO_ALTERADO
    else:
        interpretacao = (
            f"Queda navicular ≤ {NAVICULAR_LIMIAR_MM} mm em ambos os pes "
            f"(D: {xs} mm; E: {ys} mm), dentro do criterio Brody (Modo A)."
        )
        conclusao = "Teste navicular sem alteracao pelo limiar adoptado."
        recomendacoes = RECOMENDACOES_PADRAO_NORMAL

    return {
        "interpretacao": interpretacao,
        "conclusao": conclusao,
        "recomendacoes": recomendacoes,
    }
