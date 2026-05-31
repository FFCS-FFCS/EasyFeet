"""Painel Tk: marcar pontos (um clique) sobre imagem — P&B na pré-visualização."""

from __future__ import annotations

import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from marcador_pontos.definitions import (
    MARKER_BY_ID,
    MARKER_COMBO_TO_ID,
    MARKER_ID_TO_COMBO,
    POINT_MARKERS,
)
from easyfeet_markers.collapsible import CollapsibleFooter
from easyfeet_markers.ui_style import (
    EFM_SHELL_GUTTER,
    EFM_UI_FONT_PANEL,
    EFM_UI_FONT_PANEL_HINT,
    format_rules_path_short,
    tune_combobox_font,
)
from marcador_plantar.rules_io import find_marker_rules_json, list_active_point_rules
from marcador_pontos.exporter import export_annotated_points
from marcador_pontos.footprint_bbox import detect_plantar_bbox, map_norm_to_image


class PontosReferenciasPanel(ttk.Frame):
    """Marcador de pontos anatómicos, embutível no EFM."""

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

        self._points_img: dict[str, tuple[float, float]] = {}
        self._current_marker_id = POINT_MARKERS[0].id
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
        self._points_img.clear()
        self._current_marker_id = POINT_MARKERS[0].id
        self.after_idle(self._refit_preview)
        self.after(300, self._refit_preview)

    def clear_image(self) -> None:
        """Remove imagem e marcacoes do canvas (ex.: ao trocar de paciente)."""
        self._source_path = None
        self._pil_image = None
        self._photo = None
        self._points_img.clear()
        self._current_marker_id = POINT_MARKERS[0].id
        self._zoom_factor = 1.0
        self._var_zoom.set("100%")
        self._canvas.delete("all")
        self._canvas.configure(scrollregion=(0, 0, 0, 0))
        self._lbl_hint.configure(text=self._hint_text())

    def toolbar_export(self) -> None:
        self._export()

    def toolbar_suggest(self) -> None:
        self._suggest_points()

    def toolbar_clear_current(self) -> None:
        self._clear_current()

    def toolbar_clear_all(self) -> None:
        self._clear_all()

    def get_points_data(self) -> dict[str, tuple[float, float]]:
        return dict(self._points_img)

    def set_points_data(self, data: dict[str, tuple[float, float]]) -> None:
        self._points_img = dict(data)
        self._redraw_overlay()
        self._lbl_hint.configure(text=self._hint_text())

    def export_to(self, output_png: Path, output_json: Path) -> None:
        if self._source_path is None or self._pil_image is None:
            raise ValueError("Abra uma imagem e marque ao menos um ponto.")
        if not self._points_img:
            raise ValueError("Nenhum ponto marcado.")
        export_annotated_points(self._source_path, self._points_img, output_png, output_json)

    def _build_ui(self) -> None:
        if self._show_action_toolbar:
            top = ttk.Frame(self, padding=8)
            top.pack(fill="x")

            ttk.Button(top, text="Exportar PNG + JSON...", command=self.toolbar_export).pack(side="left", padx=(0, 8))
            ttk.Button(top, text="Sugerir pontos", command=self.toolbar_suggest).pack(side="left", padx=(0, 8))
            ttk.Button(top, text="Limpar ponto selecionado", command=self.toolbar_clear_current).pack(
                side="left", padx=(0, 8)
            )
            ttk.Button(top, text="Limpar todos", command=self.toolbar_clear_all).pack(side="left")

        rule_row = ttk.Frame(self, padding=self._pad_row)
        rule_row.pack(fill="x")

        ttk.Label(rule_row, text="Regra:", font=self._ui_font).pack(side="left", padx=(0, 6))
        self._rule_combo_labels = self._build_rule_combo_labels()
        self._var_rule = tk.StringVar(value=self._rule_combo_labels[0] if self._rule_combo_labels else "(sem regras)")
        self._combo_rule = ttk.Combobox(
            rule_row,
            textvariable=self._var_rule,
            values=self._rule_combo_labels,
            state="readonly",
            width=44 if self._compact_ui else 52,
        )
        self._combo_rule.pack(side="left", padx=(0, 10))
        tune_combobox_font(self._combo_rule, self._ui_font[1])

        rule_path = ttk.Frame(
            self,
            padding=(EFM_SHELL_GUTTER, 0, EFM_SHELL_GUTTER, 2) if self._compact_ui else (8, 0, 8, 4),
        )
        rule_path.pack(fill="x")
        rp = find_marker_rules_json()
        if self._compact_ui:
            ttk.Label(rule_path, text=f"Ficheiro: {format_rules_path_short(rp)}", font=self._ui_font_hint).pack(
                anchor="w"
            )
        else:
            hint_rules = str(rp) if rp else "(ficheiro data/marker_rules.json nao encontrado)"
            ttk.Label(rule_path, text=f"Regras: {hint_rules}", font=self._ui_font_hint).pack(anchor="w")

        row2 = ttk.Frame(self, padding=self._pad_row)
        row2.pack(fill="x")

        ttk.Label(row2, text="Referência:", font=self._ui_font).pack(side="left")
        first_label = MARKER_ID_TO_COMBO[POINT_MARKERS[0].id]
        self._var_marker = tk.StringVar(value=first_label)
        combo = ttk.Combobox(
            row2,
            textvariable=self._var_marker,
            values=[MARKER_ID_TO_COMBO[m.id] for m in POINT_MARKERS],
            state="readonly",
            width=36 if self._compact_ui else 46,
        )
        combo.pack(side="left", padx=(6, 8))
        combo.bind("<<ComboboxSelected>>", self._on_marker_change)
        tune_combobox_font(combo, self._ui_font[1])

        ttk.Label(row2, text="Zoom:", font=self._ui_font).pack(side="left", padx=(8, 4))
        self._var_zoom = tk.StringVar(value="100%")
        zoom_combo = ttk.Combobox(
            row2,
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
                "Referências A–F (legenda)",
                start_expanded=True,
                button_style="EFM.Panel.TButton",
            )
            refs.pack(fill="x", padx=EFM_SHELL_GUTTER, pady=(0, 4))
            inner = refs.body
            for i, m in enumerate(POINT_MARKERS):
                ttk.Label(inner, text=f"{m.letter}: {m.label_pt}", font=self._ui_font).grid(
                    row=i // 3, column=i % 3, sticky="w", padx=(0, 12), pady=1
                )
        else:
            right = ttk.LabelFrame(
                self,
                text=(
                    "Referências A–F — todos os pontos marcados ficam visíveis; "
                    "use a lista para escolher qual limpar ou recolocar."
                ),
                padding=8,
            )
            right.pack(fill="x", padx=8, pady=(0, 6))
            for m in POINT_MARKERS:
                ttk.Label(right, text=f"{m.letter}: {m.label_pt}", font=self._ui_font).pack(anchor="w")

    @staticmethod
    def _build_rule_combo_labels() -> list[str]:
        rows = list_active_point_rules()
        if not rows:
            return ["(sem regras no JSON — sugestão por posições fixas)"]
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

    def _hint_text(self) -> str:
        m = MARKER_BY_ID.get(self._current_marker_id)
        if not m:
            return "Selecione a referência e clique uma vez na imagem."
        return (
            f"Ponto {m.letter} — {m.label_pt}: um clique coloca ou move o ponto. "
            "Os outros pontos permanecem na imagem."
        )

    def _on_marker_change(self, _event: object | None = None) -> None:
        self._current_marker_id = MARKER_COMBO_TO_ID[self._var_marker.get()]
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
        self._points_img[self._current_marker_id] = (ix, iy)
        self._redraw_overlay()
        self._lbl_hint.configure(text=self._hint_text())

    def _arm_canvas(self) -> int:
        base = max(self._disp_w, self._disp_h)
        return max(6, min(34, int(base * 0.04)))

    def _redraw_overlay(self) -> None:
        self._canvas.delete("overlay")
        if not self._pil_image:
            return
        arm = self._arm_canvas()

        for m in POINT_MARKERS:
            pt = self._points_img.get(m.id)
            if not pt:
                continue
            x, y = pt[0] * self._scale + self._offset_x, pt[1] * self._scale + self._offset_y
            stroke = max(2, int(round(2 * self._zoom_factor)))
            self._canvas.create_line(x - arm, y, x + arm, y, fill="#000000", width=stroke, tags="overlay")
            self._canvas.create_line(x, y - arm, x, y + arm, fill="#000000", width=stroke, tags="overlay")
            r = arm + 2
            self._canvas.create_oval(x - r, y - r, x + r, y + r, outline="#000000", width=stroke, tags="overlay")

            tid = self._canvas.create_text(
                x,
                y - arm - max(12, int(12 * self._zoom_factor)),
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

    def _suggest_points(self) -> None:
        if self._pil_image is None:
            messagebox.showinfo("Marcador", "Abra uma imagem primeiro.", parent=self._tk)
            return
        iw, ih = self._pil_image.size
        if iw < 16 or ih < 16:
            messagebox.showwarning("Marcador", "Imagem demasiado pequena.", parent=self._tk)
            return

        bb = detect_plantar_bbox(self._pil_image)

        def p(nx: float, ny: float) -> tuple[float, float]:
            return map_norm_to_image(bb, nx, ny)

        # Normalizados dentro da caixa da pegada: topo ≈ antepé, base ≈ retropé (vista plantar habitual).
        # nx: 0 esq. / 1 dir. da caixa — pé direito: hálux mais à esq. (nx menor), 5.º metatarso à dir.
        self._points_img[POINT_MARKERS[0].id] = p(0.36, 0.10)  # A hálux — antepé medial
        self._points_img[POINT_MARKERS[1].id] = p(0.82, 0.20)  # B cabeça 5.º — antepé lateral
        self._points_img[POINT_MARKERS[2].id] = p(0.22, 0.48)  # C médio-pé medial
        self._points_img[POINT_MARKERS[3].id] = p(0.38, 0.82)  # D calcâneo medial
        self._points_img[POINT_MARKERS[4].id] = p(0.74, 0.80)  # E calcâneo lateral
        self._points_img[POINT_MARKERS[5].id] = p(0.54, 0.93)  # F centro retropé

        self._redraw_overlay()
        rule_lbl = self._var_rule.get().strip()
        self._lbl_hint.configure(
            text=(
                f"Pontos sugeridos dentro da área da pegada (referência: {rule_lbl}). "
                "Se a foto for irregular, ajuste cada referência manualmente."
            )
        )

    def _clear_current(self) -> None:
        mid = MARKER_COMBO_TO_ID[self._var_marker.get()]
        self._current_marker_id = mid
        self._points_img.pop(mid, None)
        self._redraw_overlay()
        self._lbl_hint.configure(text=self._hint_text())

    def _clear_all(self) -> None:
        self._points_img.clear()
        self._redraw_overlay()
        self._lbl_hint.configure(text=self._hint_text())

    def _export(self) -> None:
        if self._source_path is None or self._pil_image is None:
            messagebox.showwarning("Exportar", "Abra uma imagem e marque ao menos um ponto.", parent=self._tk)
            return
        if not self._points_img:
            messagebox.showwarning("Exportar", "Nenhum ponto marcado.", parent=self._tk)
            return

        stamp = datetime.now().strftime("%Y%m%d")
        base = f"{self._source_path.stem}_efm_pontos_{stamp}"
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
            export_annotated_points(self._source_path, self._points_img, out_png, out_json)
        except OSError as exc:
            messagebox.showerror("Erro", str(exc), parent=self._tk)
            return

        messagebox.showinfo("Exportar", f"Salvo:\n{out_png}\n{out_json}", parent=self._tk)
