from easyfeet.db import SessionLocal, init_db
from easyfeet.gui import EasyFeetApp
from easyfeet.services import EasyFeetService


def main() -> None:
    init_db()
    with SessionLocal() as session:
        service = EasyFeetService(session)
        app = EasyFeetApp(service)
        app.mainloop()


if __name__ == "__main__":
    main()
