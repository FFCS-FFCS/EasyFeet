"""Teste Navicular — Modo A (Brody): limiar fixo em mm."""

from __future__ import annotations

NAVICULAR_LIMIAR_MM = 10


def parse_altura_mm(texto: str) -> float | None:
    raw = (texto or "").strip().replace(",", ".")
    if not raw:
        return None
    try:
        valor = float(raw)
    except ValueError as exc:
        raise ValueError("Medicao invalida. Informe apenas numeros em milimetros.") from exc
    if valor < 0:
        raise ValueError("Medicao em mm nao pode ser negativa.")
    return valor


def calcular_queda_mm(
    altura_sentado: float | None,
    altura_pe: float | None,
) -> float | None:
    if altura_sentado is None or altura_pe is None:
        return None
    if altura_sentado <= altura_pe:
        raise ValueError(
            "Altura sentado deve ser maior que altura em pe (queda = sentado − em pe)."
        )
    return round(altura_sentado - altura_pe, 1)


def classificar_modo_a(
    queda_mm: float | None,
    *,
    limiar_mm: float = NAVICULAR_LIMIAR_MM,
) -> str:
    if queda_mm is None:
        return ""
    return "normal" if queda_mm <= limiar_mm else "alterado"


def rotulo_classificacao(classificacao: str) -> str:
    if classificacao == "normal":
        return f"Normal (queda ≤ {NAVICULAR_LIMIAR_MM} mm — Brody)"
    if classificacao == "alterado":
        return f"Alterado (queda > {NAVICULAR_LIMIAR_MM} mm — Brody)"
    return "—"
