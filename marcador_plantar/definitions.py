"""Definicoes de marcadores de linha — protocolo plantar v1 (preto e branco)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

PROTOCOL_ID: Final[str] = "plantar_lines_v1"
JSON_VERSION: Final[str] = "1.0"


@dataclass(frozen=True)
class LineMarkerDef:
    id: str
    letter: str
    label_pt: str


# Ordem fixa A–D = legenda estavel na imagem e no JSON.
LINE_MARKERS: tuple[LineMarkerDef, ...] = (
    LineMarkerDef("line_longitudinal_axis", "A", "Eixo longitudinal"),
    LineMarkerDef("line_width_forefoot", "B", "Largura antepé"),
    LineMarkerDef("line_width_midfoot", "C", "Largura médio-pé"),
    LineMarkerDef("line_width_hindfoot", "D", "Largura retropé"),
)

MARKER_BY_ID: dict[str, LineMarkerDef] = {m.id: m for m in LINE_MARKERS}


def marcador_combo_label(m: LineMarkerDef) -> str:
    """Texto só em português para a lista de tipos e legendas (sem identificadores técnicos em inglês)."""
    return f"{m.letter} — {m.label_pt}"


MARKER_ID_TO_COMBO: dict[str, str] = {m.id: marcador_combo_label(m) for m in LINE_MARKERS}
MARKER_COMBO_TO_ID: dict[str, str] = {v: k for k, v in MARKER_ID_TO_COMBO.items()}
