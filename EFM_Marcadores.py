"""EasyFeet — Módulo de marcadores (EFM). Ponto de entrada único para todos os tipos de marcador."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from easyfeet_markers.app import main

if __name__ == "__main__":
    main()
