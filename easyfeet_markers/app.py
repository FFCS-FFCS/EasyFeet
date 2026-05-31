"""Janela unificada do módulo de marcadores com vínculo ao paciente."""

from __future__ import annotations

import json
import shutil
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from PIL import Image
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from easyfeet.db import SessionLocal, init_db
from easyfeet.models import Cliente, ImagemPlantar, MarcacaoPlantar, MomentoClinico
from easyfeet.paths import DATA_DIR, resolve_project_file, stored_path_for_write
from easyfeet_markers.registry import KIND_BY_ID, KIND_LABEL_TO_ID, MARKER_KINDS, help_text_for_kind
from easyfeet_markers.ui_style import (
    EFM_COLOR_ACTIONS_BG,
    EFM_COLOR_PRIMARY,
    EFM_COLOR_PRIMARY_HOVER,
    EFM_SHELL_GUTTER,
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

NOVO_MOMENTO_LABEL = "[Novo momento de hoje]"

LADO_UI_OPCOES: tuple[tuple[str, str], ...] = (
    ("Direito (D)", "direito"),
    ("Esquerdo (E)", "esquerdo"),
    ("Ambos os pes", "ambos"),
)
LADO_LABEL_BY_VALUE = {value: label for label, value in LADO_UI_OPCOES}
LADO_VALUE_BY_LABEL = {label: value for label, value in LADO_UI_OPCOES}
LADO_PROMPT_LABEL = "— indique o lado —"
LADO_COMBO_VALUES = [LADO_PROMPT_LABEL] + [label for label, _ in LADO_UI_OPCOES]
LADO_VALUES_KNOWN = frozenset(LADO_VALUE_BY_LABEL.values())


class EFMMarcadoresApp(tk.Tk):
    def __init__(
        self,
        preselected_cliente_id: int | None = None,
        preselected_momento_id: int | None = None,
        preselected_imagem_id: int | None = None,
        preselected_kind_id: str | None = None,
    ) -> None:
        super().__init__()
        init_db()
        self._session: Session = SessionLocal()
        self.title("EasyFeet — Módulo de marcadores (EFM)")
        self.geometry("1180x820")
        self.minsize(800, 560)
        apply_efm_ttk_theme(self, EFM_UI_FONT_PT)
        configure_shell_style(self)

        self._clientes_by_label: dict[str, Cliente] = {}
        self._momentos_by_label: dict[str, MomentoClinico] = {}
        self._current_momento_id: int | None = None
        self._current_imagem_id: int | None = None
        self._current_source_path: Path | None = None
        self._imagens_by_label: dict[str, ImagemPlantar] = {}
        self._loading_imagem = False
        self._loading_lado = False
        self._preselected_cliente_id = preselected_cliente_id
        self._preselected_momento_id = preselected_momento_id
        self._preselected_imagem_id = preselected_imagem_id
        self._preselected_kind_id = preselected_kind_id
        if preselected_cliente_id is not None and preselected_momento_id is not None:
            self._context_mode = "hub"
        elif preselected_cliente_id is not None:
            self._context_mode = "cliente"
        else:
            self._context_mode = "full"

        self._var_cliente = tk.StringVar(value="Selecione paciente...")
        self._var_momento = tk.StringVar(value=NOVO_MOMENTO_LABEL)
        self._var_kind = tk.StringVar(value=MARKER_KINDS[0].label_pt)
        self._current_kind_id = MARKER_KINDS[0].id

        header = ttk.Frame(self, padding=(EFM_SHELL_GUTTER, 6, EFM_SHELL_GUTTER, 2))
        header.pack(fill="x")

        self._header_ctx = ttk.Frame(header)
        self._header_ctx.pack(fill="x")
        self._header_img = ttk.Frame(header)
        self._header_img.pack(fill="x", pady=(4, 0))

        self._lbl_paciente = ttk.Label(self._header_ctx, text="Paciente:", style="EFM.Shell.TLabel")
        self._lbl_paciente.pack(side="left", padx=(0, 4))
        self._combo_cliente = ttk.Combobox(
            self._header_ctx,
            textvariable=self._var_cliente,
            values=[],
            state="readonly",
            width=27,
            style="EFM.Shell.TCombobox",
        )
        self._combo_cliente.pack(side="left", padx=(0, 8))
        self._combo_cliente.bind("<<ComboboxSelected>>", self._on_cliente_change)
        tune_combobox_font(self._combo_cliente, EFM_UI_FONT_SHELL_PT)

        self._lbl_momento = ttk.Label(self._header_ctx, text="Momento:", style="EFM.Shell.TLabel")
        self._lbl_momento.pack(side="left", padx=(0, 4))
        self._combo_momento = ttk.Combobox(
            self._header_ctx,
            textvariable=self._var_momento,
            values=[NOVO_MOMENTO_LABEL],
            state="readonly",
            width=24,
            style="EFM.Shell.TCombobox",
        )
        self._combo_momento.pack(side="left", padx=(0, 8))
        self._combo_momento.bind("<<ComboboxSelected>>", self._on_momento_change)
        tune_combobox_font(self._combo_momento, EFM_UI_FONT_SHELL_PT)

        self._btn_novo_momento = ttk.Button(
            self._header_ctx,
            text="Novo momento",
            style="EFM.Shell.TButton",
            command=self._create_new_momento_for_selected_cliente,
        )
        self._btn_novo_momento.pack(side="left", padx=(0, 10))

        ttk.Label(self._header_ctx, text="Tipo de marcador:", style="EFM.Shell.TLabel").pack(side="left", padx=(0, 4))
        kind_combo = ttk.Combobox(
            self._header_ctx,
            textvariable=self._var_kind,
            values=[k.label_pt for k in MARKER_KINDS],
            state="readonly",
            width=26,
            style="EFM.Shell.TCombobox",
        )
        kind_combo.pack(side="left", padx=(0, 8))
        kind_combo.bind("<<ComboboxSelected>>", self._on_kind_change)
        tune_combobox_font(kind_combo, EFM_UI_FONT_SHELL_PT)

        ttk.Button(self._header_ctx, text="Ajuda", style="EFM.Shell.TButton", command=self._show_help_current).pack(
            side="left"
        )

        self._btn_carregar_imagem = ttk.Button(
            self._header_img,
            text="Carregar imagem",
            style="EFM.Shell.TButton",
            command=self._open_image_common,
        )
        self._btn_carregar_imagem.pack(side="left", padx=(0, 10))

        self._lbl_imagem = ttk.Label(self._header_img, text="Imagem:", style="EFM.Shell.TLabel")
        self._var_imagem = tk.StringVar(value="")
        self._combo_imagem = ttk.Combobox(
            self._header_img,
            textvariable=self._var_imagem,
            values=[],
            state="disabled",
            width=24,
            style="EFM.Shell.TCombobox",
        )
        self._combo_imagem.bind("<<ComboboxSelected>>", self._on_imagem_change)
        tune_combobox_font(self._combo_imagem, EFM_UI_FONT_SHELL_PT)

        self._lbl_lado = ttk.Label(self._header_img, text="Lado:", style="EFM.Shell.TLabel")
        self._var_lado = tk.StringVar(value="")
        self._combo_lado = ttk.Combobox(
            self._header_img,
            textvariable=self._var_lado,
            values=LADO_COMBO_VALUES,
            state="disabled",
            width=18,
            style="EFM.Shell.TCombobox",
        )
        self._combo_lado.bind("<<ComboboxSelected>>", self._on_lado_change)
        tune_combobox_font(self._combo_lado, EFM_UI_FONT_SHELL_PT)

        self._btn_excluir_imagem = ttk.Button(
            self._header_img,
            text="Excluir imagem",
            style="EFM.Shell.TButton",
            command=self._delete_current_imagem,
        )

        self._context_bar = ttk.Frame(self, padding=(EFM_SHELL_GUTTER, 4, EFM_SHELL_GUTTER, 2))
        self._context_label = ttk.Label(
            self._context_bar,
            text="",
            style="EFM.Shell.TLabel",
            wraplength=900,
        )
        self._context_label.pack(side="left", fill="x", expand=True)

        self._actions_frame = tk.Frame(self, bg=EFM_COLOR_ACTIONS_BG, pady=8)
        self._actions_frame.pack(fill="x", pady=(2, 4))
        tk.Label(
            self._actions_frame,
            text="Ações",
            bg=EFM_COLOR_ACTIONS_BG,
            fg=EFM_COLOR_PRIMARY,
            font=("Segoe UI", EFM_UI_FONT_SHELL_PT, "bold"),
        ).pack(anchor="w", padx=EFM_SHELL_GUTTER, pady=(0, 6))
        actions_row = tk.Frame(self._actions_frame, bg=EFM_COLOR_ACTIONS_BG)
        actions_row.pack(fill="x", anchor="w", padx=EFM_SHELL_GUTTER)

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
        self._btn_clear_all.pack(side="left", padx=(0, 4))
        self._btn_save_patient = tk.Button(
            actions_row,
            text="Salvar no paciente",
            font=("Segoe UI", EFM_UI_FONT_SHELL_PT),
            bg=EFM_COLOR_PRIMARY,
            fg="#ffffff",
            activebackground=EFM_COLOR_PRIMARY_HOVER,
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=3,
            cursor="hand2",
            command=self._action_save_to_patient,
        )
        self._btn_save_patient.pack(side="left", padx=(4, 0))

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
        self._load_clientes()
        self._apply_open_context()
        self._apply_context_mode_ui()
        self._refresh_action_bar()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self) -> None:
        self._session.close()
        self.destroy()

    def _query(self, stmt: Select[tuple[object]]) -> list[object]:
        return list(self._session.scalars(stmt))

    def _load_clientes(self) -> None:
        clientes = self._query(select(Cliente).order_by(Cliente.nome.asc()))
        self._clientes_by_label.clear()
        labels: list[str] = []
        for c in clientes:
            if not isinstance(c, Cliente):
                continue
            label = f"#{c.id} - {c.nome}"
            self._clientes_by_label[label] = c
            labels.append(label)
        if not labels:
            self._combo_cliente.configure(values=["Sem pacientes"])
            self._var_cliente.set("Sem pacientes")
            self._combo_momento.configure(values=[NOVO_MOMENTO_LABEL])
            self._var_momento.set(NOVO_MOMENTO_LABEL)
            return
        self._combo_cliente.configure(values=labels)
        selected_label: str | None = None
        if self._preselected_cliente_id is not None:
            for label, cli in self._clientes_by_label.items():
                if cli.id == self._preselected_cliente_id:
                    selected_label = label
                    break
        if selected_label is not None:
            self._var_cliente.set(selected_label)
            self._preselected_cliente_id = None
        elif self._var_cliente.get() not in self._clientes_by_label:
            self._var_cliente.set(labels[0])
        self._refresh_momentos_combo()

    def _selected_cliente(self) -> Cliente | None:
        return self._clientes_by_label.get(self._var_cliente.get())

    def _selected_momento(self) -> MomentoClinico | None:
        return self._momentos_by_label.get(self._var_momento.get())

    @staticmethod
    def _format_lado_label(lado: str) -> str:
        labels = {
            "direito": "Direito (D)",
            "esquerdo": "Esquerdo (E)",
            "ambos": "Ambos os pes",
            "nao_informado": "Nao informado",
        }
        return labels.get(lado, lado.replace("_", " ").title())

    def _context_summary_text(self) -> str:
        cliente = self._selected_cliente()
        if cliente is None:
            return "Plantigrafo — Analise"
        stamp = ""
        if self._context_mode == "hub":
            mom = self._selected_momento()
            if mom is not None:
                rotulo = (mom.rotulo or "").strip() or "Momento"
                stamp = f" · {mom.data_referencia.strftime('%d/%m/%Y %H:%M')} — {rotulo}"
        elif self._current_momento_id is not None:
            mom = self._selected_momento()
            if mom is not None:
                rotulo = (mom.rotulo or "").strip() or "Momento"
                stamp = f" · {mom.data_referencia.strftime('%d/%m/%Y %H:%M')} — {rotulo}"
        img_note = ""
        if self._current_imagem_id is not None:
            img = self._session.get(ImagemPlantar, self._current_imagem_id)
            if img is not None:
                img_note = f" · Imagem #{img.id} ({self._format_lado_label(img.lado)})"
        return f"Plantigrafo — Analise · {cliente.nome}{stamp}{img_note}"

    def _apply_context_mode_ui(self) -> None:
        if self._context_mode == "hub":
            for w in (self._lbl_paciente, self._combo_cliente, self._lbl_momento, self._combo_momento, self._btn_novo_momento):
                w.pack_forget()
            self._context_bar.pack(fill="x", before=self._actions_frame)
            self._context_label.configure(text=self._context_summary_text())
        elif self._context_mode == "cliente":
            self._lbl_paciente.pack_forget()
            self._combo_cliente.pack_forget()
            self._context_bar.pack(fill="x", before=self._actions_frame)
            self._context_label.configure(text=self._context_summary_text())
        else:
            self._context_bar.pack_forget()

    def _refresh_context_banner(self) -> None:
        if self._context_mode in ("hub", "cliente"):
            self._context_label.configure(text=self._context_summary_text())

    def _sync_lado_combo(self) -> None:
        if self._current_imagem_id is None:
            self._lbl_lado.pack_forget()
            self._combo_lado.pack_forget()
            self._combo_lado.configure(state="disabled")
            self._var_lado.set("")
            self._sync_imagem_actions()
            return
        img = self._session.get(ImagemPlantar, self._current_imagem_id)
        if img is None:
            self._lbl_lado.pack_forget()
            self._combo_lado.pack_forget()
            self._combo_lado.configure(state="disabled")
            self._var_lado.set("")
            self._sync_imagem_actions()
            return
        lado = (img.lado or "nao_informado").strip()
        if lado in LADO_VALUES_KNOWN:
            label = LADO_LABEL_BY_VALUE[lado]
        else:
            label = LADO_PROMPT_LABEL
        self._loading_lado = True
        self._var_lado.set(label)
        self._loading_lado = False
        self._lbl_lado.pack(side="left", padx=(8, 4))
        self._combo_lado.configure(state="readonly")
        self._combo_lado.pack(side="left", padx=(0, 8))
        self._sync_imagem_actions()

    def _sync_imagem_actions(self) -> None:
        if self._current_imagem_id is None:
            self._btn_excluir_imagem.pack_forget()
        else:
            self._btn_excluir_imagem.pack(side="left", padx=(0, 4))

    def _delete_current_imagem(self) -> None:
        if self._current_imagem_id is None:
            messagebox.showinfo("Marcadores", "Nenhuma imagem aberta para excluir.", parent=self)
            return
        img_id = self._current_imagem_id
        img = self._session.get(ImagemPlantar, img_id)
        if img is None:
            return
        rotulo = self._imagem_combo_label(img)
        if not messagebox.askyesno(
            "Excluir imagem",
            f"Remover {rotulo}?\n\n"
            "Apaga a foto e todas as marcacoes (linhas e pontos) desta imagem.\n"
            "Esta acao nao pode ser desfeita.",
            parent=self,
        ):
            return
        cliente = self._selected_cliente()
        momento_id = self._current_momento_id
        for marc in self._session.scalars(
            select(MarcacaoPlantar).where(MarcacaoPlantar.imagem_id == img_id)
        ):
            self._session.delete(marc)
        if cliente is not None and momento_id is not None:
            pasta = DATA_DIR / "pacientes" / str(cliente.id) / "momentos" / str(momento_id) / "imagens" / str(img_id)
            if pasta.is_dir():
                try:
                    shutil.rmtree(pasta)
                except OSError:
                    pass
        self._session.delete(img)
        self._session.commit()
        self._current_imagem_id = None
        self._current_source_path = None
        self._load_latest_or_requested_image_for_current_momento()
        messagebox.showinfo("Marcadores", "Imagem excluida.", parent=self)

    def _on_lado_change(self, _event: object | None = None) -> None:
        if self._loading_lado:
            return
        if self._current_imagem_id is None:
            return
        img = self._session.get(ImagemPlantar, self._current_imagem_id)
        if img is None:
            return
        label = self._var_lado.get().strip()
        novo_lado = LADO_VALUE_BY_LABEL.get(label)
        if not novo_lado or novo_lado == img.lado:
            return
        img.lado = novo_lado
        self._session.commit()
        self._refresh_imagens_combo(select_id=img.id)
        self._refresh_context_banner()

    def _imagem_combo_label(self, img: ImagemPlantar) -> str:
        return f"#{img.id} — {self._format_lado_label(img.lado)}"

    def _refresh_imagens_combo(self, *, select_id: int | None = None) -> None:
        momento_id = self._current_momento_id
        self._imagens_by_label.clear()
        labels: list[str] = []
        if momento_id is not None:
            imagens = self._query(
                select(ImagemPlantar)
                .where(ImagemPlantar.momento_id == momento_id)
                .order_by(ImagemPlantar.id.asc())
            )
            for img in imagens:
                if not isinstance(img, ImagemPlantar):
                    continue
                label = self._imagem_combo_label(img)
                self._imagens_by_label[label] = img
                labels.append(label)
        if not labels:
            self._lbl_imagem.pack_forget()
            self._combo_imagem.pack_forget()
            self._combo_imagem.configure(values=[], state="disabled")
            self._var_imagem.set("")
            return
        self._combo_imagem.configure(values=labels, state="readonly")
        pick_id = select_id if select_id is not None else self._current_imagem_id
        selected_label = labels[-1]
        if pick_id is not None:
            for label, img in self._imagens_by_label.items():
                if img.id == pick_id:
                    selected_label = label
                    break
        self._loading_imagem = True
        self._var_imagem.set(selected_label)
        self._loading_imagem = False
        self._lbl_imagem.pack(side="left", padx=(0, 4))
        self._combo_imagem.pack(side="left", padx=(0, 10))

    def _on_imagem_change(self, _event: object | None = None) -> None:
        if self._loading_imagem:
            return
        img = self._imagens_by_label.get(self._var_imagem.get())
        if img is None:
            return
        if img.id == self._current_imagem_id:
            return
        self._load_imagem_by_id(img.id)

    def _load_imagem_by_id(self, imagem_id: int) -> None:
        img = self._session.get(ImagemPlantar, imagem_id)
        if img is None:
            return
        if self._current_momento_id is not None and img.momento_id != self._current_momento_id:
            return
        resolved = resolve_project_file(img.path_original)
        if resolved is None:
            messagebox.showwarning(
                "Marcadores",
                f"Imagem #{imagem_id} nao encontrada no disco.",
                parent=self,
            )
            return
        self._current_imagem_id = img.id
        self._current_source_path = resolved
        for panel in (self._panel_plantar, self._panel_pontos):
            panel.load_image(resolved)
        self._try_load_existing_marcacao(self._current_kind_id)
        self._sync_lado_combo()
        self._refresh_imagens_combo(select_id=img.id)
        self._refresh_context_banner()

    def _ask_lado_imagem(self, *, default: str = "direito") -> str | None:
        dlg = tk.Toplevel(self)
        dlg.title("Lado da imagem")
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)
        frm = ttk.Frame(dlg, padding=12)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Qual pe aparece nesta foto?").pack(anchor="w", pady=(0, 8))
        var = tk.StringVar(value=default if default in LADO_VALUE_BY_LABEL.values() else "direito")
        for label, value in LADO_UI_OPCOES:
            ttk.Radiobutton(frm, text=label, variable=var, value=value).pack(anchor="w", pady=2)
        result: list[str | None] = [None]

        def ok() -> None:
            result[0] = var.get()
            dlg.destroy()

        def cancel() -> None:
            dlg.destroy()

        row = ttk.Frame(frm)
        row.pack(fill="x", pady=(14, 0))
        ttk.Button(row, text="Continuar", command=ok).pack(side="right")
        ttk.Button(row, text="Cancelar", command=cancel).pack(side="right", padx=(0, 8))
        dlg.protocol("WM_DELETE_WINDOW", cancel)
        dlg.bind("<Return>", lambda _e: ok())
        dlg.bind("<Escape>", lambda _e: cancel())
        dlg.update_idletasks()
        req_w = max(300, int(dlg.winfo_reqwidth()))
        req_h = max(220, int(dlg.winfo_reqheight())) + 16
        px = max(0, self.winfo_x() + (self.winfo_width() - req_w) // 2)
        py = max(0, self.winfo_y() + (self.winfo_height() - req_h) // 2)
        dlg.geometry(f"{req_w}x{req_h}+{px}+{py}")
        self.wait_window(dlg)
        return result[0]

    def _refresh_momentos_combo(self) -> None:
        cliente = self._selected_cliente()
        self._momentos_by_label.clear()
        labels = [NOVO_MOMENTO_LABEL]
        if cliente is not None:
            momentos = self._query(
                select(MomentoClinico)
                .where(MomentoClinico.cliente_id == cliente.id)
                .order_by(MomentoClinico.data_referencia.desc(), MomentoClinico.id.desc())
            )
            for m in momentos:
                if not isinstance(m, MomentoClinico):
                    continue
                stamp = m.data_referencia.strftime("%d/%m/%Y %H:%M")
                rotulo = (m.rotulo or "").strip() or "Momento"
                label = f"{stamp} - {rotulo} (#{m.id})"
                self._momentos_by_label[label] = m
                labels.append(label)
        self._combo_momento.configure(values=labels)
        if self._preselected_momento_id is not None:
            for label, mom in self._momentos_by_label.items():
                if mom.id == self._preselected_momento_id:
                    self._var_momento.set(label)
                    self._preselected_momento_id = None
                    break
        if self._var_momento.get() not in labels:
            self._var_momento.set(NOVO_MOMENTO_LABEL)
        self._on_momento_change()
        self._refresh_context_banner()

    def _clear_workspace_image(self) -> None:
        for panel in (self._panel_plantar, self._panel_pontos):
            clear_fn = getattr(panel, "clear_image", None)
            if callable(clear_fn):
                clear_fn()
        self._sync_lado_combo()

    def _on_cliente_change(self, _event: object | None = None) -> None:
        self._current_momento_id = None
        self._current_imagem_id = None
        self._current_source_path = None
        self._clear_workspace_image()
        self._refresh_momentos_combo()

    def _on_momento_change(self, _event: object | None = None) -> None:
        m = self._momentos_by_label.get(self._var_momento.get())
        self._current_momento_id = m.id if m is not None else None
        self._current_imagem_id = None
        self._current_source_path = None
        if self._current_momento_id is None:
            self._clear_workspace_image()
            return
        self._load_latest_or_requested_image_for_current_momento()

    def _load_latest_or_requested_image_for_current_momento(self) -> None:
        momento_id = self._current_momento_id
        if momento_id is None:
            self._refresh_imagens_combo()
            self._clear_workspace_image()
            return
        pick_id: int | None = None
        if self._preselected_imagem_id is not None:
            maybe = self._session.get(ImagemPlantar, self._preselected_imagem_id)
            if maybe is not None and maybe.momento_id == momento_id:
                pick_id = maybe.id
            self._preselected_imagem_id = None
        self._refresh_imagens_combo(select_id=pick_id)
        if not self._imagens_by_label:
            self._clear_workspace_image()
            return
        if pick_id is None:
            pick_id = int(list(self._imagens_by_label.values())[-1].id)
        self._load_imagem_by_id(pick_id)

    def _apply_open_context(self) -> None:
        kind_id = (self._preselected_kind_id or "").strip()
        if kind_id in self._panels_by_kind and kind_id != self._current_kind_id:
            self._current_kind_id = kind_id
            self._var_kind.set(KIND_BY_ID[kind_id].label_pt)
            for p in self._panels_by_kind.values():
                p.pack_forget()
            self._panels_by_kind[kind_id].pack(fill="both", expand=True)

    def _create_new_momento_for_selected_cliente(self) -> None:
        cliente = self._selected_cliente()
        if cliente is None:
            messagebox.showwarning("Marcadores", "Selecione um paciente.", parent=self)
            return
        now = datetime.now()
        momento = MomentoClinico(
            cliente_id=cliente.id,
            data_referencia=now,
            rotulo=f"Momento {now.strftime('%d/%m/%Y %H:%M')}",
        )
        self._session.add(momento)
        self._session.commit()
        self._refresh_momentos_combo()
        # Seleciona o novo momento criado.
        for label, item in self._momentos_by_label.items():
            if item.id == momento.id:
                self._var_momento.set(label)
                self._current_momento_id = item.id
                break

    def _ensure_momento(self) -> int | None:
        if self._current_momento_id is not None:
            return self._current_momento_id
        self._create_new_momento_for_selected_cliente()
        return self._current_momento_id

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
        cliente = self._selected_cliente()
        if cliente is None:
            messagebox.showwarning("Marcadores", "Selecione um paciente antes de carregar imagem.", parent=self)
            return
        momento_id = self._ensure_momento()
        if momento_id is None:
            return

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
        lado = self._ask_lado_imagem()
        if lado is None:
            return
        try:
            p = Path(path).resolve()
            width = 0
            height = 0
            try:
                with Image.open(p) as src:
                    width, height = src.size
            except OSError:
                pass

            imagem = ImagemPlantar(
                momento_id=momento_id,
                lado=lado,
                nome_arquivo=p.name,
                path_original="",
                largura=width,
                altura=height,
            )
            self._session.add(imagem)
            self._session.commit()
            self._session.refresh(imagem)

            dest_dir = DATA_DIR / "pacientes" / str(cliente.id) / "momentos" / str(momento_id) / "imagens" / str(imagem.id)
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_original = dest_dir / f"original{p.suffix.lower()}"
            shutil.copy2(p, dest_original)
            imagem.path_original = stored_path_for_write(dest_original)
            self._session.commit()

            self._current_imagem_id = imagem.id
            self._current_source_path = dest_original
            load_im(dest_original)
            self._try_load_existing_marcacao(self._current_kind_id)
            self._refresh_imagens_combo(select_id=imagem.id)
            self._sync_lado_combo()
            self._refresh_context_banner()
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
        self._try_load_existing_marcacao(kind_id)
        self._refresh_action_bar()

    def _try_load_existing_marcacao(self, kind_id: str) -> None:
        if self._current_imagem_id is None:
            return
        panel = self._active_panel()
        if panel is None:
            return
        marc = self._session.scalar(
            select(MarcacaoPlantar).where(
                MarcacaoPlantar.imagem_id == self._current_imagem_id,
                MarcacaoPlantar.tipo_marcador == kind_id,
            )
        )
        if marc is None:
            # Sem marcação para este tipo nesta imagem.
            if kind_id == "plantar_linhas" and hasattr(panel, "set_lines_data"):
                panel.set_lines_data({})  # type: ignore[attr-defined]
            if kind_id == "plantar_pontos" and hasattr(panel, "set_points_data"):
                panel.set_points_data({})  # type: ignore[attr-defined]
            return
        json_path = resolve_project_file(marc.path_json)
        if json_path is None:
            return
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        markers = payload.get("markers", [])
        if kind_id == "plantar_linhas" and hasattr(panel, "set_lines_data"):
            lines: dict[str, tuple[tuple[float, float], tuple[float, float]]] = {}
            for m in markers:
                mid = str(m.get("id", "")).strip()
                pts = m.get("points") or []
                if not mid or len(pts) < 2:
                    continue
                p1 = pts[0]
                p2 = pts[1]
                if not isinstance(p1, list) or not isinstance(p2, list) or len(p1) < 2 or len(p2) < 2:
                    continue
                lines[mid] = ((float(p1[0]), float(p1[1])), (float(p2[0]), float(p2[1])))
            panel.set_lines_data(lines)  # type: ignore[attr-defined]
        elif kind_id == "plantar_pontos" and hasattr(panel, "set_points_data"):
            points: dict[str, tuple[float, float]] = {}
            for m in markers:
                mid = str(m.get("id", "")).strip()
                pts = m.get("points") or []
                if not mid or not pts:
                    continue
                p0 = pts[0]
                if not isinstance(p0, list) or len(p0) < 2:
                    continue
                points[mid] = (float(p0[0]), float(p0[1]))
            panel.set_points_data(points)  # type: ignore[attr-defined]

    def _action_save_to_patient(self) -> None:
        cliente = self._selected_cliente()
        if cliente is None:
            messagebox.showwarning("Marcadores", "Selecione um paciente.", parent=self)
            return
        if self._current_imagem_id is None:
            messagebox.showwarning("Marcadores", "Abra uma imagem para salvar a marcação.", parent=self)
            return
        panel = self._active_panel()
        if panel is None:
            return

        momento_id = self._current_momento_id
        if momento_id is None:
            messagebox.showwarning("Marcadores", "Selecione ou crie um momento clínico.", parent=self)
            return

        out_dir = DATA_DIR / "pacientes" / str(cliente.id) / "momentos" / str(momento_id) / "imagens" / str(self._current_imagem_id)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_png = out_dir / f"marcado_{self._current_kind_id}.png"
        out_json = out_dir / f"anotacao_{self._current_kind_id}.json"

        try:
            export_to = getattr(panel, "export_to", None)
            if not callable(export_to):
                messagebox.showerror("Marcadores", "Painel atual não suporta exportação programática.", parent=self)
                return
            export_to(out_png, out_json)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Marcadores", str(exc), parent=self)
            return

        marc = self._session.scalar(
            select(MarcacaoPlantar).where(
                MarcacaoPlantar.imagem_id == self._current_imagem_id,
                MarcacaoPlantar.tipo_marcador == self._current_kind_id,
            )
        )
        path_json = stored_path_for_write(out_json)
        path_png = stored_path_for_write(out_png)
        if marc is None:
            marc = MarcacaoPlantar(
                imagem_id=self._current_imagem_id,
                tipo_marcador=self._current_kind_id,
                path_json=path_json,
                path_png_marcado=path_png,
            )
            self._session.add(marc)
        else:
            marc.path_json = path_json
            marc.path_png_marcado = path_png
        self._session.commit()
        messagebox.showinfo(
            "Marcadores",
            f"Marcacao salva no paciente #{cliente.id} ({cliente.nome}).",
            parent=self,
        )

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
        hint = (
            "Ajuda textual: «Linhas» — marcador_plantar/help_plantar_pt.txt; "
            "«Pontos» — marcador_pontos/help_pontos_pt.txt (editáveis)"
        )
        if kind_id == "plantar_linhas":
            hint = "Edite marcador_plantar/help_plantar_pt.txt para alterar este texto."
        elif kind_id == "plantar_pontos":
            hint = "Edite marcador_pontos/help_pontos_pt.txt para alterar este texto."
        ttk.Label(row, text=hint, wraplength=640).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Fechar", command=win.destroy).pack(side="right", padx=(8, 0))


def _parse_int_arg(argv: list[str], name: str) -> int | None:
    for i, arg in enumerate(argv):
        if arg == f"--{name}" and i + 1 < len(argv):
            raw = argv[i + 1].strip()
            if raw.isdigit():
                return int(raw)
        if arg.startswith(f"--{name}="):
            raw = arg.split("=", 1)[1].strip()
            if raw.isdigit():
                return int(raw)
    return None


def main() -> None:
    argv = sys.argv[1:]
    preselected_id = _parse_int_arg(argv, "cliente-id")
    preselected_momento_id = _parse_int_arg(argv, "momento-id")
    preselected_imagem_id = _parse_int_arg(argv, "imagem-id")
    preselected_kind_id: str | None = None
    for i, arg in enumerate(argv):
        if arg == "--tipo" and i + 1 < len(argv):
            preselected_kind_id = argv[i + 1].strip()
            break
        if arg.startswith("--tipo="):
            preselected_kind_id = arg.split("=", 1)[1].strip()
            break
    app = EFMMarcadoresApp(
        preselected_cliente_id=preselected_id,
        preselected_momento_id=preselected_momento_id,
        preselected_imagem_id=preselected_imagem_id,
        preselected_kind_id=preselected_kind_id,
    )
    app.mainloop()


if __name__ == "__main__":
    main()
