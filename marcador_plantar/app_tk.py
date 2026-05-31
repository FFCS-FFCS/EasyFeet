"""Interface Tk para colocar linhas (dois cliques) sobre imagem plantar.

Pre-visualizacao em tons de cinza, linhas e letras pretas (adequado a impressao P&B).
"""

from __future__ import annotations

import math
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from marcador_plantar.definitions import (
    LINE_MARKERS,
    MARKER_BY_ID,
    MARKER_COMBO_TO_ID,
    MARKER_ID_TO_COMBO,
)
from marcador_plantar.exporter import export_annotated
from easyfeet_markers.collapsible import CollapsibleFooter
from easyfeet_markers.ui_style import (
    EFM_SHELL_GUTTER,
    EFM_UI_FONT_PANEL,
    EFM_UI_FONT_PANEL_HINT,
    format_rules_path_short,
    tune_combobox_font,
)
from marcador_plantar.rules_io import find_marker_rules_json, list_active_line_rules

try:
    from marcador_plantar.line_suggest import suggest_abcd_segments
except ImportError:
    suggest_abcd_segments = None  # type: ignore[misc, assignment]


class PlantarLinhasPanel(ttk.Frame):
    """Painel do marcador de linhas (vista plantar), embutível no módulo EFM."""

    _resize_job: str | None = None

    def __init__(
        self,
        parent: tk.Misc,
        *,
        show_action_toolbar: bool = True,
        ui_font_pt: int = 9,
        ui_font_hint_pt: int | None = None,
        compact_ui: bool = False,
        **kwargs: object,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._show_action_toolbar = show_action_toolbar
        self._compact_ui = compact_ui
        self._ui_font: tuple[str, int] = EFM_UI_FONT_PANEL if compact_ui else ("Segoe UI", ui_font_pt)
        if compact_ui and ui_font_pt != 9:
            self._ui_font = ("Segoe UI", ui_font_pt)
        hint_pt = ui_font_hint_pt if ui_font_hint_pt is not None else (EFM_UI_FONT_PANEL_HINT[1] if compact_ui else ui_font_pt)
        self._ui_font_hint: tuple[str, int] = ("Segoe UI", hint_pt) if compact_ui else self._ui_font
        self._pad_row = (EFM_SHELL_GUTTER, 0, EFM_SHELL_GUTTER, 4) if compact_ui else (8, 0, 8, 8)
        self._tk = self.winfo_toplevel()

        self._source_path: Path | None = None
        self._pil_image: Image.Image | None = None
        self._photo: ImageTk.PhotoImage | None = None
        self._scale: float = 1.0
        self._fit_scale: float = 1.0
        self._zoom_factor: float = 1.0
        self._disp_w = 0
        self._disp_h = 0
        self._offset_x = 0
        self._offset_y = 0

        self._lines_img: dict[str, tuple[tuple[float, float], tuple[float, float]]] = {}
        self._pending: tuple[float, float] | None = None
        self._current_marker_id = LINE_MARKERS[0].id
        self._rule_combo_labels: list[str] = []

        if compact_ui:
            style = ttk.Style(self)
            style.configure("EFM.Panel.TButton", font=self._ui_font)
        self._build_ui()

    def get_source_path(self) -> Path | None:
        return self._source_path

    def load_image(self, path: Path) -> None:
        """Carrega a mesma imagem neste painel (usado para sincronizar ao trocar tipo)."""
        self._source_path = path
        try:
            self._pil_image = Image.open(self._source_path).convert("RGBA")
        except OSError as exc:
            messagebox.showerror("Erro", f"Nao foi possivel abrir a imagem:\n{exc}", parent=self._tk)
            return

        # Ao carregar a nova imagem neste painel, limpamos apenas as marcações deste tipo.
        self._lines_img.clear()
        self._pending = None
        self.after_idle(self._refit_preview)
        self.after(300, self._refit_preview)

    def clear_image(self) -> None:
        """Remove imagem e marcacoes do canvas (ex.: ao trocar de paciente)."""
        self._source_path = None
        self._pil_image = None
        self._photo = None
        self._lines_img.clear()
        self._pending = None
        self._zoom_factor = 1.0
        self._var_zoom.set("100%")
        self._canvas.delete("all")
        self._canvas.configure(scrollregion=(0, 0, 0, 0))
        self._lbl_hint.configure(text=self._hint_text())

    def toolbar_export(self) -> None:
        self._export()

    def toolbar_generate(self) -> None:
        self._generate_all_lines()

    def toolbar_suggest(self) -> None:
        self._suggest_from_active_rule()

    def toolbar_clear_current(self) -> None:
        self._clear_current()

    def toolbar_clear_all(self) -> None:
        self._clear_all()

    def get_lines_data(self) -> dict[str, tuple[tuple[float, float], tuple[float, float]]]:
        return dict(self._lines_img)

    def set_lines_data(self, data: dict[str, tuple[tuple[float, float], tuple[float, float]]]) -> None:
        self._lines_img = dict(data)
        self._pending = None
        self._redraw_overlay()
        self._lbl_hint.configure(text=self._hint_text())

    def export_to(self, output_png: Path, output_json: Path) -> None:
        if self._source_path is None or self._pil_image is None:
            raise ValueError("Abra uma imagem e desenhe ao menos uma linha.")
        if not self._lines_img:
            raise ValueError("Nenhuma linha desenhada.")
        export_annotated(self._source_path, self._lines_img, output_png, output_json)

    def _build_ui(self) -> None:
        if self._show_action_toolbar:
            top = ttk.Frame(self, padding=8)
            top.pack(fill="x")

            ttk.Button(top, text="Exportar PNG + JSON...", command=self.toolbar_export).pack(side="left", padx=(0, 8))
            ttk.Button(top, text="Heuristica simples (A-D)", command=self.toolbar_generate).pack(
                side="left", padx=(0, 8)
            )
            ttk.Button(top, text="Sugerir pela regra...", command=self.toolbar_suggest).pack(
                side="left", padx=(0, 8)
            )
            ttk.Button(top, text="Limpar linha selecionada", command=self.toolbar_clear_current).pack(
                side="left", padx=(0, 8)
            )
            ttk.Button(top, text="Limpar todas", command=self.toolbar_clear_all).pack(side="left")

        row2 = ttk.Frame(self, padding=self._pad_row)
        row2.pack(fill="x")

        ttk.Label(row2, text="Regra:", font=self._ui_font).pack(side="left", padx=(0, 6))
        self._rule_combo_labels = self._build_rule_combo_labels()
        self._var_rule = tk.StringVar(value=self._rule_combo_labels[0] if self._rule_combo_labels else "(sem regras)")
        rule_w = 44 if self._compact_ui else 52
        self._combo_rule = ttk.Combobox(
            row2,
            textvariable=self._var_rule,
            values=self._rule_combo_labels,
            state="readonly",
            width=rule_w,
        )
        self._combo_rule.pack(side="left", padx=(0, 10))
        tune_combobox_font(self._combo_rule, self._ui_font[1])

        if not self._compact_ui:
            row2b = ttk.Frame(self, padding=(8, 0, 8, 4))
            row2b.pack(fill="x")
            rp = find_marker_rules_json()
            hint_rules = str(rp) if rp else "(ficheiro data/marker_rules.json nao encontrado)"
            ttk.Label(row2b, text=f"Regras: {hint_rules}", font=self._ui_font_hint).pack(anchor="w")
        else:
            row2b = ttk.Frame(self, padding=(EFM_SHELL_GUTTER, 0, EFM_SHELL_GUTTER, 2))
            row2b.pack(fill="x")
            rp = find_marker_rules_json()
            ttk.Label(
                row2b,
                text=f"Ficheiro: {format_rules_path_short(rp)}",
                font=self._ui_font_hint,
            ).pack(anchor="w")

        row3 = ttk.Frame(self, padding=self._pad_row)
        row3.pack(fill="x")

        ttk.Label(row3, text="Tipo de linha:", font=self._ui_font).pack(side="left")
        first_label = MARKER_ID_TO_COMBO[LINE_MARKERS[0].id]
        self._var_marker = tk.StringVar(value=first_label)
        combo = ttk.Combobox(
            row3,
            textvariable=self._var_marker,
            values=[MARKER_ID_TO_COMBO[m.id] for m in LINE_MARKERS],
            state="readonly",
            width=36 if self._compact_ui else 46,
        )
        combo.pack(side="left", padx=(6, 8))
        combo.bind("<<ComboboxSelected>>", self._on_marker_change)
        tune_combobox_font(combo, self._ui_font[1])

        ttk.Label(row3, text="Zoom:", font=self._ui_font).pack(side="left", padx=(8, 4))
        self._var_zoom = tk.StringVar(value="100%")
        zoom_combo = ttk.Combobox(
            row3,
            textvariable=self._var_zoom,
            values=["100%", "150%", "200%", "250%", "300%", "350%", "400%"],
            state="readonly",
            width=7,
        )
        zoom_combo.pack(side="left")
        zoom_combo.bind("<<ComboboxSelected>>", self._on_zoom_change)
        tune_combobox_font(zoom_combo, self._ui_font[1])

        hint_row = ttk.Frame(
            self,
            padding=(EFM_SHELL_GUTTER, 0, EFM_SHELL_GUTTER, 4) if self._compact_ui else (8, 0, 8, 4),
        )
        hint_row.pack(fill="x")
        self._lbl_hint = ttk.Label(
            hint_row,
            text=self._hint_text(),
            font=self._ui_font_hint if self._compact_ui else self._ui_font,
            wraplength=720 if self._compact_ui else 0,
        )
        self._lbl_hint.pack(anchor="w")

        pan = ttk.Frame(self)
        pan.pack(fill="both", expand=True, padx=EFM_SHELL_GUTTER if self._compact_ui else 8, pady=(0, 8))

        self._canvas = tk.Canvas(pan, bg="#ffffff", highlightthickness=0)
        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._xbar = ttk.Scrollbar(pan, orient="horizontal", command=self._canvas.xview)
        self._ybar = ttk.Scrollbar(pan, orient="vertical", command=self._canvas.yview)
        self._xbar.grid(row=1, column=0, sticky="ew")
        self._ybar.grid(row=0, column=1, sticky="ns")
        self._canvas.configure(xscrollcommand=self._xbar.set, yscrollcommand=self._ybar.set)
        pan.grid_rowconfigure(0, weight=1)
        pan.grid_columnconfigure(0, weight=1)

        self._canvas.bind("<Button-1>", self._on_click)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        if self._compact_ui:
            refs = CollapsibleFooter(
                self,
                "Tipos A–D (legenda)",
                start_expanded=True,
                button_style="EFM.Panel.TButton",
            )
            refs.pack(fill="x", padx=EFM_SHELL_GUTTER, pady=(0, 4))
            inner = refs.body
            for col, m in enumerate(LINE_MARKERS):
                ttk.Label(inner, text=f"{m.letter}: {m.label_pt}", font=self._ui_font).grid(
                    row=0, column=col, sticky="w", padx=(0, 14), pady=2
                )
        else:
            right = ttk.LabelFrame(
                self,
                text=(
                    "Tipos (fixos A–D) — todas ficam visíveis ao mesmo tempo; "
                    "use a lista acima para escolher qual linha limpar ou redesenhar."
                ),
                padding=8,
            )
            right.pack(fill="x", padx=8, pady=(0, 6))
            for m in LINE_MARKERS:
                ttk.Label(right, text=f"{m.letter}: {m.label_pt}", font=self._ui_font).pack(anchor="w")

    def _hint_text(self) -> str:
        m = MARKER_BY_ID.get(self._current_marker_id)
        if not m:
            return "Selecione o tipo e clique dois pontos na imagem."
        return f"Marcador {m.letter} — {m.label_pt}: primeiro clique, segundo clique. (Todas as linhas ja feitas permanecem na imagem.)"

    @staticmethod
    def _build_rule_combo_labels() -> list[str]:
        rows = list_active_line_rules()
        if not rows:
            return ["(sem regras no JSON — analise geometrica)"]
        labels: list[str] = []
        for r in rows:
            rid = r.get("id", "?")
            nome = str(r.get("nome_regra", "")).strip()
            if len(nome) > 46:
                nome = nome[:43] + "..."
            sr = str(r.get("seed_role") or "").strip()
            suf = f" [{sr}]" if sr else ""
            labels.append(f"#{rid} — {nome}{suf}")
        return labels

    def _suggest_from_active_rule(self) -> None:
        """Sugere A-D pela analise da pegada; a regra escolhida e referencia (parametros futuros)."""
        if self._pil_image is None:
            messagebox.showinfo("Marcador", "Abra uma imagem primeiro.", parent=self._tk)
            return
        if suggest_abcd_segments is None:
            messagebox.showerror(
                "Marcador",
                "O modulo de sugestao requer NumPy.\nInstale com: pip install numpy",
                parent=self._tk,
            )
            return
        rule_lbl = self._var_rule.get().strip()
        try:
            segs = suggest_abcd_segments(self._pil_image)
        except ValueError as exc:
            messagebox.showwarning("Sugestao", str(exc), parent=self._tk)
            return
        self._lines_img.clear()
        for k, seg in segs.items():
            self._lines_img[k] = seg
        self._pending = None
        self._redraw_overlay()
        self._lbl_hint.configure(
            text=(
                f"Sugestao A-D aplicada (referencia: {rule_lbl}). "
                "Ajuste por tipo na lista e dois cliques se precisar."
            )
        )

    def _on_marker_change(self, _event: object | None = None) -> None:
        self._current_marker_id = MARKER_COMBO_TO_ID[self._var_marker.get()]
        self._pending = None
        self._lbl_hint.configure(text=self._hint_text())

    def _on_canvas_configure(self, _event: tk.Event[tk.Misc]) -> None:
        if self._pil_image is None:
            return
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(120, self._schedule_refit)

    def _schedule_refit(self) -> None:
        self._resize_job = None
        self._refit_preview()

    def _on_zoom_change(self, _event: object | None = None) -> None:
        txt = self._var_zoom.get().replace("%", "").strip()
        try:
            pct = int(txt)
        except ValueError:
            pct = 100
        self._zoom_factor = max(1.0, min(4.0, pct / 100.0))
        self._refit_preview()

    def _open_image(self) -> None:
        path = filedialog.askopenfilename(
            parent=self._tk,
            title="Imagem plantar",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp *.bmp"), ("Todos", "*.*")],
        )
        if not path:
            return
        self.load_image(Path(path))

    def _refit_preview(self) -> None:
        """Recalcula escala e posicao para a imagem caber na area do canvas (sem barras de rolagem)."""
        self._canvas.delete("all")
        if self._pil_image is None:
            return

        self.update_idletasks()
        cw = max(self._canvas.winfo_width(), 200)
        ch = max(self._canvas.winfo_height(), 200)
        margin = 24
        iw, ih = self._pil_image.size
        avail_w = max(cw - margin, 50)
        avail_h = max(ch - margin, 50)

        z = min(avail_w / iw, avail_h / ih)
        self._fit_scale = min(float(z), 1.0)
        self._scale = self._fit_scale * self._zoom_factor

        self._disp_w = int(iw * self._scale)
        self._disp_h = int(ih * self._scale)
        self._offset_x = max((cw - self._disp_w) // 2, 0)
        self._offset_y = max((ch - self._disp_h) // 2, 0)

        preview_src = self._pil_to_gray_preview(self._pil_image)
        preview = preview_src.resize((self._disp_w, self._disp_h), Image.Resampling.LANCZOS)
        self._photo = ImageTk.PhotoImage(preview)
        self._canvas.create_image(
            self._offset_x,
            self._offset_y,
            anchor="nw",
            image=self._photo,
            tags=("bg",),
        )
        sr = (
            0,
            0,
            max(cw, self._offset_x + self._disp_w),
            max(ch, self._offset_y + self._disp_h),
        )
        self._canvas.configure(scrollregion=sr)
        if self._zoom_factor <= 1.0:
            self._canvas.xview_moveto(0)
            self._canvas.yview_moveto(0)
        self._redraw_overlay()

    @staticmethod
    def _pil_to_gray_preview(src: Image.Image) -> Image.Image:
        """Mostra a foto em tons de cinza (a imagem original em disco mantem-se para o export)."""
        if src.mode == "RGBA":
            rgb = Image.new("RGB", src.size, (255, 255, 255))
            rgb.paste(src, mask=src.split()[3])
            return rgb.convert("L")
        return src.convert("L")

    def _canvas_to_image(self, cx: float, cy: float) -> tuple[float, float]:
        lx = cx - self._offset_x
        ly = cy - self._offset_y
        return lx / self._scale, ly / self._scale

    def _on_click(self, event: tk.Event[tk.Misc]) -> None:
        if self._pil_image is None:
            messagebox.showinfo("Marcador", "Abra uma imagem primeiro.", parent=self._tk)
            return
        self._current_marker_id = MARKER_COMBO_TO_ID[self._var_marker.get()]
        cx = self._canvas.canvasx(event.x)
        cy = self._canvas.canvasy(event.y)
        lx = cx - self._offset_x
        ly = cy - self._offset_y
        if lx < 0 or ly < 0 or lx > self._disp_w or ly > self._disp_h:
            return
        ix, iy = self._canvas_to_image(cx, cy)

        if self._pending is None:
            self._pending = (ix, iy)
            self._lbl_hint.configure(text="Segundo clique para completar a linha.")
            return

        x1, y1 = self._pending
        self._pending = None
        self._lines_img[self._current_marker_id] = ((x1, y1), (ix, iy))
        self._redraw_overlay()
        self._lbl_hint.configure(text=self._hint_text())

    def _redraw_overlay(self) -> None:
        self._canvas.delete("overlay")
        if not self._pil_image:
            return
        # Desenhar na ordem fixa A-D para sobreposicao consistente (todas as linhas guardadas aparecem).
        for m in LINE_MARKERS:
            seg = self._lines_img.get(m.id)
            if not seg:
                continue
            p1, p2 = seg
            x1 = p1[0] * self._scale + self._offset_x
            y1 = p1[1] * self._scale + self._offset_y
            x2 = p2[0] * self._scale + self._offset_x
            y2 = p2[1] * self._scale + self._offset_y
            line_w = max(2, int(round(3 * self._zoom_factor)))
            self._canvas.create_line(x1, y1, x2, y2, fill="#000000", width=line_w, tags="overlay")
            # Evita sobreposicao de letras no ponto de cruzamento (ex: A com C).
            if m.id == "line_longitudinal_axis":
                # Ponta superior (menor Y) para o eixo longitudinal A.
                if y1 <= y2:
                    lx, ly = x1, y1
                else:
                    lx, ly = x2, y2
            else:
                # Ponta "esquerda" (menor X) para B/C/D.
                if x1 <= x2:
                    lx, ly = x1, y1
                else:
                    lx, ly = x2, y2

            # Afasta a letra da própria linha para facilitar clique visual na ponta.
            dx = x2 - x1
            dy = y2 - y1
            norm = math.hypot(dx, dy) or 1.0
            nx = -dy / norm
            ny = dx / norm
            label_gap = max(18, int(22 * self._zoom_factor))
            tx = lx + nx * label_gap
            ty = ly + ny * label_gap

            tid = self._canvas.create_text(
                tx,
                ty,
                text=m.letter,
                fill="#000000",
                font=("Segoe UI", max(13, int(13 * self._zoom_factor)), "bold"),
                tags="overlay",
            )
            bbox = self._canvas.bbox(tid)
            if bbox:
                pad = 3
                rid = self._canvas.create_rectangle(
                    bbox[0] - pad,
                    bbox[1] - pad,
                    bbox[2] + pad,
                    bbox[3] + pad,
                    fill="#ffffff",
                    outline="#000000",
                    width=1,
                    tags="overlay",
                )
                self._canvas.tag_lower(rid, tid)

    def _generate_all_lines(self) -> None:
        """Coloca A-D com heuristica simples (pe centralizado, tres larguras em faixas verticais)."""
        if self._pil_image is None:
            messagebox.showinfo("Marcador", "Abra uma imagem primeiro.", parent=self._tk)
            return
        iw, ih = self._pil_image.size
        if iw < 16 or ih < 16:
            messagebox.showwarning("Marcador", "Imagem demasiado pequena.", parent=self._tk)
            return

        xm = iw / 2.0
        # Margens para nao encostar nas bordas (coordenadas em pixels da imagem original).
        mx_pct = 0.10
        my_top = 0.08 * ih
        my_bot = 0.92 * ih
        left = mx_pct * iw
        right = (1.0 - mx_pct) * iw

        # A: eixo longitudinal (vertical pelo centro, dedos -> retropé).
        self._lines_img[LINE_MARKERS[0].id] = ((xm, my_top), (xm, my_bot))
        # B/C/D: linhas de largura (horizontais em tres niveis do pé).
        y_fore = 0.22 * ih
        y_mid = 0.50 * ih
        y_hind = 0.78 * ih
        self._lines_img[LINE_MARKERS[1].id] = ((left, y_fore), (right, y_fore))
        self._lines_img[LINE_MARKERS[2].id] = ((left, y_mid), (right, y_mid))
        self._lines_img[LINE_MARKERS[3].id] = ((left, y_hind), (right, y_hind))

        self._pending = None
        self._redraw_overlay()
        self._lbl_hint.configure(
            text="Linhas automáticas A–D na imagem. Para corrigir: escolha o tipo na lista e marque de novo com dois cliques."
        )

    def _clear_current(self) -> None:
        # Sincronizar com a lista (evita dessincronização com o id interno).
        mid = MARKER_COMBO_TO_ID[self._var_marker.get()]
        self._current_marker_id = mid
        self._lines_img.pop(mid, None)
        self._pending = None
        self._redraw_overlay()
        self._lbl_hint.configure(text=self._hint_text())

    def _clear_all(self) -> None:
        self._lines_img.clear()
        self._pending = None
        self._redraw_overlay()
        self._lbl_hint.configure(text=self._hint_text())

    def _export(self) -> None:
        if self._source_path is None or self._pil_image is None:
            messagebox.showwarning("Exportar", "Abra uma imagem e desenhe ao menos uma linha.", parent=self._tk)
            return
        if not self._lines_img:
            messagebox.showwarning("Exportar", "Nenhuma linha desenhada.", parent=self._tk)
            return

        stamp = datetime.now().strftime("%Y%m%d")
        base = f"{self._source_path.stem}_efm_linhas_{stamp}"
        out_dir = self._source_path.parent
        out_png = out_dir / f"{base}.png"

        path_png = filedialog.asksaveasfilename(
            parent=self._tk,
            title="Salvar imagem anotada",
            initialfile=out_png.name,
            initialdir=str(out_dir),
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
        )
        if not path_png:
            return
        out_png = Path(path_png)
        out_json = out_png.with_suffix(".json")

        try:
            export_annotated(self._source_path, self._lines_img, out_png, out_json)
        except OSError as exc:
            messagebox.showerror("Erro", str(exc), parent=self._tk)
            return

        messagebox.showinfo("Exportar", f"Salvo:\n{out_png}\n{out_json}", parent=self._tk)
