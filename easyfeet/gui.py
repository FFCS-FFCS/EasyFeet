from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
from PIL import Image

from easyfeet.marker_rules_store import (
    PROTOCOLO_VERSAO_ATUAL,
    MarkerRule,
    MarkerRuleStore,
    SEED_ROLE_ABCD_REFERENCE,
    SEED_ROLE_ABCD_USER_COPY,
    SEED_ROLE_POINTS_REFERENCE,
    SEED_ROLE_POINTS_USER_COPY,
    default_rotulos,
    required_item_count,
)
from easyfeet.navigation import (
    collect_nav_module_ids_for_role,
    find_menu_item_path,
    get_visible_child_menu_items,
    get_visible_menu_for_role,
    load_menu_config,
)
from easyfeet.cliente_dados_corporais import (
    FAIXAS_IMC_ADULTO,
    LATERALIDADE_OPCOES,
    calcular_imc,
    classificar_imc,
    formatar_altura,
    formatar_imc,
    formatar_peso,
    imc_preview,
    imc_valor_numerico,
)
from easyfeet.dashboard_ui import render_dashboard
from easyfeet.paths import resolve_project_file
from easyfeet.paciente_cadastro_pdf import (
    export_ficha_cadastro_paciente_pdf_branco,
    export_ficha_cadastro_paciente_pdf_preenchida,
)
from easyfeet.podoscopio_pdf import export_ficha_podoscopio_pdf_branco, export_ficha_podoscopio_pdf_preenchida
from easyfeet.services import EasyFeetService, MOMENTO_OBSERVACOES_MAX, MOMENTO_ROTULO_MAX
from easyfeet.version import format_app_version

# Tamanho unico de texto na interface (alinha formulario, cabecalho e tabela).
UI_FONT_PT = 15
IMC_MODAL_FONT_PT = 13
TREE_ROW_HEIGHT = 30

SPI_GETWORKAREA = 0x0030
RESTORE_WIDTH = 1220
RESTORE_HEIGHT = 760


def _windows_work_area_geometry() -> tuple[int, int, int, int] | None:
    """Retangulo da area util primaria (sem barra de tarefas). Funciona em qualquer Windows."""
    try:
        import ctypes
        from ctypes import wintypes
    except ImportError:
        return None

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", wintypes.LONG),
            ("top", wintypes.LONG),
            ("right", wintypes.LONG),
            ("bottom", wintypes.LONG),
        ]

    rect = RECT()
    if not ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0):
        return None
    w = int(rect.right - rect.left)
    h = int(rect.bottom - rect.top)
    return w, h, int(rect.left), int(rect.top)


