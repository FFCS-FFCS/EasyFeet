"""Validação de altura, peso e lateralidade no cadastro de pacientes."""

from __future__ import annotations

from dataclasses import dataclass

LATERALIDADE_OPCOES: tuple[str, ...] = ("Destro", "Canhoto", "Ambidestro")

ALTURA_MIN_M = 0.30
ALTURA_MAX_M = 2.50
PESO_MIN_KG = 2.0
PESO_MAX_KG = 400.0


def _parse_decimal_br(raw: str) -> float:
    texto = (raw or "").strip().replace(" ", "")
    if not texto:
        raise ValueError("Valor numerico obrigatorio.")
    texto = texto.replace(",", ".")
    try:
        return float(texto)
    except ValueError as exc:
        raise ValueError("Use apenas numeros (ex.: 1,75 ou 70,5).") from exc


def validar_altura_metros(raw: str) -> float:
    valor = _parse_decimal_br(raw)
    if not (ALTURA_MIN_M <= valor <= ALTURA_MAX_M):
        raise ValueError(f"Altura deve estar entre {ALTURA_MIN_M:g} m e {ALTURA_MAX_M:g} m.")
    return round(valor, 3)


def validar_peso_kg(raw: str) -> float:
    valor = _parse_decimal_br(raw)
    if not (PESO_MIN_KG <= valor <= PESO_MAX_KG):
        raise ValueError(f"Peso deve estar entre {PESO_MIN_KG:g} kg e {PESO_MAX_KG:g} kg.")
    return round(valor, 2)


def validar_lateralidade(raw: str) -> str:
    valor = (raw or "").strip()
    if valor not in LATERALIDADE_OPCOES:
        raise ValueError("Selecione Destro, Canhoto ou Ambidestro.")
    return valor


def formatar_altura(valor: float | None) -> str:
    if valor is None:
        return ""
    return f"{valor:.2f}".replace(".", ",")


def formatar_peso(valor: float | None) -> str:
    if valor is None:
        return ""
    texto = f"{valor:.2f}".rstrip("0").rstrip(".")
    return texto.replace(".", ",")


def calcular_imc(altura_m: float | None, peso_kg: float | None) -> float | None:
    if altura_m is None or peso_kg is None or altura_m <= 0:
        return None
    return round(peso_kg / (altura_m * altura_m), 1)


def formatar_imc(valor: float | None) -> str:
    if valor is None:
        return "-"
    return f"{valor:.1f}".replace(".", ",")


def imc_preview(altura_raw: str, peso_raw: str) -> str:
    """Calcula IMC para exibição em tempo real (sem validar faixas clínicas)."""
    try:
        altura = _parse_decimal_br(altura_raw)
        peso = _parse_decimal_br(peso_raw)
    except ValueError:
        return "-"
    return formatar_imc(calcular_imc(altura, peso))


@dataclass(frozen=True)
class FaixaIMC:
    """Faixa de classificação do IMC (referência OMS para adultos)."""

    nome: str
    intervalo: str
    interpretacao: str
    texto_tabela: str


# Referência habitual em avaliação clínica de adultos (OMS / Ministério da Saúde — Brasil).
FAIXAS_IMC_ADULTO: tuple[FaixaIMC, ...] = (
    FaixaIMC(
        "Baixo peso",
        "Abaixo de 18,5",
        "Peso abaixo do intervalo usual para adultos. Avaliar causas e contexto clínico.",
        "Peso abaixo do usual; avaliar causas e contexto clínico.",
    ),
    FaixaIMC(
        "Peso adequado (eutrofia)",
        "18,5 a 24,9",
        "Faixa em que, em adultos, o IMC costuma associar-se a menor risco metabólico em populacionais.",
        "Faixa habitualmente associada a menor risco metabólico (populacional).",
    ),
    FaixaIMC(
        "Sobrepeso",
        "25,0 a 29,9",
        "Acima do peso considerado adequado para a altura. Ex.: IMC 29 está nesta faixa — não é 'peso ideal', "
        "mas ainda não é obesidade grau I.",
        "Acima do peso adequado; ainda não é obesidade grau I (ex.: IMC 29).",
    ),
    FaixaIMC(
        "Obesidade grau I",
        "30,0 a 34,9",
        "Obesidade. Requer acompanhamento clínico e plano de cuidado.",
        "Obesidade; acompanhamento clínico recomendado.",
    ),
    FaixaIMC(
        "Obesidade grau II",
        "35,0 a 39,9",
        "Obesidade moderada. Risco cardiometabólico elevado.",
        "Obesidade moderada; risco cardiometabólico elevado.",
    ),
    FaixaIMC(
        "Obesidade grau III",
        "40,0 ou mais",
        "Obesidade grave (mórbida).",
        "Obesidade grave (mórbida).",
    ),
)


def classificar_imc(imc: float) -> FaixaIMC:
    if imc < 18.5:
        return FAIXAS_IMC_ADULTO[0]
    if imc < 25.0:
        return FAIXAS_IMC_ADULTO[1]
    if imc < 30.0:
        return FAIXAS_IMC_ADULTO[2]
    if imc < 35.0:
        return FAIXAS_IMC_ADULTO[3]
    if imc < 40.0:
        return FAIXAS_IMC_ADULTO[4]
    return FAIXAS_IMC_ADULTO[5]


def imc_valor_numerico(altura_raw: str, peso_raw: str) -> float | None:
    try:
        return calcular_imc(_parse_decimal_br(altura_raw), _parse_decimal_br(peso_raw))
    except ValueError:
        return None


def texto_ajuda_imc(altura_raw: str = "", peso_raw: str = "") -> str:
    """Texto da janela de ajuda com tabela e interpretação do IMC atual (se houver)."""
    linhas: list[str] = [
        "Índice de Massa Corporal (IMC) = peso (kg) ÷ [altura (m)]²",
        "",
        "Referência para adultos (18 anos ou mais), como na prática clínica habitual (OMS).",
        "Para crianças e adolescentes usam-se curvas pediátricas por idade e sexo — não esta tabela.",
        "",
    ]
    atual = imc_valor_numerico(altura_raw, peso_raw)
    if atual is not None:
        faixa = classificar_imc(atual)
        linhas.extend(
            [
                f">> IMC calculado agora: {formatar_imc(atual)}  ->  {faixa.nome}",
                f"   {faixa.interpretacao}",
                "",
            ]
        )
    else:
        linhas.extend([">> Preencha altura e peso para ver a classificacao do paciente aqui.", ""])

    linhas.append("Tabela de referência (adultos):")
    linhas.append("")
    for f in FAIXAS_IMC_ADULTO:
        marcador = "  << " if atual is not None and classificar_imc(atual) == f else "    "
        linhas.append(f"{marcador}IMC {f.intervalo}: {f.nome}")
        linhas.append(f"      {f.interpretacao}")
        linhas.append("")

    linhas.append(
        "Nota: o IMC é um indicador populacional, não substitui exame clínico, composição corporal "
        "ou avaliação postural/plantar do EasyFeet."
    )
    return "\n".join(linhas)
