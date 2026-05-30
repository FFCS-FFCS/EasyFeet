"""Verificacao rapida das tabelas Fase 2 marcadores."""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from easyfeet.db import DB_PATH, init_db

init_db()
conn = sqlite3.connect(str(DB_PATH))
rows = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' "
    "AND (name LIKE '%plantar%' OR name LIKE '%clinico%')"
).fetchall()
conn.close()
print("Tabelas:", rows)
expected = {"momentos_clinicos", "imagens_plantares", "marcacoes_plantares"}
found = {r[0] for r in rows}
missing = expected - found
if missing:
    print("FALHOU: faltam", missing)
    raise SystemExit(1)
print("OK: tabelas Fase 2 presentes")
