"""Registo de tipos de marcador (extensível). Cada entrada tem id estável e rótulo em português."""

from __future__ import annotations

from dataclasses import dataclass

from marcador_plantar.plantar_help import help_plantar_text
from marcador_pontos.pontos_help import help_pontos_text


@dataclass(frozen=True)
class MarkerKind:
    """Identificador interno + texto mostrado na lista."""

    id: str
    label_pt: str


# Ordem na lista da janela principal.
MARKER_KINDS: tuple[MarkerKind, ...] = (
    MarkerKind("plantar_linhas", "Linhas — vista plantar"),
    MarkerKind("plantar_pontos", "Pontos — articulações e referências"),
)

KIND_BY_ID: dict[str, MarkerKind] = {k.id: k for k in MARKER_KINDS}
KIND_LABEL_TO_ID: dict[str, str] = {k.label_pt: k.id for k in MARKER_KINDS}


def help_text_for_kind(kind_id: str) -> str:
    """Texto de ajuda conforme o tipo de marcador (editável via ficheiros por submódulo)."""
    if kind_id == "plantar_linhas":
        return help_plantar_text()
    if kind_id == "plantar_pontos":
        return help_pontos_text()
    return "Ajuda para este marcador ainda não está definida.\n"
