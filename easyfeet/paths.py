"""Raiz do repositório EasyFeet (independente do diretório de trabalho atual)."""

from __future__ import annotations

import sys
from pathlib import Path


def _project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


PROJECT_ROOT = _project_root()
DATA_DIR = PROJECT_ROOT / "data"

# Prefixos absolutos antigos (migração de pasta do projeto).
_LEGACY_ROOTS: tuple[Path, ...] = (
    Path(r"C:\Cursor_Projetos\EasyFeet"),
)


def _remap_from_legacy_root(p: Path) -> Path | None:
    """Se o caminho estiver sob uma raiz antiga, devolve o equivalente em PROJECT_ROOT."""
    resolved = p.resolve()
    for old in _LEGACY_ROOTS:
        try:
            rel = resolved.relative_to(old.resolve())
            return PROJECT_ROOT / rel
        except ValueError:
            low = str(resolved).lower().replace("/", "\\")
            old_s = str(old.resolve()).lower().replace("/", "\\")
            if low.startswith(old_s):
                tail = str(resolved)[len(str(old.resolve())) :].lstrip("\\/")
                if tail:
                    return PROJECT_ROOT / tail
    return None


def resolve_project_file(stored: str) -> Path | None:
    """Resolve caminho gravado (absoluto legado, relativo ou já no root atual)."""
    raw = (stored or "").strip()
    if not raw:
        return None
    p = Path(raw)
    candidates: list[Path] = []
    if p.is_absolute():
        remapped = _remap_from_legacy_root(p)
        if remapped is not None:
            candidates.append(remapped)
        candidates.append(p.resolve())
    else:
        candidates.append(PROJECT_ROOT / p)
    for c in candidates:
        if c.exists():
            return c.resolve()
    return None


def stored_path_for_write(path: Path) -> str:
    """Prefere caminho relativo à raiz do projeto (portável entre máquinas/pastas)."""
    resolved = path.resolve()
    remapped = _remap_from_legacy_root(resolved)
    if remapped is not None and remapped.exists():
        resolved = remapped.resolve()
    try:
        rel = resolved.relative_to(PROJECT_ROOT.resolve())
        return str(rel)
    except ValueError:
        return str(resolved)
