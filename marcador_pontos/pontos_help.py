"""Ajuda do marcador de pontos — texto editável em help_pontos_pt.txt."""

from __future__ import annotations

from pathlib import Path

_FALLBACK = """MARCADOR DE PONTOS — REFERÊNCIAS ANATÓMICAS

Edite o ficheiro help_pontos_pt.txt na pasta marcador_pontos.
"""


def help_pontos_text() -> str:
    base = Path(__file__).resolve().parent
    custom = base / "help_pontos_pt.txt"
    if custom.is_file():
        try:
            return custom.read_text(encoding="utf-8").rstrip() + "\n"
        except OSError:
            pass
    return _FALLBACK