def _windows_restore_geometry_string() -> str:
    """Tamanho 'normal' centralizado na area util do monitor primario (bom para multi-monitor)."""
    if sys.platform != "win32":
        return f"{RESTORE_WIDTH}x{RESTORE_HEIGHT}+100+100"
    area = _windows_work_area_geometry()
    if not area:
        return f"{RESTORE_WIDTH}x{RESTORE_HEIGHT}+100+100"
    aw, ah, ax, ay = area
    x = ax + max(0, (aw - RESTORE_WIDTH) // 2)
    y = ay + max(0, (ah - RESTORE_HEIGHT) // 2)
    return f"{RESTORE_WIDTH}x{RESTORE_HEIGHT}+{x}+{y}"


@dataclass
class MenuState:
    role: str = "fisioterapeuta"
    current_module: str = "dashboard"


class EasyFeetApp(ctk.CTk):
    def __init__(self, service: EasyFeetService) -> None:
        super().__init__()
        self.service = service
        self.config_data = load_menu_config()
        self.menu_state = MenuState()
        self._editing_paciente_id: int | None = None
        self._pending_paciente_edit_id: int | None = None
        self._paciente_form: dict[str, object] | None = None
        self._hub_cliente_id: int | None = None
        self._hub_section: str = "resumo"
        self._hub_content_host: ctk.CTkScrollableFrame | None = None
        self._pacientes_tree: ttk.Treeview | None = None
        self._filter_sidebar: ctk.CTkToplevel | None = None
        self._paciente_filters: dict[str, str] = {
            "nome": "",
            "telefone": "",
            "email": "",
            "nascimento": "",
            "sexo": "",
            "observacoes": "",
        }

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        ctk.set_widget_scaling(1.0)

        self.title("EasyFeet - Gestao Clinica")
        self.geometry(_windows_restore_geometry_string())
        self.minsize(1080, 680)
        self._maximize_done = False
        self._maximize_tries = 0
        self._efm_proc: subprocess.Popen[object] | None = None
        self._marker_rule_store = MarkerRuleStore()
        self._marker_rules_tree: ttk.Treeview | None = None
        self._editing_rule_id: int | None = None
        self._selected_rule_image: str = ""
        self._nav_collapsed: set[str] = set()
        self._treeview_style_ready = False
        self._podoscopio_ctx: dict[str, int | None] = {"cliente_id": None, "ficha_id": None}

        self._build_layout()
        self._render_sidebar()
        self._show_module("dashboard")

        # Windows: janela com tamanho normal fixo (Restaurar), depois maximizacao real do SO
        # (evita preencher area util em estado "normal", que quebra Restaurar em dois monitores).
        self.after(300, self._apply_startup_window_layout)

    def _ensure_treeview_style(self) -> None:
        """ttk.Treeview precisa deste estilo antes de qualquer uso (Pacientes, Regras, etc.)."""
        if self._treeview_style_ready:
            return
        style = ttk.Style()
        style.configure("EasyFeet.Treeview", font=("Segoe UI", UI_FONT_PT), rowheight=TREE_ROW_HEIGHT)
        style.configure("EasyFeet.Treeview.Heading", font=("Segoe UI", UI_FONT_PT))
        self._treeview_style_ready = True

    def _try_windows_true_maximize(self) -> None:
        """Mesma acao do botao maximizar da barra de titulo (historico de Restaurar correto)."""
        try:
            import ctypes
            from ctypes import wintypes

            WM_SYSCOMMAND = 0x0112
            SC_MAXIMIZE = 0xF030
            hwnd = wintypes.HWND(self.winfo_id())
            ctypes.windll.user32.SendMessageW(hwnd, WM_SYSCOMMAND, SC_MAXIMIZE, 0)
        except (OSError, ValueError, AttributeError, tk.TclError):
            pass

    def _apply_startup_window_layout(self) -> None:
        if self._maximize_done:
            return
        if not self.winfo_viewable():
            self._maximize_tries += 1
            if self._maximize_tries < 40:
                self.after(100, self._apply_startup_window_layout)
            else:
                self._maximize_done = True
            return
        self.update_idletasks()
        try:
            if sys.platform == "win32":
                self.state("normal")
                self.update_idletasks()
                self.geometry(_windows_restore_geometry_string())
                self.update_idletasks()
                self._try_windows_true_maximize()
            elif sys.platform == "darwin":
                try:
                    self.attributes("-zoomed", True)
                except tk.TclError:
                    self.state("zoomed")
            else:
                try:
                    self.state("zoomed")
                except tk.TclError:
                    self.geometry(
                        f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0"
                    )
        except tk.TclError:
            try:
                self.geometry(
                    f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0"
                )
            except tk.TclError:
                pass
        self._maximize_done = True

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkFrame(self, corner_radius=0, fg_color="#ffffff", height=72)
        self.header.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.header.grid_columnconfigure(2, weight=1)

        self.sidebar = ctk.CTkFrame(self, corner_radius=0, fg_color="#f4f5f7", width=240)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self._sidebar_version = ctk.CTkLabel(
            self.sidebar,
            text=format_app_version(),
            font=ctk.CTkFont(size=UI_FONT_PT - 2),
            text_color="#888888",
        )
        self._sidebar_version.pack(side="bottom", anchor="w", padx=16, pady=(0, 14))

        self._sidebar_menu_host = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            scrollbar_button_color="#b8b8b8",
            scrollbar_button_hover_color="#7c1229",
        )
        self._sidebar_menu_host.pack(fill="both", expand=True, padx=0, pady=(0, 4))

        self.content = ctk.CTkFrame(self, fg_color="#f7f7f8", corner_radius=0)
        self.content.grid(row=1, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self._build_header()

    def _build_header(self) -> None:
        logo_path = Path("Imagens") / "EasyFeet" / "easyfeet_symbol_128.png"
        if logo_path.exists():
            image = ctk.CTkImage(Image.open(logo_path), size=(42, 42))
            logo = ctk.CTkLabel(self.header, image=image, text="")
            logo.image = image
            logo.grid(row=0, column=0, padx=(18, 8), pady=12)

        brand = ctk.CTkLabel(
            self.header,
            text="EasyFeet",
            font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
            text_color="#5b0717",
        )
        brand.grid(row=0, column=1, sticky="w", padx=(0, 20))

        self.search_entry = ctk.CTkEntry(
            self.header,
            placeholder_text="Buscar paciente por nome...",
            width=360,
            font=ctk.CTkFont(size=UI_FONT_PT),
        )
        self.search_entry.grid(row=0, column=2, sticky="w", padx=8)
        self._search_btn = ctk.CTkButton(
            self.header,
            text="Buscar",
            width=92,
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#7c1229",
            hover_color="#5b0717",
            command=self._search_patient,
        )
        self._search_btn.grid(row=0, column=3, padx=10)

        self._filtro_btn = ctk.CTkButton(
            self.header,
            text="Filtro",
            width=92,
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=self._open_pacientes_filter_sidebar,
        )
        self._filtro_btn.grid(row=0, column=4, padx=(0, 8))

        self.role_select = ctk.CTkOptionMenu(
            self.header,
            values=self.config_data["roles"],
            command=self._on_role_change,
            width=140,
            font=ctk.CTkFont(size=UI_FONT_PT),
        )
        self.role_select.set(self.menu_state.role)
        self.role_select.grid(row=0, column=5, padx=(12, 8))

    def _close_pacientes_filter_sidebar(self) -> None:
        if self._filter_sidebar is not None:
            try:
                if self._filter_sidebar.winfo_exists():
                    self._filter_sidebar.destroy()
            except tk.TclError:
                pass
            self._filter_sidebar = None

    def _update_header_paciente_tools(self) -> None:
        """Busca e filtro so fazem sentido no modulo Pacientes."""
        show = self.menu_state.current_module == "pacientes"
        if show:
            self.search_entry.grid(row=0, column=2, sticky="w", padx=8)
            self._search_btn.grid(row=0, column=3, padx=10)
            self._filtro_btn.grid(row=0, column=4, padx=(0, 8))
        else:
            self.search_entry.grid_remove()
            self._search_btn.grid_remove()
            self._filtro_btn.grid_remove()
            self._close_pacientes_filter_sidebar()

    def _sidebar_label_display(self, label: str, *, compact: bool = False) -> tuple[str, int]:
        """Quebra rotulos longos em duas linhas (sidebar estreita). Altura do botao em px."""
        text = (label or "").strip()
        if "\n" in text:
            lines = text.count("\n") + 1
            return text, 34 if compact else (38 + (lines - 1) * 10)
        if len(text) <= 14:
            return text, 34 if compact else 38
        words = text.split()
        if len(words) < 2:
            return text, 34 if compact else 38
        line1 = words[0]
        line2 = " ".join(words[1:])
        if len(line1) > 16:
            return text, 34 if compact else 38
        return f"{line1}\n{line2}", 44 if compact else 48

    def _sidebar_module_selected(self, module_id: str) -> bool:
        """Hub (ficha clinica) destaca Pacientes na sidebar."""
        current = self.menu_state.current_module
        if current == "paciente_hub":
            return module_id == "pacientes"
        return module_id == current

    def _render_sidebar(self) -> None:
        for child in self._sidebar_menu_host.winfo_children():
            child.destroy()

        ctk.CTkLabel(
            self._sidebar_menu_host,
            text="Menu",
            font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
            text_color="#333333",
        ).pack(anchor="w", padx=16, pady=(16, 10))

        menu = get_visible_menu_for_role(self.config_data, self.menu_state.role)
        for item in menu:
            children = get_visible_child_menu_items(item, self.menu_state.role)
            if children:
                self._render_sidebar_accordion_row(item, children)
                continue
            parent_sel = self._sidebar_module_selected(item["id"])
            label_txt, btn_h = self._sidebar_label_display(item["label"])
            btn = ctk.CTkButton(
                self._sidebar_menu_host,
                text=label_txt,
                font=ctk.CTkFont(size=UI_FONT_PT),
                anchor="w",
                height=btn_h,
                fg_color="#dbe8ff" if parent_sel else "#ffffff",
                text_color="#232323",
                hover_color="#e9eefc",
                corner_radius=8,
                command=lambda module=item["id"]: self._show_module(module),
            )
            btn.pack(fill="x", padx=12, pady=4)

    def _nav_group_expanded(self, item: dict, _children: list) -> bool:
        """Respeita o clique na seta (_nav_collapsed). Abrir ao navegar: _expand_nav_ancestors_for."""
        return str(item["id"]) not in self._nav_collapsed

    def _expand_nav_ancestors_for(self, module_id: str) -> None:
        path = find_menu_item_path(self.config_data, module_id)
        for item in path[:-1]:
            self._nav_collapsed.discard(str(item["id"]))

    def _toggle_nav_group(self, parent_id: str) -> None:
        if parent_id in self._nav_collapsed:
            self._nav_collapsed.discard(parent_id)
        else:
            self._nav_collapsed.add(parent_id)
        self._render_sidebar()

    def _render_sidebar_accordion_row(self, item: dict, children: list) -> None:
        expanded = self._nav_group_expanded(item, children)
        pid = str(item["id"])
        row = ctk.CTkFrame(self._sidebar_menu_host, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=4)

        parent_sel = self._sidebar_module_selected(item["id"])
        label_txt, btn_h = self._sidebar_label_display(item["label"])

        chevron = ctk.CTkButton(
            row,
            text="▼" if expanded else "▶",
            width=36,
            height=btn_h,
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#eceef2",
            text_color="#232323",
            hover_color="#dfe4ee",
            corner_radius=8,
            command=lambda p=pid: self._toggle_nav_group(p),
        )
        chevron.pack(side="left", padx=(0, 6))

        title_btn = ctk.CTkButton(
            row,
            text=label_txt,
            font=ctk.CTkFont(size=UI_FONT_PT),
            anchor="w",
            height=btn_h,
            fg_color="#dbe8ff" if parent_sel else "#ffffff",
            text_color="#232323",
            hover_color="#e9eefc",
            corner_radius=8,
            command=lambda module=item["id"]: self._show_module(module),
        )
        title_btn.pack(side="left", fill="x", expand=True)

        if not expanded:
            return
        for ch in children:
            sub_children = get_visible_child_menu_items(ch, self.menu_state.role)
            if sub_children:
                self._render_sidebar_nested_accordion_row(ch, sub_children, indent=22)
            else:
                self._render_sidebar_leaf_button(ch, indent=22)

    def _render_sidebar_leaf_button(self, item: dict, *, indent: int) -> None:
        child_sel = self._sidebar_module_selected(item["id"])
        label_txt, btn_h = self._sidebar_label_display(item["label"], compact=True)
        sub = ctk.CTkButton(
            self._sidebar_menu_host,
            text=f"  {label_txt}",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            anchor="w",
            height=btn_h,
            fg_color="#dbe8ff" if child_sel else "#ffffff",
            text_color="#232323",
            hover_color="#e9eefc",
            corner_radius=8,
            command=lambda module=item["id"]: self._show_module(module),
        )
        sub.pack(fill="x", padx=(indent, 12), pady=2)

    def _render_sidebar_nested_accordion_row(self, item: dict, children: list, *, indent: int) -> None:
        expanded = self._nav_group_expanded(item, children)
        pid = str(item["id"])
        row = ctk.CTkFrame(self._sidebar_menu_host, fg_color="transparent")
        row.pack(fill="x", padx=(indent, 12), pady=2)

        parent_sel = self._sidebar_module_selected(item["id"])
        label_txt, btn_h = self._sidebar_label_display(item["label"], compact=True)

        chevron = ctk.CTkButton(
            row,
            text="▼" if expanded else "▶",
            width=32,
            height=btn_h,
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            fg_color="#eceef2",
            text_color="#232323",
            hover_color="#dfe4ee",
            corner_radius=8,
            command=lambda p=pid: self._toggle_nav_group(p),
        )
        chevron.pack(side="left", padx=(0, 4))

        title_btn = ctk.CTkButton(
            row,
            text=label_txt,
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            anchor="w",
            height=btn_h,
            fg_color="#dbe8ff" if parent_sel else "#ffffff",
            text_color="#232323",
            hover_color="#e9eefc",
            corner_radius=8,
            command=lambda module=item["id"]: self._show_module(module),
        )
        title_btn.pack(side="left", fill="x", expand=True)

        if not expanded:
            return
        for ch in children:
            self._render_sidebar_leaf_button(ch, indent=indent + 16)

    def _show_module(self, module_id: str) -> None:
        self.menu_state.current_module = module_id
        self._expand_nav_ancestors_for(module_id)
        self._render_sidebar()
        for child in self.content.winfo_children():
            child.destroy()

        if module_id == "dashboard":
            self._build_dashboard()
        elif module_id == "pacientes":
            self._build_pacientes()
        elif module_id in ("paciente_hub",):
            self._build_paciente_hub()
        elif module_id == "plantigrafo":
            self._build_plantigrafo_hub()
        elif module_id in ("efm_marcadores",):
            self._build_efm_shell_placeholder()
        elif module_id in ("plantigrafo_config", "configuracoes_regras_marcadores"):
            self._build_configuracoes_regras_marcadores()
        elif module_id == "podoscopio":
            self._build_podoscopio_hub()
        elif module_id == "podoscopio_ficha_tecnica":
            self._build_podoscopio_ficha_tecnica()
        elif module_id == "configuracoes":
            self._build_configuracoes_hub()
        elif module_id == "avaliacao_postural":
            self._build_avaliacao_postural_hub()
        elif module_id in (
            "laudos_consolidado",
            "plantigrafo_laudos",
            "podoscopio_laudos",
            "podoscopio_config",
            "palmilhas",
            "relatorios",
            "postural_avaliacao",
            "postural_laudos",
            "postural_config",
            "config_clinica",
            "config_usuarios",
            "config_licencas",
            "config_templates_pdf",
            "avaliacoes",
            "laudos",
            "imagens",
        ):
            self._build_placeholder(module_id)
        elif module_id == "modulos":
            self._show_module("plantigrafo")
        else:
            self._build_placeholder(module_id)
        self._update_header_paciente_tools()

    def _open_efm_marcadores(
        self,
        cliente_id: int | None = None,
        momento_id: int | None = None,
        imagem_id: int | None = None,
        tipo_marcador: str | None = None,
    ) -> None:
        """Abre o módulo EFM em janela separada (não-bloqueante)."""
        try:
            if self._efm_proc is not None and self._efm_proc.poll() is None:
                # Já está aberto. Se houver contexto, avisamos que precisa reabrir.
                if any(v is not None for v in (cliente_id, momento_id, imagem_id)) or bool(tipo_marcador):
                    messagebox.showinfo(
                        "Marcadores",
                        "O módulo de marcadores já está aberto.\n\n"
                        "Para abrir no contexto selecionado (paciente/momento/imagem), feche o EFM atual e clique novamente em 'Reabrir no EFM'.",
                    )
                return

            frozen = bool(getattr(sys, "frozen", False))
            if frozen:
                root = Path(sys.executable).resolve().parent
                efm_exe = root / "EFM_Marcadores.exe"
                if not efm_exe.exists():
                    messagebox.showerror("Marcadores", f"Nao encontrei o executavel: {efm_exe}")
                    return
                cmd = [str(efm_exe)]
            else:
                root = Path(__file__).resolve().parents[1]
                script = root / "EFM_Marcadores.py"
                if not script.exists():
                    messagebox.showerror("Marcadores", f"Nao encontrei o ficheiro: {script}")
                    return
                cmd = [sys.executable, str(script)]

            if cliente_id is not None:
                cmd.extend(["--cliente-id", str(cliente_id)])
            if momento_id is not None:
                cmd.extend(["--momento-id", str(momento_id)])
            if imagem_id is not None:
                cmd.extend(["--imagem-id", str(imagem_id)])
            if tipo_marcador:
                cmd.extend(["--tipo", tipo_marcador])

            creationflags = 0
            try:
                creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
            except Exception:
                creationflags = 0

            self._efm_proc = subprocess.Popen(  # type: ignore[assignment]
                cmd,
                cwd=str(root),
                creationflags=creationflags,
            )
        except Exception as exc:
            messagebox.showerror("Marcadores", f"Falha ao abrir:\n{exc}")

    def _open_path_external(self, path: Path) -> None:
        try:
            if sys.platform == "win32":
                import os

                os.startfile(str(path))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception as exc:
            messagebox.showerror("EasyFeet", f"Nao foi possivel abrir o ficheiro:\n{exc}")

    def _build_dashboard(self) -> None:
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        render_dashboard(frame, self.service, font_pt=UI_FONT_PT)

    def _set_paciente_imc_display(self, imc_entry: ctk.CTkEntry, texto: str) -> None:
        imc_entry.configure(state="normal")
        imc_entry.delete(0, tk.END)
        imc_entry.insert(0, texto)
        imc_entry.configure(state="disabled")

    def _atualizar_imc_preview_paciente(self, altura: ctk.CTkEntry, peso: ctk.CTkEntry, imc_entry: ctk.CTkEntry) -> None:
        self._set_paciente_imc_display(imc_entry, imc_preview(altura.get(), peso.get()))

    def _show_paciente_imc_help(self, altura: ctk.CTkEntry, peso: ctk.CTkEntry) -> None:
        modal = ctk.CTkToplevel(self)
        modal.title("IMC — tabela de referência (adultos)")
        modal.geometry("920x520")
        modal.minsize(820, 440)
        modal.transient(self)
        modal.grab_set()

        modal_font = ctk.CTkFont(size=IMC_MODAL_FONT_PT)
        modal_font_bold = ctk.CTkFont(size=IMC_MODAL_FONT_PT, weight="bold")

        frame = ctk.CTkFrame(modal, fg_color="#ffffff")
        frame.pack(fill="both", expand=True, padx=16, pady=16)
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text="Classificação do IMC (referência clínica)",
            font=modal_font_bold,
            text_color="#333333",
        ).grid(row=0, column=0, sticky="w", padx=8, pady=(4, 6))

        ctk.CTkLabel(
            frame,
            text="Tabela para adultos (18+). Em crianças/adolescentes, use curvas pediátricas por idade/sexo.",
            font=modal_font,
            text_color="#555555",
            wraplength=860,
            justify="left",
        ).grid(row=1, column=0, sticky="w", padx=8, pady=(0, 8))

        atual = imc_valor_numerico(altura.get(), peso.get())
        resumo_txt = "Preencha altura e peso para ver a classificação do paciente."
        if atual is not None:
            faixa = classificar_imc(atual)
            resumo_txt = f"IMC atual: {formatar_imc(atual)}  →  {faixa.nome}  ({faixa.intervalo})"

        ctk.CTkLabel(frame, text=resumo_txt, font=modal_font_bold, text_color="#333333").grid(
            row=2, column=0, sticky="w", padx=8, pady=(0, 8)
        )

        table_host = ttk.Frame(frame)
        table_host.grid(row=3, column=0, sticky="nsew", padx=8, pady=(0, 10))
        table_host.grid_rowconfigure(0, weight=1)
        table_host.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("IMC.Treeview", font=("Segoe UI", IMC_MODAL_FONT_PT), rowheight=26)
        style.configure("IMC.Treeview.Heading", font=("Segoe UI", IMC_MODAL_FONT_PT, "bold"))

        cols = ("imc", "classificacao", "interpretacao")
        tree = ttk.Treeview(
            table_host,
            columns=cols,
            show="headings",
            style="IMC.Treeview",
            height=6,
            selectmode="browse",
        )
        tree.heading("imc", text="Faixa IMC (adulto)")
        tree.heading("classificacao", text="Classificação")
        tree.heading("interpretacao", text="Interpretação resumida")
        tree.column("imc", width=155, minwidth=130, anchor="w", stretch=False)
        tree.column("classificacao", width=220, minwidth=170, anchor="w", stretch=False)
        tree.column("interpretacao", width=420, minwidth=280, anchor="w", stretch=True)
        tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(table_host, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_host, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree.tag_configure("current", background="#dbe8ff", foreground="#111111")

        current_name = classificar_imc(atual).nome if atual is not None else None
        current_iid: str | None = None
        for f in FAIXAS_IMC_ADULTO:
            tag = ("current",) if current_name == f.nome else ()
            iid = tree.insert("", "end", values=(f.intervalo, f.nome, f.texto_tabela), tags=tag)
            if current_name == f.nome:
                current_iid = iid

        if current_iid is not None:
            tree.selection_set(current_iid)
            tree.focus(current_iid)
            tree.see(current_iid)

        ctk.CTkLabel(
            frame,
            text="Nota: IMC é um indicador populacional; não substitui exame clínico nem avaliação postural/plantar.",
            font=modal_font,
            text_color="#555555",
            wraplength=860,
            justify="left",
        ).grid(row=4, column=0, sticky="w", padx=8, pady=(0, 10))

        ctk.CTkButton(frame, text="Fechar", font=modal_font, command=modal.destroy).grid(
            row=5, column=0, sticky="e", padx=8, pady=(0, 4)
        )

    def _build_pacientes(self) -> None:
        if self._pending_paciente_edit_id is None:
            self._editing_paciente_id = None

        shell = ctk.CTkFrame(self.content, fg_color="transparent")
        shell.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(0, weight=1)

        root = ctk.CTkScrollableFrame(
            shell,
            fg_color="#f7f7f8",
            scrollbar_button_color="#b8b8b8",
            scrollbar_button_hover_color="#7c1229",
        )
        root.grid(row=0, column=0, sticky="nsew")
        root.grid_columnconfigure(0, weight=1)

        form = ctk.CTkFrame(root, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec")
        form.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        form.grid_columnconfigure(0, weight=1)
        for c in range(1, 6):
            form.grid_columnconfigure(c, weight=0)
        title_label = ctk.CTkLabel(form, text="Novo paciente", font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"))
        title_label.grid(
            row=0, column=0, columnspan=6, sticky="w", padx=14, pady=(12, 4)
        )
        # Labels da linha principal do CRUD.
        ctk.CTkLabel(form, text="Nome *", font=ctk.CTkFont(size=UI_FONT_PT - 1)).grid(
            row=1, column=0, padx=8, pady=(2, 0), sticky="w"
        )
        ctk.CTkLabel(form, text="Telefone", font=ctk.CTkFont(size=UI_FONT_PT - 1)).grid(
            row=1, column=1, padx=8, pady=(2, 0), sticky="w"
        )
        ctk.CTkLabel(form, text="Email", font=ctk.CTkFont(size=UI_FONT_PT - 1)).grid(
            row=1, column=2, padx=8, pady=(2, 0), sticky="w"
        )
        birth_lbl_fr = ctk.CTkFrame(form, fg_color="transparent")
        birth_lbl_fr.grid(row=1, column=3, padx=8, pady=(2, 0), sticky="w")
        ctk.CTkLabel(birth_lbl_fr, text="Nascimento *", font=ctk.CTkFont(size=UI_FONT_PT - 1)).pack(side="left")
        ctk.CTkButton(
            birth_lbl_fr,
            text="ⓘ",
            width=28,
            height=22,
            font=ctk.CTkFont(size=UI_FONT_PT - 2),
            fg_color="#ececec",
            text_color="#333333",
            hover_color="#dbe8ff",
            corner_radius=6,
            command=self._show_nascimento_idade_help,
        ).pack(side="left", padx=(6, 0))
        ctk.CTkLabel(form, text="Sexo *", font=ctk.CTkFont(size=UI_FONT_PT - 1)).grid(
            row=1, column=4, padx=8, pady=(2, 0), sticky="w"
        )
        ctk.CTkLabel(form, text="Lateralidade *", font=ctk.CTkFont(size=UI_FONT_PT - 1)).grid(
            row=1, column=5, padx=8, pady=(2, 0), sticky="w"
        )

        field_font = ctk.CTkFont(size=UI_FONT_PT)
        entry_h = 36
        nome = ctk.CTkEntry(form, placeholder_text="Nome completo", font=field_font, height=entry_h)
        telefone = ctk.CTkEntry(form, placeholder_text="Telefone", font=field_font, height=entry_h, width=130)
        email = ctk.CTkEntry(form, placeholder_text="Email", font=field_font, height=entry_h, width=170)
        nascimento = ctk.CTkEntry(form, placeholder_text="DD/MM/AAAA", font=field_font, height=entry_h, width=110)
        sexo = ctk.CTkOptionMenu(
            form,
            values=["Selecione... *", "Masculino", "Feminino"],
            font=field_font,
            height=entry_h,
            width=120,
            dynamic_resizing=False,
        )
        sexo.set("Selecione... *")
        lateralidade = ctk.CTkOptionMenu(
            form,
            values=["Selecione... *", *LATERALIDADE_OPCOES],
            font=field_font,
            height=entry_h,
            width=120,
            dynamic_resizing=False,
        )
        lateralidade.set("Selecione... *")

        corp = ctk.CTkFrame(form, fg_color="#f8f8f8", corner_radius=8, border_width=1, border_color="#e0e0e0")
        corp.grid(row=3, column=0, columnspan=3, padx=8, pady=(4, 6), sticky="w")
        ctk.CTkLabel(corp, text="Altura (m) *", font=ctk.CTkFont(size=UI_FONT_PT - 1)).grid(
            row=0, column=0, padx=(10, 6), pady=(8, 0), sticky="w"
        )
        ctk.CTkLabel(corp, text="Peso (kg) *", font=ctk.CTkFont(size=UI_FONT_PT - 1)).grid(
            row=0, column=1, padx=6, pady=(8, 0), sticky="w"
        )
        imc_hdr = ctk.CTkFrame(corp, fg_color="transparent")
        imc_hdr.grid(row=0, column=2, padx=(6, 10), pady=(8, 0), sticky="w")
        ctk.CTkLabel(imc_hdr, text="IMC", font=ctk.CTkFont(size=UI_FONT_PT - 1)).pack(side="left")

        altura = ctk.CTkEntry(corp, placeholder_text="1,75", font=field_font, height=entry_h, width=80)
        peso = ctk.CTkEntry(corp, placeholder_text="68,5", font=field_font, height=entry_h, width=80)
        imc_row = ctk.CTkFrame(corp, fg_color="transparent")
        imc_row.grid(row=1, column=2, padx=(6, 10), pady=(4, 10), sticky="w")
        imc_entry = ctk.CTkEntry(
            imc_row,
            font=field_font,
            height=entry_h,
            width=68,
            placeholder_text="-",
            state="disabled",
            text_color="#333333",
        )
        imc_entry.pack(side="left")
        ctk.CTkButton(
            imc_row,
            text="?",
            width=26,
            height=entry_h - 4,
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            fg_color="#ececec",
            text_color="#333333",
            hover_color="#dbe8ff",
            corner_radius=6,
            command=lambda: self._show_paciente_imc_help(altura, peso),
        ).pack(side="left", padx=(6, 0))
        altura.grid(row=1, column=0, padx=(10, 6), pady=(4, 10), sticky="w")
        peso.grid(row=1, column=1, padx=6, pady=(4, 10), sticky="w")

        def _on_corporal_change(_event: object | None = None) -> None:
            self._atualizar_imc_preview_paciente(altura, peso, imc_entry)

        altura.bind("<KeyRelease>", _on_corporal_change)
        peso.bind("<KeyRelease>", _on_corporal_change)

        obs = ctk.CTkTextbox(
            form,
            font=field_font,
            height=70,
            border_width=1,
            border_color="#b8b8b8",
            fg_color="#ffffff",
        )
        nome.grid(row=2, column=0, padx=8, pady=(0, 6), sticky="ew")
        telefone.grid(row=2, column=1, padx=8, pady=(0, 6), sticky="w")
        email.grid(row=2, column=2, padx=8, pady=(0, 6), sticky="w")
        nascimento.grid(row=2, column=3, padx=8, pady=(0, 6), sticky="w")
        sexo.grid(row=2, column=4, padx=8, pady=(0, 6), sticky="w")
        lateralidade.grid(row=2, column=5, padx=8, pady=(0, 6), sticky="w")
        ctk.CTkLabel(form, text="Observacoes", font=ctk.CTkFont(size=UI_FONT_PT - 1)).grid(
            row=4, column=0, columnspan=6, padx=8, pady=(4, 0), sticky="w"
        )
        obs.grid(row=5, column=0, columnspan=6, padx=8, pady=(0, 8), sticky="ew")
        obs.insert("1.0", "Observacoes...")
        obs.configure(text_color="#666666")

        def _focus_obs_in(_event: object | None = None) -> None:
            if obs.get("1.0", "end-1c").strip() == "Observacoes...":
                obs.delete("1.0", "end")
                obs.configure(text_color="#000000")

        def _focus_obs_out(_event: object | None = None) -> None:
            if not obs.get("1.0", "end-1c").strip():
                obs.delete("1.0", "end")
                obs.insert("1.0", "Observacoes...")
                obs.configure(text_color="#666666")

        obs.bind("<FocusIn>", _focus_obs_in)
        obs.bind("<FocusOut>", _focus_obs_out)

        self._paciente_form = {
            "title_label": title_label,
            "salvar_btn": None,
            "nome": nome,
            "telefone": telefone,
            "email": email,
            "nascimento": nascimento,
            "sexo": sexo,
            "lateralidade": lateralidade,
            "altura": altura,
            "peso": peso,
            "obs": obs,
            "on_corporal_change": _on_corporal_change,
        }

        def _apply_date_mask(_event: object | None = None) -> None:
            raw = "".join(ch for ch in nascimento.get() if ch.isdigit())[:8]
            parts: list[str] = []
            if raw:
                parts.append(raw[:2])
            if len(raw) > 2:
                parts.append(raw[2:4])
            if len(raw) > 4:
                parts.append(raw[4:8])
            masked = "/".join(parts)
            atual = nascimento.get()
            if masked != atual:
                nascimento.delete(0, tk.END)
                nascimento.insert(0, masked)

        nascimento.bind("<KeyRelease>", _apply_date_mask)

        def salvar_ou_atualizar() -> None:
            obs_text = obs.get("1.0", "end-1c")
            if obs_text.strip() == "Observacoes...":
                obs_text = ""
            lat = lateralidade.get()
            if lat.startswith("Selecione"):
                lat = ""
            try:
                if self._editing_paciente_id is None:
                    self.service.cadastrar_cliente(
                        nome.get(),
                        telefone.get(),
                        email.get(),
                        nascimento.get(),
                        sexo.get(),
                        obs_text,
                        altura.get(),
                        peso.get(),
                        lat,
                        exigir_dados_corporais=True,
                    )
                    messagebox.showinfo("EasyFeet", "Paciente cadastrado com sucesso.")
                else:
                    self.service.atualizar_cliente(
                        self._editing_paciente_id,
                        nome.get(),
                        telefone.get(),
                        email.get(),
                        nascimento.get(),
                        sexo.get(),
                        obs_text,
                        altura.get(),
                        peso.get(),
                        lat,
                        exigir_dados_corporais=True,
                    )
                    messagebox.showinfo("EasyFeet", "Paciente atualizado com sucesso.")
            except ValueError as exc:
                messagebox.showerror("Validacao", str(exc))
                return

            limpar_formulario_novo()
            self._refresh_patients_table(tree)

        def limpar_formulario_novo() -> None:
            self._editing_paciente_id = None
            title_label.configure(text="Novo paciente")
            salvar_btn.configure(text="Salvar paciente")
            for entry in (nome, telefone, email, nascimento, altura, peso):
                entry.delete(0, tk.END)
            obs.delete("1.0", "end")
            obs.insert("1.0", "Observacoes...")
            obs.configure(text_color="#666666")
            sexo.set("Selecione... *")
            lateralidade.set("Selecione... *")
            _on_corporal_change()
            for sel in tree.selection():
                tree.selection_remove(sel)

        salvar_btn = ctk.CTkButton(
            form,
            text="Salvar paciente",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#7c1229",
            hover_color="#5b0717",
            command=salvar_ou_atualizar,
        )
        salvar_btn.grid(row=6, column=5, padx=8, pady=(4, 12), sticky="e")
        if self._paciente_form is not None:
            self._paciente_form["salvar_btn"] = salvar_btn
        _on_corporal_change()

        table_box = ctk.CTkFrame(root, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec")
        table_box.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        table_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            root,
            text="Marcacoes e momentos clinicos: selecione o paciente e use «Abrir ficha clinica» → Linha do tempo.",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            text_color="#666666",
            wraplength=900,
            justify="left",
        ).grid(row=2, column=0, sticky="w", pady=(0, 14))

        table_hdr = ctk.CTkFrame(table_box, fg_color="transparent")
        table_hdr.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
        table_hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            table_hdr,
            text="Pacientes cadastrados",
            font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
            text_color="#333333",
        ).grid(row=0, column=0, sticky="w")

        self._ensure_treeview_style()

        columns = ("id", "nome", "idade", "sexo", "altura", "peso", "imc", "lat", "telefone", "email", "obs")
        tree_host = ttk.Frame(table_box)
        tree_host.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        tree_host.grid_columnconfigure(0, weight=1)
        tree_host.grid_rowconfigure(0, weight=1)

        tree = ttk.Treeview(
            tree_host,
            columns=columns,
            show="headings",
            height=8,
            displaycolumns=columns,
        )
        tree.configure(style="EasyFeet.Treeview")
        col_specs: tuple[tuple[str, str, int, str], ...] = (
            ("id", "ID", 48, "center"),
            ("nome", "Nome", 200, "w"),
            ("idade", "Idade", 76, "center"),
            ("sexo", "Sexo", 96, "center"),
            ("altura", "Alt. (m)", 80, "center"),
            ("peso", "Peso (kg)", 84, "center"),
            ("imc", "IMC", 64, "center"),
            ("lat", "Lateralidade", 118, "center"),
            ("telefone", "Telefone", 118, "center"),
            ("email", "Email", 260, "w"),
            ("obs", "Obs", 52, "center"),
        )
        for cid, title, width, anchor in col_specs:
            tree.heading(cid, text=title)
            tree.column(cid, width=width, minwidth=width, anchor=anchor, stretch=False)
        tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(tree_host, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_host, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        def _get_selected_cliente() -> tuple[int, object] | None:
            selecionado = tree.focus()
            if not selecionado:
                return None
            valores = tree.item(selecionado, "values")
            if not valores:
                return None
            cliente_id = int(valores[0])
            cliente = self.service.clientes.obter_por_id(cliente_id)
            if not cliente:
                return None
            return cliente_id, cliente

        def carregar_para_edicao(event: object | None = None) -> None:
            selected = _get_selected_cliente()
            if not selected:
                messagebox.showinfo("Edicao", "Selecione um paciente na tabela.")
                return
            _cliente_id, cliente = selected
            self._fill_paciente_edit_form(cliente)

        def ver_observacao() -> None:
            selected = _get_selected_cliente()
            if not selected:
                messagebox.showinfo("Observacao", "Selecione um paciente na tabela.")
                return
            _cliente_id, cliente = selected
            texto = (cliente.observacoes or "").strip()
            if not texto:
                messagebox.showinfo("Observacao", "Este paciente nao possui observacoes.")
                return
            self._show_observacao_modal(cliente.nome, texto)

        def abrir_marcadores_paciente() -> None:
            selected = _get_selected_cliente()
            if not selected:
                messagebox.showinfo("Marcadores", "Selecione um paciente na tabela.")
                return
            cliente_id, _cliente = selected
            self._open_efm_marcadores(cliente_id=cliente_id)

        def _abrir_ficha_clinica() -> None:
            selected = _get_selected_cliente()
            if not selected:
                messagebox.showinfo("Ficha clinica", "Selecione um paciente na tabela.")
                return
            cliente_id, _cliente = selected
            self._open_paciente_hub(cliente_id)

        def _exportar_pdf_cadastro_branco() -> None:
            default_name = "Cadastro_Paciente_EM_BRANCO.pdf"
            dest = filedialog.asksaveasfilename(
                title="PDF cadastro em branco (caneta)",
                defaultextension=".pdf",
                initialfile=default_name,
                filetypes=[("PDF", "*.pdf")],
            )
            if not dest:
                return
            try:
                export_ficha_cadastro_paciente_pdf_branco(Path(dest))
            except Exception as exc:
                messagebox.showerror("Pacientes", f"Falha ao gerar PDF:\n{exc}")
                return
            messagebox.showinfo("Pacientes", f"PDF para caneta gerado:\n{dest}")

        def _exportar_pdf_cadastro_preenchida() -> None:
            selected = _get_selected_cliente()
            if not selected:
                messagebox.showinfo(
                    "Pacientes",
                    "Selecione um paciente na tabela para gerar o PDF com os dados gravados.",
                )
                return
            _cid, cliente = selected
            nome_safe = "".join(ch if ch.isalnum() or ch in " -_" else "_" for ch in cliente.nome)[:40]
            default_name = f"Cadastro_Paciente_PREENCHIDO_{nome_safe}.pdf"
            dest = filedialog.asksaveasfilename(
                title="PDF cadastro preenchido (dados do sistema)",
                defaultextension=".pdf",
                initialfile=default_name,
                filetypes=[("PDF", "*.pdf")],
            )
            if not dest:
                return
            try:
                export_ficha_cadastro_paciente_pdf_preenchida(Path(dest), cliente=cliente)
            except Exception as exc:
                messagebox.showerror("Pacientes", f"Falha ao gerar PDF:\n{exc}")
                return
            messagebox.showinfo("Pacientes", f"PDF com dados do paciente:\n{dest}")

        pdf_btns = ctk.CTkFrame(table_hdr, fg_color="transparent")
        pdf_btns.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(
            pdf_btns,
            text="PDF cadastro em branco",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=_exportar_pdf_cadastro_branco,
        ).pack(side="left")
        ctk.CTkButton(
            pdf_btns,
            text="PDF cadastro preenchido",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=_exportar_pdf_cadastro_preenchida,
        ).pack(side="left", padx=(8, 0))

        botoes_frame = ctk.CTkFrame(form, fg_color="transparent")
        botoes_frame.grid(row=6, column=0, columnspan=3, padx=8, pady=(4, 12), sticky="w")

        ctk.CTkButton(
            botoes_frame,
            text="Novo paciente",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=limpar_formulario_novo,
        ).pack(side="left")

        obs_btn = ctk.CTkButton(
            botoes_frame,
            text="Ver observacao",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=ver_observacao,
        )
        obs_btn.pack(side="left")

        editar_btn = ctk.CTkButton(
            botoes_frame,
            text="Editar selecionado",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=carregar_para_edicao,
        )
        editar_btn.pack(side="left", padx=(8, 0))

        marcadores_btn = ctk.CTkButton(
            botoes_frame,
            text="Abrir marcadores",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=abrir_marcadores_paciente,
        )
        marcadores_btn.pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            botoes_frame,
            text="Abrir ficha clinica",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#7c1229",
            hover_color="#5b0717",
            command=_abrir_ficha_clinica,
        ).pack(side="left", padx=(8, 0))

        self._refresh_patients_table(tree)
        self._pacientes_tree = tree
        tree.bind("<Double-1>", carregar_para_edicao)

        def on_tree_click(event: tk.Event[tk.Misc]) -> None:
            region = tree.identify("region", event.x, event.y)
            if region != "cell":
                return
            col = tree.identify_column(event.x)
            if col != "#11":
                return
            row_id = tree.identify_row(event.y)
            if not row_id:
                return
            tree.selection_set(row_id)
            tree.focus(row_id)
            ver_observacao()

        tree.bind("<Button-1>", on_tree_click)

        if self._pending_paciente_edit_id is not None:
            pending_id = self._pending_paciente_edit_id
            self._pending_paciente_edit_id = None
            cliente = self.service.clientes.obter_por_id(pending_id)
            if cliente is not None:
                self._fill_paciente_edit_form(cliente)
                for row_id in tree.get_children():
                    vals = tree.item(row_id, "values")
                    if vals and int(vals[0]) == pending_id:
                        tree.selection_set(row_id)
                        tree.focus(row_id)
                        break

    def _fill_paciente_edit_form(self, cliente: object) -> None:
        form = self._paciente_form
        if not form:
            return
        self._editing_paciente_id = int(getattr(cliente, "id"))
        title_label = form["title_label"]
        salvar_btn = form["salvar_btn"]
        nome = form["nome"]
        telefone = form["telefone"]
        email = form["email"]
        nascimento = form["nascimento"]
        sexo = form["sexo"]
        lateralidade = form["lateralidade"]
        altura = form["altura"]
        peso = form["peso"]
        obs = form["obs"]
        on_corporal = form["on_corporal_change"]
        assert isinstance(title_label, ctk.CTkLabel)
        assert isinstance(salvar_btn, ctk.CTkButton)
        title_label.configure(text=f"Editar paciente #{cliente.id}")
        salvar_btn.configure(text="Atualizar paciente")
        for entry in (nome, telefone, email, nascimento, altura, peso):
            assert isinstance(entry, ctk.CTkEntry)
            entry.delete(0, tk.END)
        assert isinstance(nome, ctk.CTkEntry)
        nome.insert(0, cliente.nome)
        telefone.insert(0, cliente.telefone or "")
        email.insert(0, cliente.email or "")
        nascimento.insert(0, cliente.data_nascimento or "")
        sexo_salvo = (cliente.sexo or "").strip()
        assert isinstance(sexo, ctk.CTkOptionMenu)
        sexo.set(sexo_salvo if sexo_salvo in {"Masculino", "Feminino"} else "Selecione... *")
        lat_salva = (cliente.lateralidade or "").strip()
        assert isinstance(lateralidade, ctk.CTkOptionMenu)
        lateralidade.set(lat_salva if lat_salva in LATERALIDADE_OPCOES else "Selecione... *")
        altura.insert(0, formatar_altura(cliente.altura_m))
        peso.insert(0, formatar_peso(cliente.peso_kg))
        assert callable(on_corporal)
        on_corporal()
        assert isinstance(obs, ctk.CTkTextbox)
        obs.delete("1.0", "end")
        texto_obs = (cliente.observacoes or "").strip()
        if texto_obs:
            obs.insert("1.0", texto_obs)
            obs.configure(text_color="#000000")
        else:
            obs.insert("1.0", "Observacoes...")
            obs.configure(text_color="#666666")

    def _refresh_patients_table(self, tree: ttk.Treeview) -> None:
        for row in tree.get_children():
            tree.delete(row)
        for cliente in self.service.clientes.listar():
            if not self._cliente_matches_filters(cliente):
                continue
            idade = self._format_idade(cliente.data_nascimento or "")
            obs_icon = "👁" if (cliente.observacoes or "").strip() else ""
            tree.insert(
                "",
                "end",
                values=(
                    cliente.id,
                    cliente.nome,
                    idade,
                    (cliente.sexo or "-"),
                    formatar_altura(cliente.altura_m) or "-",
                    formatar_peso(cliente.peso_kg) or "-",
                    formatar_imc(calcular_imc(cliente.altura_m, cliente.peso_kg)),
                    (cliente.lateralidade or "-"),
                    cliente.telefone or "-",
                    cliente.email or "-",
                    obs_icon,
                ),
            )

    def _cliente_matches_filters(self, cliente: object) -> bool:
        nome = self._paciente_filters["nome"].strip().lower()
        telefone = self._paciente_filters["telefone"].strip().lower()
        email = self._paciente_filters["email"].strip().lower()
        nascimento = self._paciente_filters["nascimento"].strip().lower()
        sexo = self._paciente_filters["sexo"].strip()
        observacoes = self._paciente_filters["observacoes"].strip().lower()

        if nome and nome not in (getattr(cliente, "nome", "") or "").lower():
            return False
        if telefone and telefone not in (getattr(cliente, "telefone", "") or "").lower():
            return False
        if email and email not in (getattr(cliente, "email", "") or "").lower():
            return False
        if nascimento and nascimento not in (getattr(cliente, "data_nascimento", "") or "").lower():
            return False
        if sexo and sexo != (getattr(cliente, "sexo", "") or ""):
            return False
        if observacoes and observacoes not in (getattr(cliente, "observacoes", "") or "").lower():
            return False
        return True

    def _open_pacientes_filter_sidebar(self) -> None:
        if self.menu_state.current_module != "pacientes":
            messagebox.showinfo("Filtro", "Abra o modulo de Pacientes para usar os filtros.")
            return

        if self._filter_sidebar is not None and self._filter_sidebar.winfo_exists():
            self._filter_sidebar.focus()
            return

        sidebar = ctk.CTkToplevel(self)
        sidebar.title("Filtros - Pacientes")
        sidebar.geometry("420x520")
        sidebar.resizable(False, True)
        sidebar.transient(self)
        self._filter_sidebar = sidebar

        frame = ctk.CTkFrame(sidebar, fg_color="#ffffff")
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        for i in range(2):
            frame.grid_columnconfigure(i, weight=1)

        label_font = ctk.CTkFont(size=UI_FONT_PT - 1)
        field_font = ctk.CTkFont(size=UI_FONT_PT)

        def _lbl(text: str, row: int, col: int) -> None:
            ctk.CTkLabel(frame, text=text, font=label_font).grid(row=row, column=col, padx=8, pady=(6, 0), sticky="w")

        _lbl("Nome", 0, 0)
        _lbl("Telefone", 0, 1)
        nome = ctk.CTkEntry(frame, font=field_font)
        telefone = ctk.CTkEntry(frame, font=field_font)
        nome.grid(row=1, column=0, padx=8, pady=(0, 6), sticky="ew")
        telefone.grid(row=1, column=1, padx=8, pady=(0, 6), sticky="ew")

        _lbl("Email", 2, 0)
        _lbl("Nascimento (DD/MM/AAAA)", 2, 1)
        email = ctk.CTkEntry(frame, font=field_font)
        nascimento = ctk.CTkEntry(frame, font=field_font)
        email.grid(row=3, column=0, padx=8, pady=(0, 6), sticky="ew")
        nascimento.grid(row=3, column=1, padx=8, pady=(0, 6), sticky="ew")

        _lbl("Sexo", 4, 0)
        sexo = ctk.CTkOptionMenu(frame, values=["Todos", "Masculino", "Feminino"], font=field_font)
        sexo.grid(row=5, column=0, padx=8, pady=(0, 6), sticky="ew")

        _lbl("Observacoes", 6, 0)
        observacoes = ctk.CTkEntry(frame, font=field_font)
        observacoes.grid(row=7, column=0, columnspan=2, padx=8, pady=(0, 6), sticky="ew")

        # Prefill com filtros atuais
        nome.insert(0, self._paciente_filters["nome"])
        telefone.insert(0, self._paciente_filters["telefone"])
        email.insert(0, self._paciente_filters["email"])
        nascimento.insert(0, self._paciente_filters["nascimento"])
        sexo.set(self._paciente_filters["sexo"] or "Todos")
        observacoes.insert(0, self._paciente_filters["observacoes"])

        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.grid(row=8, column=0, columnspan=2, padx=8, pady=(12, 8), sticky="ew")

        def aplicar() -> None:
            self._paciente_filters = {
                "nome": nome.get().strip(),
                "telefone": telefone.get().strip(),
                "email": email.get().strip(),
                "nascimento": nascimento.get().strip(),
                "sexo": "" if sexo.get() == "Todos" else sexo.get(),
                "observacoes": observacoes.get().strip(),
            }
            if self._pacientes_tree is not None:
                self._refresh_patients_table(self._pacientes_tree)

        def limpar() -> None:
            for w in (nome, telefone, email, nascimento, observacoes):
                w.delete(0, tk.END)
            sexo.set("Todos")
            self._paciente_filters = {k: "" for k in self._paciente_filters}
            if self._pacientes_tree is not None:
                self._refresh_patients_table(self._pacientes_tree)

        ctk.CTkButton(
            btns,
            text="Aplicar filtros",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#7c1229",
            hover_color="#5b0717",
            command=aplicar,
        ).pack(side="left")
        ctk.CTkButton(
            btns,
            text="Limpar filtros",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=limpar,
        ).pack(side="left", padx=(8, 0))

    def _format_idade(self, data_nascimento: str) -> str:
        """Converte DD/MM/AAAA para idade legivel (ex.: 60 anos e 7 meses)."""
        s = (data_nascimento or "").strip()
        if not s:
            return "-"
        try:
            dt = datetime.strptime(s, "%d/%m/%Y").date()
        except ValueError:
            return "-"
        hoje = date.today()
        if dt > hoje:
            return "-"
        anos = hoje.year - dt.year
        meses = hoje.month - dt.month
        if hoje.day < dt.day:
            meses -= 1
        if meses < 0:
            anos -= 1
            meses += 12
        if anos < 0:
            return "-"
        if anos == 0 and meses == 0:
            return "0 meses"
        partes: list[str] = []
        if anos > 0:
            partes.append("1 ano" if anos == 1 else f"{anos} anos")
        if meses > 0:
            partes.append("1 mês" if meses == 1 else f"{meses} meses")
        if len(partes) == 2:
            return f"{partes[0]} e {partes[1]}"
        return partes[0] if partes else "-"

    def _module_label(self, module_id: str) -> str:
        path = find_menu_item_path(self.config_data, module_id)
        if path:
            return str(path[-1].get("label", module_id))
        return module_id.replace("_", " ").title()

    def _build_placeholder(self, module_id: str) -> None:
        title = self._module_label(module_id)
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        box = ctk.CTkFrame(frame, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec")
        box.pack(fill="both", expand=True)
        ctk.CTkLabel(
            box,
            text=f"{title} — em construcao",
            font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
            text_color="#444444",
        ).pack(pady=(40, 8), padx=24)
        ctk.CTkLabel(
            box,
            text="Modulo previsto na versao 2. Sera ligado nas proximas etapas (M2, M3…).",
            font=ctk.CTkFont(size=UI_FONT_PT),
            text_color="#666666",
            wraplength=520,
            justify="center",
        ).pack(pady=(0, 40), padx=24)

    def _build_efm_shell_placeholder(self) -> None:
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        box = ctk.CTkFrame(frame, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec")
        box.pack(fill="both", expand=True)
        ctk.CTkLabel(
            box,
            text=f"{self._module_label('efm_marcadores')} — Plantigrafo",
            font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
            text_color="#444444",
        ).pack(pady=(32, 8), padx=24)
        ctk.CTkLabel(
            box,
            text="Selecione um paciente na ficha clinica (Linha do tempo) e abra a analise\n"
            "a partir do card do momento clinico.\n\n"
            "Atalho: Pacientes → selecionar paciente → «Abrir marcadores» (momento escolhido no EFM).",
            font=ctk.CTkFont(size=UI_FONT_PT),
            text_color="#666666",
            justify="center",
        ).pack(pady=(0, 16), padx=24)
        btn_row = ctk.CTkFrame(box, fg_color="transparent")
        btn_row.pack(pady=(0, 32))
        ctk.CTkButton(
            btn_row,
            text="Ir para Pacientes",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#7c1229",
            hover_color="#5b0717",
            command=lambda: self._show_module("pacientes"),
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            btn_row,
            text="Abrir EFM (modo tecnico)",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=lambda: self._open_efm_marcadores(),
        ).pack(side="left")

    def _open_paciente_hub(self, cliente_id: int, section: str = "resumo") -> None:
        self._hub_cliente_id = cliente_id
        self._hub_section = section
        self._show_module("paciente_hub")

    def _set_hub_section(self, section: str) -> None:
        self._hub_section = section
        if self.menu_state.current_module == "paciente_hub":
            for child in self.content.winfo_children():
                child.destroy()
            self._build_paciente_hub()

    def _hub_momento_stats(self, cliente_id: int) -> dict[int, tuple[int, int]]:
        marc_por_momento: dict[int, int] = {}
        for marc, _img, mom in self.service.marcacoes.listar_marcacoes_por_cliente(cliente_id):
            marc_por_momento[mom.id] = marc_por_momento.get(mom.id, 0) + 1
        stats: dict[int, tuple[int, int]] = {}
        for mom in self.service.marcacoes.listar_momentos_por_cliente(cliente_id):
            n_img = len(self.service.marcacoes.listar_imagens_por_momento(mom.id))
            stats[mom.id] = (n_img, marc_por_momento.get(mom.id, 0))
        return stats

    def _hub_marcacoes_por_momento(
        self, cliente_id: int
    ) -> dict[int, list[tuple[object, object, object]]]:
        grouped: dict[int, list[tuple[object, object, object]]] = defaultdict(list)
        for marc, img, mom in self.service.marcacoes.listar_marcacoes_por_cliente(cliente_id):
            grouped[mom.id].append((marc, img, mom))
        return dict(grouped)

    def _hub_timeline_outlined_btn(self, parent: ctk.CTkFrame, text: str, command: object) -> None:
        ctk.CTkButton(
            parent,
            text=text,
            font=ctk.CTkFont(size=UI_FONT_PT - 2),
            height=28,
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=command,
        ).pack(side="left", padx=(0, 6))

    def _hub_abrir_imagem(self, path_relativo: str, *, rotulo: str) -> None:
        p = resolve_project_file(path_relativo)
        if p is None:
            messagebox.showerror("Marcacoes", f"{rotulo} nao encontrada no disco.")
            return
        self._open_path_external(p)

    @staticmethod
    def _format_lado_plantar(lado: str) -> str:
        labels = {
            "direito": "Direito (D)",
            "esquerdo": "Esquerdo (E)",
            "ambos": "Ambos",
            "nao_informado": "Nao informado",
        }
        return labels.get(lado, (lado or "nao_informado").replace("_", " ").title())

    def _hub_plantigrafo_imagens_agrupadas(
        self, momento_id: int, items: list[tuple[object, object, object]]
    ) -> list[dict[str, object]]:
        by_img: dict[int, dict[str, object]] = {}
        for marc, img, mom in items:
            iid = int(getattr(img, "id", 0))
            if iid not in by_img:
                by_img[iid] = {"img": img, "mom": mom, "marcacoes": []}
            cast_marc = by_img[iid]["marcacoes"]
            assert isinstance(cast_marc, list)
            cast_marc.append(marc)
        for img in self.service.marcacoes.listar_imagens_por_momento(momento_id):
            if img.id not in by_img:
                by_img[img.id] = {"img": img, "mom": None, "marcacoes": []}
        return [by_img[k] for k in sorted(by_img.keys(), reverse=True)]

    def _render_hub_plantigrafo_momento_block(
        self,
        parent: ctk.CTkFrame,
        *,
        cliente_id: int,
        momento_id: int,
        items: list[tuple[object, object, object]],
    ) -> None:
        block = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e8ecf2")
        block.pack(fill="x", padx=14, pady=(0, 10))

        grupos = self._hub_plantigrafo_imagens_agrupadas(momento_id, items)
        n_linhas = sum(
            1
            for g in grupos
            for m in g["marcacoes"]  # type: ignore[union-attr]
            if getattr(m, "tipo_marcador", "") == "plantar_linhas"
        )
        n_pontos = sum(
            1
            for g in grupos
            for m in g["marcacoes"]  # type: ignore[union-attr]
            if getattr(m, "tipo_marcador", "") == "plantar_pontos"
        )
        resumo_partes = [f"{len(grupos)} imagem(ns)"]
        if n_linhas:
            resumo_partes.append(f"Linhas: {n_linhas}")
        if n_pontos:
            resumo_partes.append(f"Pontos: {n_pontos}")
        resumo = " · ".join(resumo_partes)

        ctk.CTkLabel(
            block,
            text="Plantigrafo",
            font=ctk.CTkFont(size=UI_FONT_PT - 1, weight="bold"),
            text_color="#5b0717",
            anchor="w",
        ).pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(
            block,
            text=resumo,
            font=ctk.CTkFont(size=UI_FONT_PT - 2),
            text_color="#666666",
            anchor="w",
        ).pack(anchor="w", padx=12, pady=(0, 8))

        for grupo in grupos:
            img = grupo["img"]
            marcacoes = grupo["marcacoes"]
            assert isinstance(marcacoes, list)
            lado = self._format_lado_plantar(str(getattr(img, "lado", "") or "nao_informado"))
            has_linhas = any(getattr(m, "tipo_marcador", "") == "plantar_linhas" for m in marcacoes)
            has_pontos = any(getattr(m, "tipo_marcador", "") == "plantar_pontos" for m in marcacoes)
            estado: list[str] = []
            if has_linhas:
                estado.append("Linhas salvas")
            if has_pontos:
                estado.append("Pontos salvos")
            if not estado:
                estado.append("Sem marcacoes")
            row = ctk.CTkFrame(block, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=(0, 6))
            ctk.CTkLabel(
                row,
                text=f"· {lado} — {' · '.join(estado)}",
                font=ctk.CTkFont(size=UI_FONT_PT - 2),
                text_color="#444444",
                anchor="w",
            ).pack(side="left", padx=(4, 8))
            btns = ctk.CTkFrame(row, fg_color="transparent")
            btns.pack(side="right")
            imagem_id = int(getattr(img, "id", 0))
            path_original = str(getattr(img, "path_original", ""))
            marc_por_tipo = {str(getattr(m, "tipo_marcador", "")): m for m in marcacoes}
            for tipo_marcador, rotulo_btn in (
                ("plantar_linhas", "Linhas"),
                ("plantar_pontos", "Pontos"),
            ):
                self._hub_timeline_outlined_btn(
                    btns,
                    rotulo_btn,
                    lambda cid=cliente_id, mid=momento_id, iid=imagem_id, tm=tipo_marcador: self._open_efm_marcadores(
                        cliente_id=cid, momento_id=mid, imagem_id=iid, tipo_marcador=tm
                    ),
                )
            self._hub_timeline_outlined_btn(
                btns,
                "Original",
                lambda p=path_original: self._hub_abrir_imagem(p, rotulo="Imagem original"),
            )
            for tipo_marcador, rotulo_btn in (("plantar_linhas", "Marcada L"), ("plantar_pontos", "Marcada P")):
                marc = marc_por_tipo.get(tipo_marcador)
                if marc is None:
                    continue
                path_marcada = str(getattr(marc, "path_png_marcado", ""))
                self._hub_timeline_outlined_btn(
                    btns,
                    rotulo_btn,
                    lambda p=path_marcada: self._hub_abrir_imagem(p, rotulo="Imagem marcada"),
                )

        btn_row = ctk.CTkFrame(block, fg_color="transparent")
        btn_row.pack(anchor="w", padx=12, pady=(0, 10))
        ctk.CTkButton(
            btn_row,
            text="Abrir Plantigrafo neste momento",
            font=ctk.CTkFont(size=UI_FONT_PT - 2),
            fg_color="#7c1229",
            hover_color="#5b0717",
            height=30,
            command=lambda cid=cliente_id, mid=momento_id: self._open_efm_marcadores(cliente_id=cid, momento_id=mid),
        ).pack(side="left")

        ctk.CTkLabel(block, text="").pack(pady=2)

    @staticmethod
    def _hub_momentos_agrupados_por_dia(momentos: list[object]) -> list[tuple[date, list[object]]]:
        grupos: dict[date, list[object]] = {}
        ordem_dias: list[date] = []
        for mom in momentos:
            ref = getattr(mom, "data_referencia", None)
            if ref is None:
                continue
            dia = ref.date() if hasattr(ref, "date") else ref
            if dia not in grupos:
                grupos[dia] = []
                ordem_dias.append(dia)
            grupos[dia].append(mom)
        return [(d, grupos[d]) for d in ordem_dias]

    def _render_hub_momento_subcard(
        self,
        parent: ctk.CTkFrame,
        *,
        cliente_id: int,
        mom: object,
        marcacoes_por_mom: dict[int, list[tuple[object, object, object]]],
    ) -> None:
        rotulo = (getattr(mom, "rotulo", "") or "Momento").strip()
        ref = getattr(mom, "data_referencia", None)
        hora = ref.strftime("%H:%M") if ref is not None else "--:--"
        momento_id = int(getattr(mom, "id", 0))

        card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=8, border_width=1, border_color="#e4e8ef")
        card.pack(fill="x", padx=12, pady=(0, 8))

        titulo_row = ctk.CTkFrame(card, fg_color="transparent")
        titulo_row.pack(fill="x", padx=12, pady=(10, 0))
        ctk.CTkLabel(
            titulo_row,
            text=f"{hora} — {rotulo}",
            font=ctk.CTkFont(size=UI_FONT_PT - 1, weight="bold"),
            text_color="#333333",
            anchor="w",
        ).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            titulo_row,
            text="Editar",
            width=72,
            height=28,
            font=ctk.CTkFont(size=UI_FONT_PT - 2),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=lambda mid=momento_id: self._hub_dialog_editar_momento(cliente_id, mid),
        ).pack(side="right")

        obs_mom = (getattr(mom, "observacoes", "") or "").strip()
        if obs_mom:
            ctk.CTkLabel(
                card,
                text=obs_mom,
                font=ctk.CTkFont(size=UI_FONT_PT - 2),
                text_color="#555555",
                wraplength=520,
                justify="left",
                anchor="w",
            ).pack(anchor="w", padx=12, pady=(6, 8))
        else:
            ctk.CTkLabel(card, text="").pack(pady=2)

        items = marcacoes_por_mom.get(momento_id, [])
        if items or self.service.marcacoes.listar_imagens_por_momento(momento_id):
            self._render_hub_plantigrafo_momento_block(
                card, cliente_id=cliente_id, momento_id=momento_id, items=items
            )
        else:
            ctk.CTkLabel(
                card,
                text="Ainda sem exames neste momento. Use «Abrir Plantigrafo» abaixo\n"
                "ou o atalho Plantigrafo na barra lateral da ficha.",
                font=ctk.CTkFont(size=UI_FONT_PT - 2),
                text_color="#888888",
                wraplength=520,
                justify="left",
                anchor="w",
            ).pack(anchor="w", padx=12, pady=(0, 8))
            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(anchor="w", padx=12, pady=(0, 10))
            ctk.CTkButton(
                btn_row,
                text="Abrir Plantigrafo (Analise)",
                font=ctk.CTkFont(size=UI_FONT_PT - 2),
                fg_color="#7c1229",
                hover_color="#5b0717",
                height=30,
                command=lambda cid=cliente_id, mid=momento_id: self._open_efm_marcadores(cliente_id=cid, momento_id=mid),
            ).pack(side="left")

    def _render_hub_dia_timeline_group(
        self,
        parent: ctk.CTkScrollableFrame,
        *,
        dia: date,
        momentos_dia: list[object],
        cliente_id: int,
        marcacoes_por_mom: dict[int, list[tuple[object, object, object]]],
    ) -> None:
        n = len(momentos_dia)
        contagem = "1 momento" if n == 1 else f"{n} momentos"
        group = ctk.CTkFrame(parent, fg_color="#eef1f6", corner_radius=10, border_width=1, border_color="#d8dee8")
        group.pack(fill="x", padx=18, pady=(0, 14))
        ctk.CTkLabel(
            group,
            text=f"{dia.strftime('%d/%m/%Y')}  ·  {contagem}",
            font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
            text_color="#5b0717",
            anchor="w",
        ).pack(anchor="w", padx=14, pady=(12, 8))
        for mom in momentos_dia:
            self._render_hub_momento_subcard(
                group,
                cliente_id=cliente_id,
                mom=mom,
                marcacoes_por_mom=marcacoes_por_mom,
            )
        ctk.CTkLabel(group, text="").pack(pady=2)

    def _hub_dialog_novo_momento(self, cliente_id: int) -> None:
        self._hub_dialog_momento(cliente_id, momento_id=None)

    def _hub_dialog_editar_momento(self, cliente_id: int, momento_id: int) -> None:
        self._hub_dialog_momento(cliente_id, momento_id=momento_id)

    def _hub_dialog_momento(self, cliente_id: int, *, momento_id: int | None) -> None:
        editando = momento_id is not None
        momento = self.service.marcacoes.obter_momento(momento_id) if editando else None
        if editando and momento is None:
            messagebox.showerror("Momento clinico", "Momento nao encontrado.")
            return

        dlg = ctk.CTkToplevel(self)
        dlg.title("Editar momento clinico" if editando else "Novo momento clinico")
        dlg.geometry("460x420")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        frame = ctk.CTkFrame(dlg, fg_color="#ffffff")
        frame.pack(fill="both", expand=True, padx=16, pady=16)

        if editando and momento is not None:
            when_txt = momento.data_referencia.strftime("%d/%m/%Y %H:%M")
            ctk.CTkLabel(
                frame,
                text=f"Data e hora do registo: {when_txt}",
                font=ctk.CTkFont(size=UI_FONT_PT - 2),
                text_color="#666666",
                anchor="w",
            ).pack(anchor="w", pady=(0, 10))
        else:
            ctk.CTkLabel(
                frame,
                text="Registo do que foi feito neste atendimento (data/hora gravadas ao criar).\n"
                "Depois associe exames no Plantigrafo ou Podoscopio a este momento.",
                font=ctk.CTkFont(size=UI_FONT_PT - 2),
                text_color="#666666",
                wraplength=400,
                justify="left",
            ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            frame,
            text=f"Rotulo (max. {MOMENTO_ROTULO_MAX} caracteres)",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            text_color="#333333",
        ).pack(anchor="w", pady=(0, 4))
        rotulo_entry = ctk.CTkEntry(frame, font=ctk.CTkFont(size=UI_FONT_PT), height=36)
        rotulo_entry.pack(fill="x", pady=(0, 10))
        now = datetime.now()
        if editando and momento is not None:
            rotulo_entry.insert(0, (momento.rotulo or "").strip())
        else:
            rotulo_entry.insert(0, f"Consulta {now.strftime('%d/%m/%Y')}")

        ctk.CTkLabel(
            frame,
            text=f"Observacoes — o que foi feito (max. {MOMENTO_OBSERVACOES_MAX} caracteres)",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            text_color="#333333",
        ).pack(anchor="w", pady=(0, 4))
        obs_box = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            height=120,
            border_width=1,
            border_color="#b8b8b8",
            fg_color="#ffffff",
        )
        obs_box.pack(fill="x", pady=(0, 8))
        if editando and momento is not None and (momento.observacoes or "").strip():
            obs_box.insert("1.0", (momento.observacoes or "").strip())

        def gravar() -> None:
            rotulo = rotulo_entry.get()
            obs = obs_box.get("1.0", "end-1c")
            try:
                if editando and momento_id is not None:
                    self.service.atualizar_momento_clinico(momento_id, rotulo, obs)
                else:
                    self.service.criar_momento_clinico(cliente_id, rotulo, now, obs)
            except ValueError as exc:
                messagebox.showerror("Momento clinico", str(exc), parent=dlg)
                return
            dlg.destroy()
            self._set_hub_section("timeline")
            if editando:
                messagebox.showinfo("Momento clinico", "Momento actualizado.")
            else:
                messagebox.showinfo(
                    "Momento clinico",
                    "Momento criado.\n\n"
                    "Na Linha do tempo aparece o card. Para exames e marcacoes:\n"
                    "Plantigrafo → Analise ou Abrir marcadores em Pacientes.",
                )

        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.pack(fill="x", pady=(8, 0))
        ctk.CTkButton(
            btns,
            text="Cancelar",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=dlg.destroy,
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            btns,
            text="Gravar",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            fg_color="#7c1229",
            hover_color="#5b0717",
            command=gravar,
        ).pack(side="right")

        rotulo_entry.focus_set()
        dlg.after(100, rotulo_entry.focus_set)

    def _hub_atalho_modulo(self, modulo: str) -> None:
        cliente_id = self._hub_cliente_id
        if not cliente_id:
            messagebox.showinfo("Ficha clinica", "Nenhum paciente seleccionado.")
            return
        if modulo == "podoscopio":
            messagebox.showinfo(
                "Ficha clinica",
                "Atalho Podoscopio com contexto do paciente chega numa etapa futura.\n\n"
                "Por agora use Podoscopio no menu lateral.",
            )
            return
        if modulo != "plantigrafo":
            return
        momentos = self.service.marcacoes.listar_momentos_por_cliente(cliente_id)
        if not momentos:
            if messagebox.askyesno(
                "Plantigrafo",
                "Este paciente ainda nao tem momentos clinicos.\n\nDeseja criar um agora?",
            ):
                self._hub_dialog_novo_momento(cliente_id)
                momentos = self.service.marcacoes.listar_momentos_por_cliente(cliente_id)
        if not momentos:
            return
        momento_id = int(momentos[0].id)
        self._open_efm_marcadores(cliente_id=cliente_id, momento_id=momento_id)

    def _build_paciente_hub(self) -> None:
        cliente_id = self._hub_cliente_id
        if not cliente_id:
            messagebox.showinfo("Ficha clinica", "Nenhum paciente seleccionado.")
            self._show_module("pacientes")
            return
        cliente = self.service.clientes.obter_por_id(cliente_id)
        if cliente is None:
            messagebox.showerror("Ficha clinica", "Paciente nao encontrado.")
            self._hub_cliente_id = None
            self._show_module("pacientes")
            return

        root = ctk.CTkFrame(self.content, fg_color="transparent")
        root.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(root, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec")
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            hdr,
            text="← Pacientes",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            width=120,
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=lambda: self._show_module("pacientes"),
        ).grid(row=0, column=0, padx=(14, 10), pady=14, sticky="w")

        idade_txt = self._format_idade(cliente.data_nascimento or "")
        titulo = f"{cliente.nome}  (#{cliente.id})"
        if idade_txt != "-":
            titulo += f"  ·  {idade_txt}"
        ctk.CTkLabel(
            hdr,
            text=titulo,
            font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
            text_color="#333333",
        ).grid(row=0, column=1, sticky="w", pady=14)

        def _editar_cadastro() -> None:
            self._pending_paciente_edit_id = cliente.id
            self._show_module("pacientes")

        ctk.CTkButton(
            hdr,
            text="Editar cadastro",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            fg_color="#7c1229",
            hover_color="#5b0717",
            command=_editar_cadastro,
        ).grid(row=0, column=2, padx=14, pady=14, sticky="e")

        body = ctk.CTkFrame(root, fg_color="transparent")
        body.grid(row=1, column=0, columnspan=2, sticky="nsew")
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        nav = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec", width=210)
        nav.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
        nav.grid_propagate(False)

        nav_sections: tuple[tuple[str, str, bool], ...] = (
            ("resumo", "Resumo", True),
            ("timeline", "Linha do tempo", True),
            ("laudos", "Laudos", False),
            ("palmilhas", "Palmilhas", False),
        )
        ctk.CTkLabel(
            nav,
            text="Secoes",
            font=ctk.CTkFont(size=UI_FONT_PT - 1, weight="bold"),
            text_color="#333333",
        ).pack(anchor="w", padx=14, pady=(14, 8))

        for sec_id, label, enabled in nav_sections:
            active = self._hub_section == sec_id
            if enabled:
                ctk.CTkButton(
                    nav,
                    text=label,
                    font=ctk.CTkFont(size=UI_FONT_PT - 1),
                    anchor="w",
                    height=36,
                    fg_color="#dbe8ff" if active else "#ffffff",
                    text_color="#232323",
                    hover_color="#e9eefc",
                    command=lambda s=sec_id: self._set_hub_section(s),
                ).pack(fill="x", padx=12, pady=3)
            else:
                ctk.CTkButton(
                    nav,
                    text=f"{label}  (em breve)",
                    font=ctk.CTkFont(size=UI_FONT_PT - 2),
                    anchor="w",
                    height=36,
                    fg_color="#f4f4f4",
                    text_color="#999999",
                    hover_color="#f4f4f4",
                    state="disabled",
                ).pack(fill="x", padx=12, pady=3)

        ctk.CTkLabel(nav, text="Atalhos", font=ctk.CTkFont(size=UI_FONT_PT - 2, weight="bold"), text_color="#666666").pack(
            anchor="w", padx=14, pady=(16, 6)
        )
        for mod_id, mod_label in (("plantigrafo", "Plantigrafo"), ("podoscopio", "Podoscopio")):
            ctk.CTkButton(
                nav,
                text=mod_label,
                font=ctk.CTkFont(size=UI_FONT_PT - 2),
                anchor="w",
                height=32,
                fg_color="#ffffff",
                text_color="#7c1229",
                hover_color="#f0dbe1",
                border_width=1,
                border_color="#dcc0c6",
                command=lambda m=mod_id: self._hub_atalho_modulo(m),
            ).pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(nav, text="").pack(pady=8)

        self._hub_content_host = ctk.CTkScrollableFrame(
            body,
            fg_color="#ffffff",
            corner_radius=12,
            border_width=1,
            border_color="#ececec",
            scrollbar_button_color="#b8b8b8",
            scrollbar_button_hover_color="#7c1229",
        )
        self._hub_content_host.grid(row=0, column=1, sticky="nsew")
        self._render_hub_section_content()

    def _render_hub_section_content(self) -> None:
        host = self._hub_content_host
        cliente_id = self._hub_cliente_id
        if host is None or not cliente_id:
            return
        for child in host.winfo_children():
            child.destroy()
        cliente = self.service.clientes.obter_por_id(cliente_id)
        if cliente is None:
            return

        section = self._hub_section
        pad = {"padx": 18, "pady": (16, 8)}

        if section == "resumo":
            ctk.CTkLabel(
                host,
                text="Resumo",
                font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
                text_color="#333333",
            ).pack(anchor="w", **pad)
            imc_val = formatar_imc(calcular_imc(cliente.altura_m, cliente.peso_kg))
            linhas = [
                f"Sexo: {(cliente.sexo or '—')}",
                f"Telefone: {(cliente.telefone or '—')}",
                f"Email: {(cliente.email or '—')}",
                f"Altura: {formatar_altura(cliente.altura_m) or '—'} m",
                f"Peso: {formatar_peso(cliente.peso_kg) or '—'} kg",
                f"IMC: {imc_val}",
                f"Lateralidade: {(cliente.lateralidade or '—')}",
            ]
            for ln in linhas:
                ctk.CTkLabel(host, text=ln, font=ctk.CTkFont(size=UI_FONT_PT - 1), text_color="#444444", anchor="w").pack(
                    anchor="w", padx=18, pady=2
                )
            ctk.CTkLabel(
                host,
                text="Avaliacao inicial (observacoes do cadastro)",
                font=ctk.CTkFont(size=UI_FONT_PT - 1, weight="bold"),
                text_color="#333333",
            ).pack(anchor="w", padx=18, pady=(16, 6))
            obs_txt = (cliente.observacoes or "").strip() or "Sem observacoes registadas."
            ctk.CTkLabel(
                host,
                text=obs_txt,
                font=ctk.CTkFont(size=UI_FONT_PT - 1),
                text_color="#555555",
                wraplength=640,
                justify="left",
            ).pack(anchor="w", padx=18, pady=(0, 12))
            ctk.CTkLabel(host, text="Ultimos laudos: nenhum laudo registado (fase v2).", font=ctk.CTkFont(size=UI_FONT_PT - 2), text_color="#888888").pack(
                anchor="w", padx=18, pady=2
            )
            ctk.CTkLabel(host, text="Palmilhas em andamento: nenhum pedido (fase v3).", font=ctk.CTkFont(size=UI_FONT_PT - 2), text_color="#888888").pack(
                anchor="w", padx=18, pady=2
            )
            ctk.CTkButton(
                host,
                text="+ Novo momento clinico",
                font=ctk.CTkFont(size=UI_FONT_PT - 1),
                fg_color="#7c1229",
                hover_color="#5b0717",
                command=lambda: self._hub_dialog_novo_momento(cliente_id),
            ).pack(anchor="w", padx=18, pady=(18, 24))
            return

        if section == "timeline":
            ctk.CTkLabel(
                host,
                text="Linha do tempo",
                font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
                text_color="#333333",
            ).pack(anchor="w", **pad)
            momentos = self.service.marcacoes.listar_momentos_por_cliente(cliente_id)
            marcacoes_por_mom = self._hub_marcacoes_por_momento(cliente_id)
            if not momentos:
                ctk.CTkLabel(
                    host,
                    text="Nenhum momento clinico. Use «Novo momento» no Resumo ou crie marcacoes no Plantigrafo.",
                    font=ctk.CTkFont(size=UI_FONT_PT - 1),
                    text_color="#666666",
                    wraplength=640,
                    justify="left",
                ).pack(anchor="w", padx=18, pady=(0, 16))
                ctk.CTkButton(
                    host,
                    text="+ Novo momento clinico",
                    font=ctk.CTkFont(size=UI_FONT_PT - 1),
                    fg_color="#7c1229",
                    hover_color="#5b0717",
                    command=lambda: self._hub_dialog_novo_momento(cliente_id),
                ).pack(anchor="w", padx=18, pady=(0, 24))
                return
            for dia, momentos_dia in self._hub_momentos_agrupados_por_dia(momentos):
                self._render_hub_dia_timeline_group(
                    host,
                    dia=dia,
                    momentos_dia=momentos_dia,
                    cliente_id=cliente_id,
                    marcacoes_por_mom=marcacoes_por_mom,
                )
            ctk.CTkButton(
                host,
                text="+ Novo momento clinico",
                font=ctk.CTkFont(size=UI_FONT_PT - 1),
                fg_color="#7c1229",
                hover_color="#5b0717",
                command=lambda: self._hub_dialog_novo_momento(cliente_id),
            ).pack(anchor="w", padx=18, pady=(8, 24))
            return

        ctk.CTkLabel(
            host,
            text="Secao em construcao.",
            font=ctk.CTkFont(size=UI_FONT_PT),
            text_color="#666666",
        ).pack(pady=40)

    def _build_paciente_hub_placeholder(self) -> None:
        self._build_placeholder("paciente_hub")

    def _build_module_hub(
        self,
        *,
        parent_id: str,
        intro: str,
        child_ids: tuple[str, ...],
    ) -> None:
        root = ctk.CTkFrame(self.content, fg_color="transparent")
        root.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        box = ctk.CTkFrame(root, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec")
        box.pack(fill="both", expand=True)
        ctk.CTkLabel(
            box,
            text=self._module_label(parent_id),
            font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
            text_color="#333333",
        ).pack(anchor="w", padx=18, pady=(18, 6))
        ctk.CTkLabel(
            box,
            text=intro,
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            text_color="#666666",
            wraplength=640,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 14))
        for cid in child_ids:
            ctk.CTkButton(
                box,
                text=self._module_label(cid),
                font=ctk.CTkFont(size=UI_FONT_PT),
                anchor="w",
                height=40,
                fg_color="#7c1229",
                hover_color="#5b0717",
                command=lambda m=cid: self._show_module(m),
            ).pack(fill="x", padx=18, pady=(0, 8))
        ctk.CTkLabel(box, text="").pack(pady=4)

    def _build_plantigrafo_hub(self) -> None:
        self._build_module_hub(
            parent_id="plantigrafo",
            intro="Analise de imagens plantares (EFM), laudos e configuracao das regras de marcadores.",
            child_ids=("efm_marcadores", "plantigrafo_laudos", "plantigrafo_config"),
        )

    def _build_avaliacao_postural_hub(self) -> None:
        self._build_module_hub(
            parent_id="avaliacao_postural",
            intro="Modulo de avaliacao postural (em construcao).",
            child_ids=("postural_avaliacao", "postural_laudos", "postural_config"),
        )

    def _build_modulos_hub(self) -> None:
        self._build_plantigrafo_hub()

    @staticmethod
    def _podoscopio_text_get(widget: tk.Text) -> str:
        return widget.get("1.0", "end-1c").strip()

    @staticmethod
    def _podoscopio_text_set(widget: tk.Text, texto: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        if texto:
            widget.insert("1.0", texto)

    def _podoscopio_multiline(self, parent: ctk.CTkFrame, *, lines: int = 4) -> tuple[ctk.CTkFrame, tk.Text]:
        """tk.Text evita falha de foco do CTkTextbox dentro de CTkScrollableFrame."""
        frame = ctk.CTkFrame(parent, fg_color="#F9F9FA", border_width=1, border_color="#979DA2", corner_radius=6)
        text = tk.Text(
            frame,
            height=lines,
            font=("Segoe UI", UI_FONT_PT - 1),
            wrap="word",
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#979DA2",
            highlightcolor="#7c1229",
            bg="#F9F9FA",
            fg="#1a1a1a",
            insertbackground="#1a1a1a",
            padx=8,
            pady=8,
        )
        text.pack(fill="both", expand=True, padx=2, pady=2)
        text.bind("<Button-1>", lambda _e: text.focus_set())
        return frame, text

    def _build_podoscopio_hub(self) -> None:
        self._build_module_hub(
            parent_id="podoscopio",
            intro="Ficha tecnica, laudos e configuracoes do podoscopio. Selecione uma opcao abaixo ou use o menu lateral.",
            child_ids=("podoscopio_ficha_tecnica", "podoscopio_laudos", "podoscopio_config"),
        )

    def _build_podoscopio_ficha_tecnica(self) -> None:
        """Ficha tecnica de podoscopia: edicao, gravacao na BD e exportacao PDF."""
        root = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent",
            scrollbar_button_color="#b8b8b8",
            scrollbar_button_hover_color="#7c1229",
        )
        root.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        root.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(root, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ctk.CTkLabel(
            header,
            text="Podoscopio / Ficha tecnica",
            font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
            text_color="#333333",
        ).pack(anchor="w", padx=14, pady=(12, 2))
        status_label = ctk.CTkLabel(
            header,
            text="Selecione o paciente. PDF da ficha traz so os campos desta avaliacao; cadastro do paciente em Pacientes.",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            text_color="#666666",
        )
        status_label.pack(anchor="w", padx=14, pady=(0, 12))

        form_top = ctk.CTkFrame(root, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec")
        form_top.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        form_top.grid_columnconfigure(1, weight=1)

        scroll_host = ctk.CTkFrame(
            root,
            fg_color="#ffffff",
            corner_radius=12,
            border_width=1,
            border_color="#ececec",
        )
        scroll_host.grid(row=2, column=0, sticky="ew")
        scroll_host.grid_columnconfigure(1, weight=1)

        btn_row = ctk.CTkFrame(root, fg_color="transparent")
        btn_row.grid(row=3, column=0, sticky="ew", pady=(8, 0))

        clientes = self.service.clientes.listar()
        paciente_labels = ["— Selecione o paciente —"] + [f"#{c.id} — {c.nome}" for c in clientes]
        by_paciente_label: dict[str, int] = {f"#{c.id} — {c.nome}": c.id for c in clientes}
        ficha_atual_id: list[int | None] = [None]
        fichas_by_label: dict[str, int] = {}
        press_vars: dict[str, tk.BooleanVar] = {}

        row = 0

        def section(title: str) -> None:
            nonlocal row
            ctk.CTkLabel(
                scroll_host,
                text=title,
                font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
                text_color="#7c1229",
            ).grid(row=row, column=0, columnspan=2, sticky="w", padx=14, pady=(14, 6))
            row += 1

        row_top = 0

        def field_on(
            parent: ctk.CTkFrame,
            label: str,
            widget: ctk.CTkBaseClass,
            *,
            row_idx: list[int],
            col_span: int = 1,
        ) -> None:
            ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=UI_FONT_PT - 1), text_color="#444444").grid(
                row=row_idx[0], column=0, sticky="nw", padx=(14, 8), pady=4
            )
            widget.grid(row=row_idx[0], column=1, sticky="ew", padx=(0, 14), pady=4, columnspan=col_span)
            row_idx[0] += 1

        def field(label: str, widget: ctk.CTkBaseClass, *, col_span: int = 1) -> None:
            nonlocal row
            ctk.CTkLabel(
                scroll_host,
                text=label,
                font=ctk.CTkFont(size=UI_FONT_PT - 1),
                text_color="#444444",
            ).grid(row=row, column=0, sticky="nw", padx=(14, 8), pady=6)
            widget.grid(row=row, column=1, sticky="ew", padx=(0, 14), pady=6, columnspan=col_span)
            row += 1

        def section_on(parent: ctk.CTkFrame, title: str, row_idx: list[int]) -> None:
            ctk.CTkLabel(
                parent,
                text=title,
                font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
                text_color="#7c1229",
            ).grid(row=row_idx[0], column=0, columnspan=2, sticky="w", padx=14, pady=(14, 6))
            row_idx[0] += 1

        def _cliente_id() -> int | None:
            label = var_paciente.get().strip()
            if label.startswith("#") and label in by_paciente_label:
                return by_paciente_label[label]
            return None

        def _label_ficha(ficha) -> str:
            rot = (ficha.rotulo_atendimento or "Sem rotulo").strip()
            return f"#{ficha.id} — {ficha.data_avaliacao.strftime('%d/%m/%Y %H:%M')} — {rot}"

        def _selecionar_ficha_no_combo(ficha_id: int) -> bool:
            for lbl, fid in fichas_by_label.items():
                if fid == ficha_id:
                    var_ficha.set(lbl)
                    return True
            return False

        def _refresh_fichas_combo(*, select_ficha_id: int | None = None) -> None:
            fichas_by_label.clear()
            cid = _cliente_id()
            if cid is None:
                combo_ficha.configure(values=["— Nova ficha —"], state="disabled")
                var_ficha.set("— Nova ficha —")
                return
            regs = self.service.fichas_podoscopio.listar_por_cliente(cid)
            labels_f = ["— Nova ficha —"]
            for f in regs:
                lbl = _label_ficha(f)
                labels_f.append(lbl)
                fichas_by_label[lbl] = f.id
            combo_ficha.configure(values=labels_f, state="readonly")
            if select_ficha_id is not None and _selecionar_ficha_no_combo(select_ficha_id):
                return
            var_ficha.set(labels_f[0])

        def _limpar_formulario(*, manter_paciente: bool = True) -> None:
            ficha_atual_id[0] = None
            if not manter_paciente:
                var_paciente.set(paciente_labels[0])
            data_entry.delete(0, "end")
            data_entry.insert(0, datetime.now().strftime("%d/%m/%Y %H:%M"))
            rotulo_entry.delete(0, "end")
            self._podoscopio_text_set(queixa_text, "")
            arco_d.set("Nao avaliado")
            arco_e.set("Nao avaliado")
            apoio_d.set("Nao avaliado")
            apoio_e.set("Nao avaliado")
            simetria.set("Nao avaliado")
            for v in press_vars.values():
                v.set(False)
            self._podoscopio_text_set(obs_text, "")
            status_label.configure(text="Nova ficha — preencha e clique em Salvar.")

        def _carregar_ficha(ficha_id: int) -> None:
            ficha = self.service.fichas_podoscopio.obter_por_id(ficha_id)
            if not ficha:
                messagebox.showerror("Ficha tecnica", "Ficha nao encontrada.")
                return
            cliente = self.service.clientes.obter_por_id(ficha.cliente_id)
            if cliente:
                pl = f"#{cliente.id} — {cliente.nome}"
                if pl in by_paciente_label:
                    var_paciente.set(pl)
            ficha_atual_id[0] = ficha.id
            data_entry.delete(0, "end")
            data_entry.insert(0, ficha.data_avaliacao.strftime("%d/%m/%Y %H:%M"))
            rotulo_entry.delete(0, "end")
            rotulo_entry.insert(0, ficha.rotulo_atendimento or "")
            self._podoscopio_text_set(queixa_text, ficha.queixa_objetivo or "")
            arco_d.set(ficha.arco_pe_direito)
            arco_e.set(ficha.arco_pe_esquerdo)
            apoio_d.set(ficha.apoio_pe_direito)
            apoio_e.set(ficha.apoio_pe_esquerdo)
            simetria.set(ficha.simetria_carga)
            for v in press_vars.values():
                v.set(False)
            for z in (ficha.hiperpressao_zonas or "").split(";"):
                z = z.strip()
                if z in press_vars:
                    press_vars[z].set(True)
            self._podoscopio_text_set(obs_text, ficha.observacoes or "")
            self._podoscopio_ctx = {"cliente_id": ficha.cliente_id, "ficha_id": ficha.id}
            status_label.configure(
                text=f"Ficha #{ficha.id} carregada. Ultima atualizacao: {ficha.atualizado_em.strftime('%d/%m/%Y %H:%M')}."
            )

        def _coletar_zonas() -> list[str]:
            return [nome for nome, var in press_vars.items() if var.get()]

        def _salvar_ficha() -> None:
            cid = _cliente_id()
            if cid is None:
                messagebox.showinfo("Ficha tecnica", "Selecione um paciente cadastrado em Pacientes.")
                return
            try:
                ficha = self.service.salvar_ficha_podoscopio(
                    cid,
                    data_entry.get().strip(),
                    rotulo_entry.get().strip(),
                    self._podoscopio_text_get(queixa_text),
                    arco_d.get(),
                    arco_e.get(),
                    apoio_d.get(),
                    apoio_e.get(),
                    simetria.get(),
                    _coletar_zonas(),
                    self._podoscopio_text_get(obs_text),
                    ficha_id=ficha_atual_id[0],
                )
            except ValueError as exc:
                messagebox.showerror("Ficha tecnica", str(exc))
                return
            ficha_atual_id[0] = ficha.id
            self._podoscopio_ctx = {"cliente_id": cid, "ficha_id": ficha.id}
            _refresh_fichas_combo(select_ficha_id=ficha.id)
            status_label.configure(
                text=f"Ficha #{ficha.id} gravada ({ficha.atualizado_em.strftime('%d/%m/%Y %H:%M')}). "
                "Use «Ficha salva» para abrir outra avaliacao deste paciente."
            )
            messagebox.showinfo("Ficha tecnica", f"Ficha #{ficha.id} salva.")

        def _exportar_pdf_branco() -> None:
            default_name = "Ficha_Podoscopio_EM_BRANCO.pdf"
            dest = filedialog.asksaveasfilename(
                title="PDF em branco (preencher a caneta)",
                defaultextension=".pdf",
                initialfile=default_name,
                filetypes=[("PDF", "*.pdf")],
            )
            if not dest:
                return
            try:
                export_ficha_podoscopio_pdf_branco(Path(dest))
            except Exception as exc:
                messagebox.showerror("Ficha tecnica", f"Falha ao gerar PDF:\n{exc}")
                return
            status_label.configure(text=f"PDF em branco exportado: {dest}")
            messagebox.showinfo("Ficha tecnica", f"PDF para impressao/caneta:\n{dest}")

        def _exportar_pdf_preenchida() -> None:
            cid = _cliente_id()
            if cid is None:
                messagebox.showinfo("Ficha tecnica", "Selecione um paciente antes de exportar a ficha preenchida.")
                return
            try:
                ficha = self.service.salvar_ficha_podoscopio(
                    cid,
                    data_entry.get().strip(),
                    rotulo_entry.get().strip(),
                    self._podoscopio_text_get(queixa_text),
                    arco_d.get(),
                    arco_e.get(),
                    apoio_d.get(),
                    apoio_e.get(),
                    simetria.get(),
                    _coletar_zonas(),
                    self._podoscopio_text_get(obs_text),
                    ficha_id=ficha_atual_id[0],
                )
            except ValueError as exc:
                messagebox.showerror("Ficha tecnica", str(exc))
                return
            ficha_atual_id[0] = ficha.id
            self._podoscopio_ctx = {"cliente_id": cid, "ficha_id": ficha.id}
            _refresh_fichas_combo(select_ficha_id=ficha.id)
            cliente = self.service.clientes.obter_por_id(cid)
            if not cliente:
                return
            nome_safe = "".join(ch if ch.isalnum() or ch in " -_" else "_" for ch in cliente.nome)[:40]
            default_name = f"Ficha_Podoscopio_PREENCHIDA_{nome_safe}_{ficha.data_avaliacao.strftime('%Y%m%d')}.pdf"
            dest = filedialog.asksaveasfilename(
                title="PDF preenchida (dados do sistema)",
                defaultextension=".pdf",
                initialfile=default_name,
                filetypes=[("PDF", "*.pdf")],
            )
            if not dest:
                return
            try:
                export_ficha_podoscopio_pdf_preenchida(Path(dest), ficha=ficha, paciente_nome=cliente.nome)
            except Exception as exc:
                messagebox.showerror("Ficha tecnica", f"Falha ao gerar PDF:\n{exc}")
                return
            status_label.configure(text=f"PDF preenchida exportado: {dest}")
            messagebox.showinfo("Ficha tecnica", f"PDF com dados do sistema:\n{dest}")

        def _on_paciente_change(_choice: str = "") -> None:
            cid = _cliente_id()
            _refresh_fichas_combo()
            if cid is None:
                self._podoscopio_ctx = {"cliente_id": None, "ficha_id": None}
                _limpar_formulario(manter_paciente=True)
                return
            self._podoscopio_ctx["cliente_id"] = cid
            regs = self.service.fichas_podoscopio.listar_por_cliente(cid)
            if regs:
                ultima = regs[0]
                _carregar_ficha(ultima.id)
                _refresh_fichas_combo(select_ficha_id=ultima.id)
                status_label.configure(
                    text=f"Ultima ficha do paciente carregada (#{ultima.id}). "
                    "Escolha «Nova ficha» ou outra entrada em «Ficha salva»."
                )
            else:
                self._podoscopio_ctx["ficha_id"] = None
                _limpar_formulario(manter_paciente=True)
                var_ficha.set("— Nova ficha —")

        def _on_ficha_change(choice: str) -> None:
            if choice == "— Nova ficha —":
                _limpar_formulario(manter_paciente=True)
                return
            fid = fichas_by_label.get(choice)
            if fid is not None:
                _carregar_ficha(fid)
                self._podoscopio_ctx["ficha_id"] = fid

        row_ident = [0]
        section_on(form_top, "Identificacao", row_ident)
        var_paciente = tk.StringVar(value=paciente_labels[0])
        combo_paciente = ctk.CTkComboBox(
            form_top,
            values=paciente_labels,
            variable=var_paciente,
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            state="readonly" if clientes else "disabled",
            command=_on_paciente_change,
        )
        field_on(form_top, "Paciente *", combo_paciente, row_idx=row_ident)

        var_ficha = tk.StringVar(value="— Nova ficha —")
        combo_ficha = ctk.CTkComboBox(
            form_top,
            values=["— Nova ficha —"],
            variable=var_ficha,
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            state="disabled",
            command=_on_ficha_change,
        )
        field_on(form_top, "Ficha salva", combo_ficha, row_idx=row_ident)
        ctk.CTkLabel(
            form_top,
            text="Apos salvar, a ficha aparece aqui. Ao voltar nesta tela, selecione o paciente para recarregar.",
            font=ctk.CTkFont(size=UI_FONT_PT - 2),
            text_color="#888888",
            wraplength=720,
            justify="left",
        ).grid(row=row_ident[0], column=0, columnspan=2, sticky="w", padx=14, pady=(0, 8))
        row_ident[0] += 1

        data_entry = ctk.CTkEntry(form_top, font=ctk.CTkFont(size=UI_FONT_PT - 1))
        data_entry.insert(0, datetime.now().strftime("%d/%m/%Y %H:%M"))
        field_on(form_top, "Data da avaliacao", data_entry, row_idx=row_ident)

        rotulo_entry = ctk.CTkEntry(
            form_top,
            placeholder_text="Ex.: Avaliacao inicial, Retorno 3 meses",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
        )
        field_on(form_top, "Rotulo do atendimento", rotulo_entry, row_idx=row_ident)

        queixa_frame, queixa_text = self._podoscopio_multiline(form_top, lines=4)
        field_on(form_top, "Queixa / objetivo", queixa_frame, row_idx=row_ident)

        section("Leitura plantar (podoscopio)")
        arco_opts = ["Normal", "Plano", "Cavo", "Nao avaliado"]
        apoio_opts = ["Neutro", "Pronado", "Supinado", "Misto", "Nao avaliado"]
        simetria_opts = ["Simetrica", "Maior a direita", "Maior a esquerda", "Nao avaliado"]

        arco_d = ctk.CTkOptionMenu(scroll_host, values=arco_opts, font=ctk.CTkFont(size=UI_FONT_PT - 1))
        arco_e = ctk.CTkOptionMenu(scroll_host, values=arco_opts, font=ctk.CTkFont(size=UI_FONT_PT - 1))
        field("Arco plantar — pe direito", arco_d)
        field("Arco plantar — pe esquerdo", arco_e)

        apoio_d = ctk.CTkOptionMenu(scroll_host, values=apoio_opts, font=ctk.CTkFont(size=UI_FONT_PT - 1))
        apoio_e = ctk.CTkOptionMenu(scroll_host, values=apoio_opts, font=ctk.CTkFont(size=UI_FONT_PT - 1))
        field("Apoio predominante — pe direito", apoio_d)
        field("Apoio predominante — pe esquerdo", apoio_e)

        simetria = ctk.CTkOptionMenu(scroll_host, values=simetria_opts, font=ctk.CTkFont(size=UI_FONT_PT - 1))
        field("Simetria de carga", simetria)

        section("Hiperpressao (marcar se observado)")
        press_frame = ctk.CTkFrame(scroll_host, fg_color="transparent")
        zonas_lista = ("Calcaneo", "Metatarsos", "Halux", "Borda lateral", "Medio-pe")
        for idx, zona in enumerate(zonas_lista):
            v = tk.BooleanVar(value=False)
            press_vars[zona] = v
            ctk.CTkCheckBox(
                press_frame,
                text=zona,
                variable=v,
                font=ctk.CTkFont(size=UI_FONT_PT - 1),
            ).grid(row=idx // 3, column=idx % 3, sticky="w", padx=(0, 16), pady=4)
        ctk.CTkLabel(
            scroll_host,
            text="Zonas observadas",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            text_color="#444444",
        ).grid(row=row, column=0, sticky="nw", padx=(14, 8), pady=6)
        press_frame.grid(row=row, column=1, sticky="ew", padx=(0, 14), pady=6)
        row += 1

        section("Observacoes clinicas")
        obs_frame, obs_text = self._podoscopio_multiline(scroll_host, lines=5)
        field("Observacoes", obs_frame)

        section("Registro fotografico")
        ctk.CTkLabel(
            scroll_host,
            text="Proxima etapa: anexar imagens (frontal no podoscopio, lateral D/E, posterior).",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            text_color="#666666",
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 8))
        row += 1
        fotos_placeholder = ctk.CTkFrame(scroll_host, fg_color="#f8f8f8", corner_radius=8, height=80)
        fotos_placeholder.grid(row=row, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 8))
        ctk.CTkLabel(
            fotos_placeholder,
            text="Area de imagens — em breve",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            text_color="#888888",
        ).pack(expand=True, pady=24)
        row += 1

        ctk.CTkButton(
            btn_row,
            text="Nova ficha",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=lambda: (
                _limpar_formulario(manter_paciente=True),
                var_ficha.set("— Nova ficha —"),
                self._podoscopio_ctx.update(ficha_id=None),
            ),
        ).pack(side="left")
        ctk.CTkButton(
            btn_row,
            text="Salvar ficha",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            fg_color="#7c1229",
            hover_color="#5b0717",
            command=_salvar_ficha,
        ).pack(side="left", padx=(8, 0))
        ctk.CTkButton(
            btn_row,
            text="PDF em branco (caneta)",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=_exportar_pdf_branco,
        ).pack(side="left", padx=(8, 0))
        ctk.CTkButton(
            btn_row,
            text="PDF preenchida",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=_exportar_pdf_preenchida,
        ).pack(side="left", padx=(8, 0))

        if not clientes:
            ctk.CTkLabel(
                form_top,
                text="Nenhum paciente cadastrado. Cadastre em Pacientes para usar a ficha.",
                font=ctk.CTkFont(size=UI_FONT_PT - 1),
                text_color="#b00020",
            ).grid(row=row_ident[0], column=0, columnspan=2, sticky="w", padx=14, pady=(0, 8))

        ctx = self._podoscopio_ctx
        if ctx.get("cliente_id"):
            for lbl, cid in by_paciente_label.items():
                if cid == ctx["cliente_id"]:
                    var_paciente.set(lbl)
                    break
            _refresh_fichas_combo(select_ficha_id=ctx.get("ficha_id"))
            fid = ctx.get("ficha_id")
            if fid is not None:
                _carregar_ficha(fid)
            else:
                regs = self.service.fichas_podoscopio.listar_por_cliente(ctx["cliente_id"])
                if regs:
                    _carregar_ficha(regs[0].id)
                    _refresh_fichas_combo(select_ficha_id=regs[0].id)

    def _build_configuracoes_hub(self) -> None:
        self._build_module_hub(
            parent_id="configuracoes",
            intro="Configuracoes globais da clinica. Regras dos marcadores estao em Plantigrafo > Configuracoes.",
            child_ids=("config_clinica", "config_usuarios", "config_licencas", "config_templates_pdf"),
        )

    def _build_configuracoes_regras_marcadores(self) -> None:
        root = ctk.CTkFrame(self.content, fg_color="transparent")
        root.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(root, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec")
        header.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            header,
            text=f"{self._module_label('plantigrafo')} / {self._module_label('plantigrafo_config')}",
            font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
            text_color="#333333",
        ).pack(anchor="w", padx=14, pady=(10, 2))
        ctk.CTkLabel(
            header,
            text="CRUD para modelos com imagem: linhas A-D; pontos A-F (ver ajuda do EFM).",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            text_color="#666666",
        ).pack(anchor="w", padx=14, pady=(0, 4))

        # Tipos em ordem alfabética; o primeiro fica selecionado ao abrir a tela.
        marker_types_filtro: tuple[str, ...] = tuple(sorted(("linhas", "pontos")))
        filter_bar = ctk.CTkFrame(header, fg_color="transparent")
        filter_bar.pack(fill="x", padx=14, pady=(0, 10))
        ctk.CTkLabel(
            filter_bar,
            text="Mostrar regras de:",
            font=ctk.CTkFont(size=UI_FONT_PT - 1),
            text_color="#333333",
        ).pack(side="left", padx=(0, 10))
        filter_combo = ctk.CTkOptionMenu(
            filter_bar,
            values=list(marker_types_filtro),
            font=ctk.CTkFont(size=UI_FONT_PT),
            dynamic_resizing=False,
            width=160,
        )
        filter_combo.set(marker_types_filtro[0])
        filter_combo.pack(side="left")

        body = ctk.CTkFrame(root, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#ececec")
        body.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=0)
        body.grid_rowconfigure(2, weight=0)

        form = ctk.CTkScrollableFrame(body, fg_color="transparent")
        form.grid(row=0, column=0, sticky="nsew", padx=8, pady=(12, 8))
        for col in range(3):
            form.grid_columnconfigure(col, weight=1)

        field_font = ctk.CTkFont(size=UI_FONT_PT)
        label_font = ctk.CTkFont(size=UI_FONT_PT - 1)

        def _filter_tipo() -> str:
            return (filter_combo.get() or "linhas").strip().lower() or "linhas"

        _suppress_filter_callback: list[bool] = [False]

        ctk.CTkLabel(form, text="Nome da regra *", font=label_font).grid(row=0, column=0, padx=6, sticky="w")
        ctk.CTkLabel(form, text="Status", font=label_font).grid(row=0, column=1, padx=6, sticky="w")
        ctk.CTkLabel(form, text="Imagem de exemplo *", font=label_font).grid(row=0, column=2, padx=6, sticky="w")

        nome_regra = ctk.CTkEntry(form, font=field_font, placeholder_text="Ex.: Regra base pe adulto")
        ativo_var = tk.BooleanVar(value=True)
        ativo = ctk.CTkCheckBox(form, text="Ativa", variable=ativo_var, font=field_font)
        image_label = ctk.CTkLabel(form, text="Nenhuma imagem selecionada", font=label_font, text_color="#666666")

        nome_regra.grid(row=1, column=0, padx=6, pady=(0, 8), sticky="ew")
        ativo.grid(row=1, column=1, padx=6, pady=(0, 8), sticky="w")
        image_label.grid(row=1, column=2, padx=6, pady=(0, 8), sticky="w")

        tipo_filtro_lbl = ctk.CTkLabel(
            form,
            text="",
            font=label_font,
            text_color="#666666",
        )
        tipo_filtro_lbl.grid(row=2, column=0, columnspan=3, padx=6, pady=(0, 4), sticky="w")

        def _refresh_tipo_hint() -> None:
            tipo_filtro_lbl.configure(text=f"Tipo fixo pelo filtro acima: «{_filter_tipo()}».")

        _refresh_tipo_hint()

        ctk.CTkLabel(form, text="Descricao geral", font=label_font).grid(row=3, column=0, columnspan=3, padx=6, sticky="w")
        descricao_geral = ctk.CTkTextbox(form, height=120, font=field_font)
        descricao_geral.grid(row=4, column=0, columnspan=3, padx=6, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(
            form,
            text="Protocolo por item (todos obrigatorios ao salvar)",
            font=label_font,
        ).grid(row=5, column=0, columnspan=3, padx=6, pady=(4, 0), sticky="w")
        protocolo_container = ctk.CTkFrame(form, fg_color="transparent")
        protocolo_container.grid(row=6, column=0, columnspan=3, padx=0, pady=(0, 8), sticky="ew")
        protocolo_container.grid_columnconfigure(0, weight=1)

        item_textboxes: list[ctk.CTkTextbox] = []

        def _rebuild_protocolo_ui(tipo: str, texts_in_order: list[str] | None) -> None:
            for w in protocolo_container.winfo_children():
                w.destroy()
            item_textboxes.clear()
            t = (tipo or "linhas").strip().lower() or "linhas"
            n = required_item_count(t)
            rots = default_rotulos(t)
            if texts_in_order is None:
                texts_in_order = [""] * n
            elif len(texts_in_order) < n:
                texts_in_order = list(texts_in_order) + [""] * (n - len(texts_in_order))
            else:
                texts_in_order = texts_in_order[:n]
            for i in range(n):
                base_row = i * 2
                ctk.CTkLabel(
                    protocolo_container,
                    text=f"Item {i + 1} ({rots[i]}) — definicao *",
                    font=label_font,
                ).grid(row=base_row, column=0, columnspan=3, padx=6, sticky="w")
                txt = ctk.CTkTextbox(protocolo_container, height=60, font=field_font)
                txt.grid(row=base_row + 1, column=0, columnspan=3, padx=6, pady=(0, 8), sticky="ew")
                txt.insert("1.0", texts_in_order[i])
                item_textboxes.append(txt)

        btns = ctk.CTkFrame(body, fg_color="transparent")
        btns.grid(row=1, column=0, sticky="ew", padx=12, pady=(8, 8))

        _rebuild_protocolo_ui(_filter_tipo(), None)

        def _collect_form_data() -> dict[str, object]:
            tipo = _filter_tipo()
            rots = default_rotulos(tipo)
            itens_payload: list[dict[str, object]] = []
            for idx, tb in enumerate(item_textboxes):
                itens_payload.append(
                    {
                        "ordem": idx + 1,
                        "rotulo": rots[idx],
                        "texto": tb.get("1.0", "end-1c").strip(),
                    }
                )
            return {
                "nome_regra": nome_regra.get().strip(),
                "tipo_marcador": tipo,
                "ativo": ativo_var.get(),
                "descricao_geral": descricao_geral.get("1.0", "end-1c").strip(),
                "protocolo": {"versao": PROTOCOLO_VERSAO_ATUAL, "itens": itens_payload},
            }

        def _clear_form() -> None:
            self._editing_rule_id = None
            self._selected_rule_image = ""
            nome_regra.delete(0, tk.END)
            ativo_var.set(True)
            image_label.configure(text="Nenhuma imagem selecionada", text_color="#666666")
            descricao_geral.delete("1.0", "end")
            save_btn.configure(text="Salvar regra")
            _refresh_tipo_hint()
            _rebuild_protocolo_ui(_filter_tipo(), None)

        def _fill_form(rule: MarkerRule) -> None:
            self._editing_rule_id = rule.id
            self._selected_rule_image = ""
            nome_regra.delete(0, tk.END)
            nome_regra.insert(0, rule.nome_regra)
            ativo_var.set(rule.ativo)
            image_label.configure(text=rule.imagem_exemplo_nome or "Sem imagem", text_color="#333333")
            descricao_geral.delete("1.0", "end")
            descricao_geral.insert("1.0", rule.descricao_geral)
            tipo = rule.tipo_marcador if rule.tipo_marcador in {"linhas", "pontos"} else "linhas"
            _suppress_filter_callback[0] = True
            try:
                filter_combo.set(tipo)
            finally:
                _suppress_filter_callback[0] = False
            _refresh_tipo_hint()
            _rebuild_protocolo_ui(tipo, [it.texto for it in rule.itens])
            save_btn.configure(text="Atualizar regra")
            _sync_restore_buttons()

        def _origem_label(rule: MarkerRule) -> str:
            if rule.seed_role == SEED_ROLE_ABCD_REFERENCE:
                return "Referencia sistema"
            if rule.seed_role == SEED_ROLE_ABCD_USER_COPY:
                return "Versao usuario"
            if rule.seed_role == SEED_ROLE_POINTS_REFERENCE:
                return "Referencia sistema"
            if rule.seed_role == SEED_ROLE_POINTS_USER_COPY:
                return "Versao usuario"
            return ""

        def _refresh_rules_table() -> None:
            for row in tree.get_children():
                tree.delete(row)
            ft = _filter_tipo()
            rules = self._marker_rule_store.list_rules()
            for rule in sorted(rules, key=lambda x: x.id, reverse=True):
                if rule.tipo_marcador != ft:
                    continue
                tree.insert(
                    "",
                    "end",
                    values=(
                        rule.id,
                        rule.nome_regra,
                        _origem_label(rule),
                        rule.tipo_marcador,
                        "Sim" if rule.ativo else "Nao",
                        rule.imagem_exemplo_nome or "-",
                        rule.atualizado_em or "-",
                    ),
                )

        def _selected_rule() -> MarkerRule | None:
            selected = tree.focus()
            if not selected:
                return None
            values = tree.item(selected, "values")
            if not values:
                return None
            return self._marker_rule_store.get_rule(int(values[0]))

        def escolher_imagem() -> None:
            file_path = filedialog.askopenfilename(
                title="Selecionar imagem de exemplo",
                filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.bmp;*.webp"), ("Todos", "*.*")],
            )
            if not file_path:
                return
            self._selected_rule_image = file_path
            image_label.configure(text=Path(file_path).name, text_color="#333333")

        def salvar_regra() -> None:
            data = _collect_form_data()
            if not str(data["nome_regra"]).strip():
                messagebox.showerror("Validacao", "Informe o nome da regra.")
                return
            if self._editing_rule_id is None and not self._selected_rule_image:
                messagebox.showerror("Validacao", "Selecione uma imagem de exemplo para criar a regra.")
                return
            try:
                if self._editing_rule_id is None:
                    self._marker_rule_store.create_rule(data, self._selected_rule_image)
                    messagebox.showinfo("Regras", "Regra criada com sucesso.")
                else:
                    self._marker_rule_store.update_rule(
                        self._editing_rule_id,
                        data,
                        self._selected_rule_image or None,
                    )
                    messagebox.showinfo("Regras", "Regra atualizada com sucesso.")
            except ValueError as exc:
                messagebox.showerror("Validacao", str(exc))
                return
            _refresh_rules_table()
            _clear_form()
            _sync_restore_buttons()

        def editar_regra() -> None:
            rule = _selected_rule()
            if not rule:
                messagebox.showinfo("Regras", "Selecione uma regra na tabela.")
                return
            _fill_form(rule)

        def excluir_regra() -> None:
            rule = _selected_rule()
            if not rule:
                messagebox.showinfo("Regras", "Selecione uma regra na tabela.")
                return
            ok = messagebox.askyesno("Excluir regra", f"Confirma excluir a regra '{rule.nome_regra}'?")
            if not ok:
                return
            try:
                self._marker_rule_store.delete_rule(rule.id)
            except ValueError as exc:
                messagebox.showerror("Excluir", str(exc))
                return
            _refresh_rules_table()
            _clear_form()
            _sync_restore_buttons()

        def restaurar_versao_usuario() -> None:
            choice = messagebox.askyesnocancel(
                "Restaurar versao usuario",
                "Repor a regra 'Versao usuario (copia editavel)' aos textos iniciais do pacote.\n\n"
                "Sim = textos + imagem placeholder\n"
                "Nao = so textos (mantem a imagem atual)\n"
                "Cancelar = nao fazer",
            )
            if choice is None:
                return
            try:
                self._marker_rule_store.restore_abcd_user_copy_to_defaults(reset_image=(choice is True))
            except ValueError as exc:
                messagebox.showerror("Restaurar", str(exc))
                return
            messagebox.showinfo("Restaurar", "Versao usuario restaurada.")
            _refresh_rules_table()
            _sync_restore_buttons()

        def restaurar_pontos_usuario() -> None:
            choice = messagebox.askyesnocancel(
                "Restaurar pontos A-F",
                "Repor a regra editavel de pontos (A-F) aos textos iniciais da ajuda.\n\n"
                "Sim = textos + imagem placeholder\n"
                "Nao = so textos (mantem a imagem atual)\n"
                "Cancelar = nao fazer",
            )
            if choice is None:
                return
            try:
                self._marker_rule_store.restore_points_user_copy_to_defaults(reset_image=(choice is True))
            except ValueError as exc:
                messagebox.showerror("Restaurar pontos", str(exc))
                return
            messagebox.showinfo("Restaurar pontos", "Versao usuario (pontos) restaurada.")
            _refresh_rules_table()
            _sync_restore_buttons()

        def abrir_imagem() -> None:
            rule = _selected_rule()
            if not rule:
                messagebox.showinfo("Regras", "Selecione uma regra na tabela.")
                return
            if not rule.imagem_exemplo_path:
                messagebox.showinfo("Regras", "Esta regra nao possui imagem.")
                return
            p = Path(rule.imagem_exemplo_path)
            if not p.exists():
                messagebox.showerror("Regras", "Imagem nao encontrada no disco.")
                return
            try:
                if sys.platform == "win32":
                    import os

                    os.startfile(str(p))  # type: ignore[attr-defined]
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", str(p)])
                else:
                    subprocess.Popen(["xdg-open", str(p)])
            except Exception as exc:
                messagebox.showerror("Regras", f"Nao foi possivel abrir a imagem:\n{exc}")

        ctk.CTkButton(
            btns,
            text="Selecionar imagem",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=escolher_imagem,
        ).pack(side="left")

        save_btn = ctk.CTkButton(
            btns,
            text="Salvar regra",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#7c1229",
            hover_color="#5b0717",
            command=salvar_regra,
        )
        save_btn.pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            btns,
            text="Editar selecionada",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=editar_regra,
        ).pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            btns,
            text="Excluir",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=excluir_regra,
        ).pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            btns,
            text="Abrir imagem",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=abrir_imagem,
        ).pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            btns,
            text="Limpar formulario",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=_clear_form,
        ).pack(side="left", padx=(8, 0))

        btn_restore_abcd = ctk.CTkButton(
            btns,
            text="Restaurar versao usuario (padrao ABCD)",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=restaurar_versao_usuario,
        )
        btn_restore_pts = ctk.CTkButton(
            btns,
            text="Restaurar versao usuario (pontos A-F)",
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#ffffff",
            text_color="#7c1229",
            hover_color="#f0dbe1",
            border_width=1,
            border_color="#7c1229",
            command=restaurar_pontos_usuario,
        )

        def _sync_restore_buttons() -> None:
            btn_restore_abcd.pack_forget()
            btn_restore_pts.pack_forget()
            if _filter_tipo() == "linhas":
                btn_restore_abcd.pack(side="left", padx=(8, 0))
            else:
                btn_restore_pts.pack(side="left", padx=(8, 0))

        table_box = ctk.CTkFrame(body, fg_color="transparent")
        table_box.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        table_box.grid_columnconfigure(0, weight=1)

        self._ensure_treeview_style()
        columns = ("id", "nome", "origem", "tipo", "ativo", "imagem", "atualizado")
        tree = ttk.Treeview(table_box, columns=columns, show="headings", height=3)
        tree.configure(style="EasyFeet.Treeview")
        tree.heading("id", text="ID")
        tree.heading("nome", text="Nome")
        tree.heading("origem", text="Origem")
        tree.heading("tipo", text="Tipo")
        tree.heading("ativo", text="Ativo")
        tree.heading("imagem", text="Imagem")
        tree.heading("atualizado", text="Atualizado")
        tree.column("id", width=54, anchor="center", stretch=False)
        tree.column("nome", width=220, anchor="w")
        tree.column("origem", width=120, anchor="w", stretch=False)
        tree.column("tipo", width=90, anchor="center", stretch=False)
        tree.column("ativo", width=70, anchor="center", stretch=False)
        tree.column("imagem", width=160, anchor="w")
        tree.column("atualizado", width=170, anchor="center", stretch=False)
        tree.grid(row=0, column=0, sticky="ew")
        scrollbar = ttk.Scrollbar(table_box, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._marker_rules_tree = tree

        tree.bind("<Double-1>", lambda _event: editar_regra())

        def _on_filter_change(_choice: str) -> None:
            if _suppress_filter_callback[0]:
                return
            _refresh_tipo_hint()
            _clear_form()
            _refresh_rules_table()
            _sync_restore_buttons()

        filter_combo.configure(command=_on_filter_change)
        _sync_restore_buttons()
        _refresh_rules_table()

    def _on_role_change(self, selected_role: str) -> None:
        self.menu_state.role = selected_role
        ids = collect_nav_module_ids_for_role(self.config_data, self.menu_state.role)
        if self.menu_state.current_module not in ids:
            visible = get_visible_menu_for_role(self.config_data, self.menu_state.role)
            self.menu_state.current_module = visible[0]["id"] if visible else "dashboard"
        self._show_module(self.menu_state.current_module)

    def _show_nascimento_idade_help(self) -> None:
        """Orientação por idade: palmilhas, plantígrafo e regra de cadastro (≥ 3 anos)."""
        modal = ctk.CTkToplevel(self)
        modal.title("Idade, plantígrafo e palmilhas")
        modal_w, modal_h = 820, 560
        modal.geometry(f"{modal_w}x{modal_h}")
        modal.resizable(True, True)
        modal.minsize(640, 420)
        modal.transient(self)
        modal.grab_set()

        frame = ctk.CTkFrame(modal, fg_color="#ffffff")
        frame.pack(fill="both", expand=True, padx=18, pady=18)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text="Idade, plantígrafo e palmilhas",
            font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
            text_color="#333333",
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 8))

        texto = (
            "• Enquanto não completar 3 anos de idade: não fazemos palmilha. O plantígrafo segue o "
            "critério clínico da unidade; para cadastro nesta aplicação é necessário ter completado 3 anos.\n\n"
            "• De 3 anos até antes de completar 6 anos: período de observação; confecciona-se palmilha se houver "
            "piora do quadro (clínica/postura), conforme avaliação.\n\n"
            "• A partir de completar 6 anos: confeccionamos palmilhas para estimular a formação do arco, "
            "quando houver indicação.\n\n"
            "A idade considerada é pelo aniversário completo (data de nascimento face à data atual)."
        )
        body = ctk.CTkTextbox(
            frame,
            width=760,
            height=400,
            font=ctk.CTkFont(size=UI_FONT_PT),
            wrap="word",
            activate_scrollbars=True,
        )
        body.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 8))
        body.insert("1.0", texto)
        body.configure(state="disabled")

        ctk.CTkButton(
            frame,
            text="OK",
            width=90,
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#7c1229",
            hover_color="#5b0717",
            command=modal.destroy,
        ).grid(row=2, column=0, sticky="e", padx=12, pady=(0, 12))

        modal.update_idletasks()
        sw = modal.winfo_screenwidth()
        sh = modal.winfo_screenheight()
        x = max(0, (sw - modal_w) // 2)
        y = max(0, (sh - modal_h) // 2)
        modal.geometry(f"{modal_w}x{modal_h}+{x}+{y}")

    def _show_observacao_modal(self, nome_cliente: str, texto: str) -> None:
        modal = ctk.CTkToplevel(self)
        modal.title(f"Observacao - {nome_cliente}")
        modal_w, modal_h = 760, 420
        modal.geometry(f"{modal_w}x{modal_h}")
        modal.resizable(True, True)
        modal.minsize(520, 280)
        modal.transient(self)
        modal.grab_set()

        frame = ctk.CTkFrame(modal, fg_color="#ffffff")
        frame.pack(fill="both", expand=True, padx=14, pady=14)

        ctk.CTkLabel(
            frame,
            text=f"Observacao - {nome_cliente}",
            font=ctk.CTkFont(size=UI_FONT_PT, weight="bold"),
            text_color="#333333",
        ).pack(anchor="w", padx=12, pady=(10, 8))

        body = ctk.CTkTextbox(frame, height=240, font=ctk.CTkFont(size=UI_FONT_PT))
        body.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        body.insert("1.0", texto)
        body.configure(state="disabled")

        ctk.CTkButton(
            frame,
            text="OK",
            width=90,
            font=ctk.CTkFont(size=UI_FONT_PT),
            fg_color="#7c1229",
            hover_color="#5b0717",
            command=modal.destroy,
        ).pack(anchor="e", padx=12, pady=(0, 10))

        modal.update_idletasks()
        sw = modal.winfo_screenwidth()
        sh = modal.winfo_screenheight()
        x = max(0, (sw - modal_w) // 2)
        y = max(0, (sh - modal_h) // 2)
        modal.geometry(f"{modal_w}x{modal_h}+{x}+{y}")

    def _search_patient(self) -> None:
        if self.menu_state.current_module != "pacientes":
            return
        term = self.search_entry.get().strip().lower()
        if not term:
            return
        found = [c for c in self.service.clientes.listar() if term in c.nome.lower()]
        if not found:
            messagebox.showinfo("Busca", "Nenhum paciente encontrado.")
            return
        names = "\n".join([f"#{c.id} - {c.nome}" for c in found[:8]])
        messagebox.showinfo("Resultados", names)
