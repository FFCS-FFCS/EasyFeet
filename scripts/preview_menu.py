from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from easyfeet.navigation import build_crud_routes, get_visible_menu_for_role, load_menu_config


def main() -> None:
    config = load_menu_config()

    print("=== EasyFeet | Preview de menu por perfil ===")
    for role in config["roles"]:
        print(f"\nPerfil: {role}")
        for item in get_visible_menu_for_role(config, role):
            print(f"- {item['label']} ({item['route']})")

    print("\n=== Rotas CRUD padrao ===")
    routes = build_crud_routes(config)
    for resource, actions in routes.items():
        print(f"\n[{resource}]")
        for action, route in actions.items():
            print(f"  {action:8} -> {route}")


if __name__ == "__main__":
    main()
