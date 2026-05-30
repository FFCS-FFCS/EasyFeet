"""Exporta PNG em tons de cinza + linhas pretas + legenda e JSON lado a lado."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from marcador_plantar.definitions import JSON_VERSION, LINE_MARKERS, PROTOCOL_ID


def _load_font(size: int = 14) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
    ]
    for p in candidates:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except OSError:
                continue
    return ImageFont.load_default()


def export_annotated(
    source_path: Path,
    lines_by_id: dict[str, tuple[tuple[float, float], tuple[float, float]]],
    output_png: Path,
    output_json: Path,
) -> None:
    """
    lines_by_id: marker_id -> ((x1,y1), (x2,y2)) em coordenadas da imagem original (pixels).
    """
    img = Image.open(source_path).convert("L")
    w, h = img.size
    draw = ImageDraw.Draw(img)
    font = _load_font(16)
    font_small = _load_font(12)

    stroke_w = max(2, min(w, h) // 400 or 2)

    for m in LINE_MARKERS:
        seg = lines_by_id.get(m.id)
        if not seg:
            continue
        (x1, y1), (x2, y2) = seg
        draw.line([(x1, y1), (x2, y2)], fill=0, width=stroke_w)

        # Evita sobreposicao no cruzamento (ex: A com C): letras em pontas.
        if m.id == "line_longitudinal_axis":
            # A: ponta superior (menor Y).
            if y1 <= y2:
                mx, my = x1, y1
            else:
                mx, my = x2, y2
        else:
            # B/C/D: ponta esquerda (menor X).
            if x1 <= x2:
                mx, my = x1, y1
            else:
                mx, my = x2, y2

        label = m.letter
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx, ty = mx - tw / 2, my - th / 2 - 8
        pad = 3
        draw.rectangle(
            [tx - pad, ty - pad, tx + tw + pad, ty + th + pad],
            fill=255,
            outline=0,
            width=1,
        )
        draw.text((tx, ty), label, fill=0, font=font)

    _draw_legend(draw, img.size, font_small)

    output_png.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_png, format="PNG")

    payload: dict[str, Any] = {
        "version": JSON_VERSION,
        "protocol": PROTOCOL_ID,
        "source_image": source_path.name,
        "source_path": str(source_path.resolve()),
        "image_size": {"width": w, "height": h},
        "markers": [],
    }

    for m in LINE_MARKERS:
        seg = lines_by_id.get(m.id)
        if not seg:
            continue
        (x1, y1), (x2, y2) = seg
        payload["markers"].append(
            {
                "family": "line",
                "id": m.id,
                "letter": m.letter,
                "label_pt": m.label_pt,
                "points": [[float(x1), float(y1)], [float(x2), float(y2)]],
            }
        )

    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _legend_lines() -> list[str]:
    return [f"{m.letter} — {m.label_pt}" for m in LINE_MARKERS]


def _draw_legend(draw: ImageDraw.ImageDraw, size: tuple[int, int], font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> None:
    w, h = size
    lines = [
        "EasyFeet — Marcador de linhas (vista plantar)",
        "Versão do registo: " + JSON_VERSION,
        "Tipo de dados: linhas plantares",
        "",
    ] + _legend_lines()
    line_heights: list[int] = []
    max_tw = 0
    for line in lines:
        if not line:
            line_heights.append(6)
            continue
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        max_tw = max(max_tw, tw)
        line_heights.append(th + 4)

    pad = 12
    box_w = min(max_tw + 2 * pad, w - 20)
    box_h = sum(line_heights) + pad
    x0, y0 = 10, h - box_h - 10
    draw.rectangle([x0, y0, x0 + box_w, y0 + box_h], fill=255, outline=0, width=2)

    cy = y0 + pad // 2
    for line in lines:
        if not line:
            cy += 6
            continue
        draw.text((x0 + pad, cy), line, fill=0, font=font)
        bbox = draw.textbbox((0, 0), line, font=font)
        cy += bbox[3] - bbox[1] + 4
