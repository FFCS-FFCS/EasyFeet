"""Texto de ajuda do marcador plantar: carrega help_plantar_pt.txt se existir (editável pelo utilizador)."""

from __future__ import annotations

from pathlib import Path

_FALLBACK_PT = """MARCADOR DE LINHAS — VISTA PLANTAR

Consulte o ficheiro help_plantar_pt.txt na pasta marcador_plantar para o texto completo de ajuda.
"""


def help_plantar_text() -> str:
    base = Path(__file__).resolve().parent
    custom = base / "help_plantar_pt.txt"
    if custom.is_file():
        try:
            return custom.read_text(encoding="utf-8").rstrip() + "\n"
        except OSError:
            pass
    return _FALLBACK_PT
