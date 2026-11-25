from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "menu-config-v2.json"
LEGACY_CONFIG_PATH = Path(__file__).resolve().parents[1] / "menu-config-v1.json"


class MenuConfigError(Exception):
    """Raised when menu configuration is invalid."""


def load_menu_config(config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Menu configuration file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    _validate_menu_config(data)
    return data


def get_visible_menu_for_role(config: dict[str, Any], role: str) -> list[dict[str, Any]]:
    roles = config.get("roles", [])
    if role not in roles:
        raise MenuConfigError(f"Role '{role}' not found in menu configuration.")

    visible = [
        item
        for item in config.get("menu", [])
        if role in item.get("visibleFor", []) and not item.get("hiddenInSidebar")
    ]
    return sorted(visible, key=lambda x: x.get("order", 9999))


def iter_menu_roots_for_role(config: dict[str, Any], role: str) -> list[dict[str, Any]]:
    """Itens raiz visíveis para o perfil (inclui hiddenInSidebar — ex.: ficha clínica)."""
    roots = [item for item in config.get("menu", []) if role in item.get("visibleFor", [])]
    return sorted(roots, key=lambda x: x.get("order", 9999))


def get_visible_child_menu_items(parent_item: dict[str, Any], role: str) -> list[dict[str, Any]]:
    """Filhos do item de menu visíveis para o perfil (herdam visibleFor do pai se omitido)."""
    parent_roles = list(parent_item.get("visibleFor", []))
    out: list[dict[str, Any]] = []
    for ch in parent_item.get("children") or []:
        ch_roles = ch.get("visibleFor")
        effective = ch_roles if isinstance(ch_roles, list) and ch_roles else parent_roles
        if role in effective:
            out.append(ch)
    return sorted(out, key=lambda x: x.get("order", 9999))


def collect_nav_module_ids_for_role(config: dict[str, Any], role: str) -> set[str]:
    """IDs de módulos de navegação (itens raiz + filhos, inclusive aninhados) visíveis para o perfil."""

    def walk(item: dict[str, Any]) -> None:
        ids.add(str(item["id"]))
        for ch in get_visible_child_menu_items(item, role):
            walk(ch)

    ids: set[str] = set()
    for item in iter_menu_roots_for_role(config, role):
        walk(item)
    return ids


def collect_nav_accordion_group_ids_for_role(config: dict[str, Any], role: str) -> set[str]:
    """IDs de grupos sanfona (itens com filhos visiveis) — estado inicial fechado na sidebar."""

    def walk(item: dict[str, Any]) -> None:
        children = get_visible_child_menu_items(item, role)
        if not children:
            return
        ids.add(str(item["id"]))
        for ch in children:
            walk(ch)

    ids: set[str] = set()
    for item in get_visible_menu_for_role(config, role):
        walk(item)
    return ids


def find_menu_item_path(config: dict[str, Any], module_id: str) -> list[dict[str, Any]]:
    """Caminho do item no menu: [raiz, ..., item] ou lista vazia se não existir."""
    target = str(module_id)

    def search(items: list[dict[str, Any]], trail: list[dict[str, Any]]) -> list[dict[str, Any]] | None:
        for item in items:
            path = trail + [item]
            if str(item.get("id")) == target:
                return path
            children = item.get("children") or []
            if children:
                found = search(children, path)
                if found is not None:
                    return found
        return None

    return search(config.get("menu", []), []) or []


def build_crud_routes(config: dict[str, Any]) -> dict[str, dict[str, str]]:
    routes: dict[str, dict[str, str]] = {}

    for item in config.get("menu", []):
        crud = item.get("crud")
        if not crud:
            continue

        resource = crud.get("resource")
        actions = crud.get("actions", [])
        if not resource:
            continue

        action_routes: dict[str, str] = {}
        for action in actions:
            if action == "list":
                action_routes[action] = f"/{resource}"
            elif action == "create":
                action_routes[action] = f"/{resource}/novo"
            elif action == "detail":
                action_routes[action] = f"/{resource}/{{id}}"
            elif action == "edit":
                action_routes[action] = f"/{resource}/{{id}}/editar"
            elif action == "archive":
                action_routes[action] = f"/{resource}/{{id}}/arquivar"
            else:
                action_routes[action] = f"/{resource}/{action}"

        routes[resource] = action_routes

    return routes


def _validate_menu_config(config: dict[str, Any]) -> None:
    required_root = ("app", "roles", "menu")
    for key in required_root:
        if key not in config:
            raise MenuConfigError(f"Missing required root key: '{key}'")

    if not isinstance(config.get("roles"), list) or not config["roles"]:
        raise MenuConfigError("'roles' must be a non-empty list.")

    seen_ids: set[str] = set()
    for item in config.get("menu", []):
        item_id = item.get("id")
        if not item_id:
            raise MenuConfigError("Menu item missing 'id'.")
        if item_id in seen_ids:
            raise MenuConfigError(f"Duplicate menu id found: '{item_id}'")
        seen_ids.add(item_id)

        if "label" not in item:
            raise MenuConfigError(f"Menu item '{item_id}' missing 'label'.")
        if "route" not in item:
            raise MenuConfigError(f"Menu item '{item_id}' missing 'route'.")
        if "visibleFor" not in item:
            raise MenuConfigError(f"Menu item '{item_id}' missing 'visibleFor'.")

        _validate_menu_children(item.get("children"), seen_ids, parent_id=item_id)


def _validate_menu_children(
    children: Any,
    seen_ids: set[str],
    *,
    parent_id: str,
) -> None:
    if children is None:
        return
    if not isinstance(children, list):
        raise MenuConfigError(f"Menu item '{parent_id}': 'children' must be a list when present.")
    for ch in children:
        cid = ch.get("id")
        if not cid:
            raise MenuConfigError(f"Menu item '{parent_id}': child missing 'id'.")
        if cid in seen_ids:
            raise MenuConfigError(f"Duplicate menu id found: '{cid}'")
        seen_ids.add(cid)
        if "label" not in ch:
            raise MenuConfigError(f"Menu child '{cid}' missing 'label'.")
        if "route" not in ch:
            raise MenuConfigError(f"Menu child '{cid}' missing 'route'.")
        ch_vis = ch.get("visibleFor")
        if ch_vis is not None and (not isinstance(ch_vis, list) or not ch_vis):
            raise MenuConfigError(f"Menu child '{cid}': 'visibleFor' must be a non-empty list when set.")
        _validate_menu_children(ch.get("children"), seen_ids, parent_id=str(cid))
