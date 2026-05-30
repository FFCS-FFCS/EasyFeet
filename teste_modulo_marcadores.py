"""
Protótipo EFM — barra de ações centralizada (Exportar / Gerar / Sugerir / Limpar).

Uso: duplo clique em EF_teste_modulo.bat (pasta oficial OneDrive).
O EFM principal (EFM_Marcadores.py) mantém os botões em cada painel até integração.
"""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from easyfeet_markers.registry import KIND_BY_ID, KIND_LABEL_TO_ID, MARKER_KINDS, help_text_for_kind
from easyfeet_markers.ui_style import (
    EFM_UI_FONT,
    EFM_UI_FONT_PANEL_HINT_PT,
    EFM_UI_FONT_PANEL_PT,
    EFM_UI_FONT_PT,
    EFM_UI_FONT_SHELL_PT,
    apply_efm_ttk_theme,
    configure_shell_style,
    tune_combobox_font,
)
from marcador_plantar.app_tk import PlantarLinhasPanel
from marcador_pontos.app_tk import PontosReferenciasPanel


class EFMMarcadoresTesteApp(tk.Tk):
    """Shell EFM com Exportar / Gerar / Sugerir / Limpar no topo (fora dos painéis)."""

    def __init__(self) -> None:
        super().__init__()
        self.title("EasyFeet — Teste módulo marcadores (barra central)")
        self.geometry("1180x820")
        self.minsize(800, 560)
        apply_efm_ttk_theme(self, EFM_UI_FONT_PT)
        configure_shell_style(self)

        self._var_kind = tk.StringVar(value=MARKER_KINDS[0].label_pt)
        self._current_kind_id = MARKER_KINDS[0].id

        header = ttk.Frame(self, padding=(6, 6, 6, 2))
        header.pack(fill="x")

        ttk.Label(header, text="Tipo de marcador:", style="EFM.Shell.TLabel").pack(side="left", padx=(0, 4))
        kind_combo = ttk.Combobox(
            header,
            textvariable=self._var_kind,
            values=[k.label_pt for k in MARKER_KINDS],
            state="readonly",
            width=34,
            style="EFM.Shell.TCombobox",
        )
        kind_combo.pack(side="left", padx=(0, 8))
        kind_combo.bind("<<ComboboxSelected>>", self._on_kind_change)
        tune_combobox_font(kind_combo, EFM_UI_FONT_SHELL_PT)

        ttk.Button(
            header,
            text="Abrir imagem...",
            style="EFM.Shell.TButton",
            command=self._open_image_common,
        ).pack(side="left", padx=(0, 4))
        ttk.Button(header, text="Ajuda", style="EFM.Shell.TButton", command=self._show_help_current).pack(side="left")

        actions = ttk.LabelFrame(self, text="Ações", padding=(3, 6, 3, 6))
        actions.pack(fill="x", padx=6, pady=(2, 4))
        try:
            ttk.Style(self).configure("EFM.Shell.TLabelframe.Label", font=("Segoe UI", EFM_UI_FONT_SHELL_PT))
        except tk.TclError:
            pass
        actions_row = ttk.Frame(actions)
        actions_row.pack(anchor="center")

        self._btn_export = ttk.Button(
            actions_row,
            text="Exportar PNG + JSON...",
            style="EFM.Shell.TButton",
            command=self._action_export,
        )
        self._btn_export.pack(side="left", padx=(0, 4))

        self._btn_generate = ttk.Button(
            actions_row,
            text="Gerar (heurística A–D)",
            style="EFM.Shell.TButton",
            command=self._action_generate,
        )
        self._btn_generate.pack(side="left", padx=(0, 4))

        self._btn_suggest = ttk.Button(
            actions_row,
            text="Sugerir",
            style="EFM.Shell.TButton",
            command=self._action_suggest,
        )
        self._btn_suggest.pack(side="left", padx=(0, 4))

        self._btn_clear_one = ttk.Button(
            actions_row,
            text="Limpar selecionado",
            style="EFM.Shell.TButton",
            command=self._action_clear_current,
        )
        self._btn_clear_one.pack(side="left", padx=(0, 4))

        self._btn_clear_all = ttk.Button(
            actions_row,
            text="Limpar todos",
            style="EFM.Shell.TButton",
            command=self._action_clear_all,
        )
        self._btn_clear_all.pack(side="left")

        self._container = ttk.Frame(self)
        self._container.pack(fill="both", expand=True)

        self._panel_plantar = PlantarLinhasPanel(
            self._container,
            show_action_toolbar=False,
            ui_font_pt=EFM_UI_FONT_PANEL_PT,
            ui_font_hint_pt=EFM_UI_FONT_PANEL_HINT_PT,
            compact_ui=True,
        )
        self._panel_pontos = PontosReferenciasPanel(
            self._container,
            show_action_toolbar=False,
            ui_font_pt=EFM_UI_FONT_PANEL_PT,
            ui_font_hint_pt=EFM_UI_FONT_PANEL_HINT_PT,
            compact_ui=True,
        )
        self._panels_by_kind: dict[str, ttk.Frame] = {
            "plantar_linhas": self._panel_plantar,
            "plantar_pontos": self._panel_pontos,
        }

        self._panel_plantar.pack(fill="both", expand=True)
        self._refresh_action_bar()

    def _active_panel(self) -> PlantarLinhasPanel | PontosReferenciasPanel | None:
        panel = self._panels_by_kind.get(self._current_kind_id)
        return panel  # type: ignore[return-value]

    def _refresh_action_bar(self) -> None:
        is_linhas = self._current_kind_id == "plantar_linhas"
        if is_linhas:
            self._btn_generate.configure(state="normal")
            self._btn_suggest.configure(text="Sugerir (regra)")
            self._btn_clear_one.configure(text="Limpar linha selecionada")
            self._btn_clear_all.configure(text="Limpar todas as linhas")
        else:
            self._btn_generate.configure(state="disabled")
            self._btn_suggest.configure(text="Sugerir pontos")
            self._btn_clear_one.configure(text="Limpar ponto selecionado")
            self._btn_clear_all.configure(text="Limpar todos os pontos")

    def _dispatch(self, method: str) -> None:
        panel = self._active_panel()
        if panel is None:
            return
        fn = getattr(panel, method, None)
        if callable(fn):
            fn()

    def _action_export(self) -> None:
        self._dispatch("toolbar_export")

    def _action_generate(self) -> None:
        if self._current_kind_id != "plantar_linhas":
            return
        self._dispatch("toolbar_generate")

    def _action_suggest(self) -> None:
        self._dispatch("toolbar_suggest")

    def _action_clear_current(self) -> None:
        self._dispatch("toolbar_clear_current")

    def _action_clear_all(self) -> None:
        self._dispatch("toolbar_clear_all")

    def _open_image_common(self) -> None:
        panel = self._active_panel()
        if panel is None:
            return
        load_im = getattr(panel, "load_image", None)
        if not callable(load_im):
            return
        path = filedialog.askopenfilename(
            title="Imagem plantar",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp *.bmp"), ("Todos", "*.*")],
        )
        if not path:
            return
        try:
            p = Path(path)
            load_im(p)
        except OSError:
            messagebox.showerror("Marcadores", "Nao foi possivel abrir a imagem.")

    def _sync_target_image(self, target_kind_id: str) -> None:
        target_panel = self._panels_by_kind.get(target_kind_id)
        if target_panel is None:
            return
        get_sp = getattr(target_panel, "get_source_path", None)
        load_im = getattr(target_panel, "load_image", None)
        if not callable(get_sp) or not callable(load_im):
            return
        target_path = get_sp()
        other_path: Path | None = None
        for kind_id, panel in self._panels_by_kind.items():
            if kind_id == target_kind_id:
                continue
            other_get = getattr(panel, "get_source_path", None)
            if callable(other_get):
                p = other_get()
                if p is not None:
                    other_path = p
                    break
        if other_path is None:
            return
        if target_path != other_path:
            load_im(other_path)

    def _on_kind_change(self, _event: object | None = None) -> None:
        label = self._var_kind.get()
        kind_id = KIND_LABEL_TO_ID.get(label)
        if not kind_id or kind_id == self._current_kind_id:
            return
        if kind_id not in self._panels_by_kind:
            messagebox.showinfo(
                "Marcadores",
                "Este tipo de marcador ainda não está disponível nesta versão.",
                parent=self,
            )
            self._var_kind.set(KIND_BY_ID[self._current_kind_id].label_pt)
            return
        for p in self._panels_by_kind.values():
            p.pack_forget()
        self._current_kind_id = kind_id
        self._sync_target_image(kind_id)
        self._panels_by_kind[kind_id].pack(fill="both", expand=True)
        self._refresh_action_bar()

    def _show_help_current(self) -> None:
        kind_id = KIND_LABEL_TO_ID.get(self._var_kind.get(), MARKER_KINDS[0].id)
        title = KIND_BY_ID.get(kind_id, MARKER_KINDS[0]).label_pt

        win = tk.Toplevel(self)
        win.title(f"Ajuda — {title}")
        win.transient(self)
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        w = min(980, max(620, sw - 80))
        h = min(740, max(520, sh - 120))
        win.minsize(w, h)
        frm = ttk.Frame(win, padding=12)
        frm.pack(fill="both", expand=True)
        st = scrolledtext.ScrolledText(
            frm,
            wrap="word",
            width=96,
            height=34,
            font=EFM_UI_FONT,
            relief="flat",
            padx=4,
            pady=4,
        )
        st.pack(fill="both", expand=True)
        st.insert("1.0", help_text_for_kind(kind_id))
        st.configure(state="disabled")
        row = ttk.Frame(frm)
        row.pack(fill="x", pady=(10, 0))
        hint = "Protótipo: ações centralizadas no topo (Exportar / Gerar / Sugerir / Limpar)."
        if kind_id == "plantar_linhas":
            hint = "Edite marcador_plantar/help_plantar_pt.txt para alterar este texto."
        elif kind_id == "plantar_pontos":
            hint = "Edite marcador_pontos/help_pontos_pt.txt para alterar este texto."
        ttk.Label(row, text=hint, wraplength=640).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Fechar", command=win.destroy).pack(side="right", padx=(8, 0))


def main() -> None:
    app = EFMMarcadoresTesteApp()
    app.mainloop()


if __name__ == "__main__":
    main()
