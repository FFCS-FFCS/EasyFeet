from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from easyfeet.paths import DATA_DIR

DB_PATH = DATA_DIR / "easyfeet.db"
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    from easyfeet.models import (  # noqa: F401
        Avaliacao,
        Cliente,
        ImagemPlantar,
        Laudo,
        MarcacaoPlantar,
        FichaPodoscopio,
        MomentoClinico,
        PalmilhaPedido,
    )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    _ensure_cliente_columns()


def _ensure_cliente_columns() -> None:
    """Migração leve para MVP: garante novas colunas em banco SQLite existente."""
    with engine.begin() as conn:
        cols = conn.execute(text("PRAGMA table_info(clientes)")).fetchall()
        col_names = {str(c[1]) for c in cols}
        if "sexo" not in col_names:
            conn.execute(text("ALTER TABLE clientes ADD COLUMN sexo VARCHAR(20) DEFAULT ''"))
        if "altura_m" not in col_names:
            conn.execute(text("ALTER TABLE clientes ADD COLUMN altura_m REAL"))
        if "peso_kg" not in col_names:
            conn.execute(text("ALTER TABLE clientes ADD COLUMN peso_kg REAL"))
        if "lateralidade" not in col_names:
            conn.execute(text("ALTER TABLE clientes ADD COLUMN lateralidade VARCHAR(20) DEFAULT ''"))
        if "criado_em" not in col_names:
            conn.execute(text("ALTER TABLE clientes ADD COLUMN criado_em DATETIME"))
            conn.execute(text("UPDATE clientes SET criado_em = CURRENT_TIMESTAMP WHERE criado_em IS NULL"))
