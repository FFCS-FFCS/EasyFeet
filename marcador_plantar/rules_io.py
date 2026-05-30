"""Leitura de `marker_rules.json` (sem dependência do pacote easyfeet)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def marker_rules_json_candidates() -> list[Path]:
    """Ordem: ao lado do executável (PyInstaller), raiz do repo, cwd."""
    out: list[Path] = []
    if getattr(sys, "frozen", False):
        out.append(Path(sys.executable).resolve().parent / "data" / "marker_rules.json")
    here = Path(__file__).resolve().parents[1]
    out.append(here / "data" / "marker_rules.json")
    out.append(Path.cwd() / "data" / "marker_rules.json")
    return out


def find_marker_rules_json() -> Path | None:
    for p in marker_rules_json_candidates():
        if p.is_file():
            return p.resolve()
    return None


def load_marker_rules_payload() -> dict[str, Any] | None:
    path = find_marker_rules_json()
    if path is None:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def list_active_line_rules() -> list[dict[str, Any]]:
    """Regras com tipo `linhas` e ativas, para o combobox do EFM."""
    payload = load_marker_rules_payload()
    if not payload:
        return []
    rows: list[dict[str, Any]] = []
    for r in payload.get("rules", []):
        if str(r.get("tipo_marcador", "")).strip() != "linhas":
            continue
        if not bool(r.get("ativo", True)):
            continue
        rows.append(r)
    return sorted(rows, key=lambda x: int(x.get("id", 0)))


def list_active_point_rules() -> list[dict[str, Any]]:
    """Regras com tipo `pontos` e ativas, para o combobox do EFM."""
    payload = load_marker_rules_payload()
    if not payload:
        return []
    rows: list[dict[str, Any]] = []
    for r in payload.get("rules", []):
        if str(r.get("tipo_marcador", "")).strip() != "pontos":
            continue
        if not bool(r.get("ativo", True)):
            continue
        rows.append(r)
    return sorted(rows, key=lambda x: int(x.get("id", 0)))
