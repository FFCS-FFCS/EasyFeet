from easyfeet.cli import executar_cli
from easyfeet.db import SessionLocal, init_db


def main() -> None:
    init_db()
    with SessionLocal() as session:
        executar_cli(session)


if __name__ == "__main__":
    main()
