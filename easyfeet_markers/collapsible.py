"""Secção recolhível (legenda de marcadores no rodapé do EFM)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class CollapsibleFooter(ttk.Frame):
    """Barra com botão para expandir/recolher o conteúdo abaixo."""

    def __init__(
        self,
        parent: tk.Misc,
        title: str,
        *,
        start_expanded: bool = True,
        button_style: str | None = None,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._expanded = start_expanded

        btn_kw: dict = {"command": self._on_toggle}
        if button_style:
            btn_kw["style"] = button_style
        self._toggle = ttk.Button(self, **btn_kw)
        self._toggle.pack(anchor="w", fill="x", pady=(0, 2))

        self._body = ttk.Frame(self)
        self._sync()

    @property
    def body(self) -> ttk.Frame:
        return self._body

    def _sync(self) -> None:
        arrow = "▼" if self._expanded else "▶"
        self._toggle.configure(text=f"{arrow} {self._title}")
        if self._expanded:
            self._body.pack(fill="x", pady=(0, 4))
        else:
            self._body.pack_forget()

    def _on_toggle(self) -> None:
        self._expanded = not self._expanded
        self._sync()
