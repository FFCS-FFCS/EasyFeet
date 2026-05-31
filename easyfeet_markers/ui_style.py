"""Fonte do módulo EFM — tamanhos coordenados (protótipo e integração)."""

from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import ttk

# Shell (tipo + ações): um pouco menor. Painel de controles: um pouco maior que 10 pt base.
EFM_UI_FONT_PT = 10
EFM_UI_FONT_SHELL_PT = 10
EFM_UI_FONT_PANEL_PT = 11
EFM_UI_FONT_PANEL_HINT_PT = 10
EFM_UI_FONT_HINT_PT = 9
EFM_UI_FONT = ("Segoe UI", EFM_UI_FONT_PT)
EFM_UI_FONT_SHELL = ("Segoe UI", EFM_UI_FONT_SHELL_PT)
EFM_UI_FONT_PANEL = ("Segoe UI", EFM_UI_FONT_PANEL_PT)
EFM_UI_FONT_PANEL_HINT = ("Segoe UI", EFM_UI_FONT_PANEL_HINT_PT)
EFM_UI_FONT_HINT = ("Segoe UI", EFM_UI_FONT_HINT_PT)

EFM_COLOR_PRIMARY = "#7c1229"
EFM_COLOR_PRIMARY_HOVER = "#5b0717"
EFM_COLOR_ACTIONS_BG = "#f7eef1"
EFM_SHELL_GUTTER = 6


def configure_shell_style(root: tk.Misc) -> ttk.Style:
    style = ttk.Style(root)
    font = ("Segoe UI", EFM_UI_FONT_SHELL_PT)
    for name in ("EFM.Shell.TLabel", "EFM.Shell.TButton", "EFM.Shell.TLabelframe.Label"):
        style.configure(name, font=font)
    style.configure("EFM.Shell.TCombobox", font=font)
    return style


def _tk_font(font_pt: int) -> tkfont.Font:
    return tkfont.Font(root=None, family="Segoe UI", size=font_pt)


def format_rules_path_short(path: Path | None) -> str:
    if path is None:
        return "data/marker_rules.json (nao encontrado)"
    return f"data/{path.name}"


def apply_efm_ttk_theme(root: tk.Misc, font_pt: int = EFM_UI_FONT_PT) -> ttk.Style:
    style = ttk.Style(root)
    font = _tk_font(font_pt)
    tuple_font = ("Segoe UI", font_pt)

    for name in (
        ".",
        "TLabel",
        "TButton",
        "TCombobox",
        "TEntry",
        "TLabelframe",
        "TLabelframe.Label",
    ):
        style.configure(name, font=font)

    root.option_add("*TCombobox*Font", tuple_font)
    root.option_add("*TCombobox*Listbox*Font", tuple_font)
    root.option_add("*Listbox*Font", tuple_font)
    return style


def tune_combobox_font(combo: ttk.Combobox, font_pt: int = EFM_UI_FONT_PT) -> None:
    tuple_font = ("Segoe UI", font_pt)
    try:
        combo.configure(font=tuple_font)
    except tk.TclError:
        pass

    def _apply() -> None:
        for child in combo.winfo_children():
            try:
                child.configure(font=tuple_font)
            except tk.TclError:
                pass

    combo.after_idle(_apply)
