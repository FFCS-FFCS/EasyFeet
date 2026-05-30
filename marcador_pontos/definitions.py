"""Marcadores de ponto — referências anatómicas na vista plantar (protocolo pontos v1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

PROTOCOL_ID: Final[str] = "plantar_points_v1"
JSON_VERSION: Final[str] = "1.0"


@dataclass(frozen=True)
class PointMarkerDef:
    id: str
    letter: str
    label_pt: str


# Ordem fixa A–F; pode alargar mais tarde mantendo letras e ids estáveis no JSON.
POINT_MARKERS: tuple[PointMarkerDef, ...] = (
    PointMarkerDef("point_hallux_mtp", "A", "Hálux — articulação MTP"),
    PointMarkerDef("point_fifth_met_head", "B", "5.º metatarso — cabeça"),
    PointMarkerDef("point_medial_midfoot", "C", "Médio-pé — referência medial"),
    PointMarkerDef("point_calcaneus_medial", "D", "Calcâneo — face medial"),
    PointMarkerDef("point_calcaneus_lateral", "E", "Calcâneo — face lateral"),
    PointMarkerDef("point_retrofoot_center", "F", "Retropé — referência central"),
)

MARKER_BY_ID: dict[str, PointMarkerDef] = {m.id: m for m in POINT_MARKERS}


def marcador_combo_label(m: PointMarkerDef) -> str:
    return f"{m.letter} — {m.label_pt}"


MARKER_ID_TO_COMBO: dict[str, str] = {m.id: marcador_combo_label(m) for m in POINT_MARKERS}
MARKER_COMBO_TO_ID: dict[str, str] = {v: k for k, v in MARKER_ID_TO_COMBO.items()}
