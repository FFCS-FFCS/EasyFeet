"""Versão semver da aplicação (major.minor.patch)."""

from __future__ import annotations

APP_VERSION_MAJOR = 1
APP_VERSION_MINOR = 0
APP_VERSION_PATCH = 0

APP_VERSION = f"{APP_VERSION_MAJOR}.{APP_VERSION_MINOR}.{APP_VERSION_PATCH}"


def format_app_version(*, prefix: str = "v") -> str:
    return f"{prefix}{APP_VERSION}"
