"""Exporta PNG em tons de cinza + pontos (cruz) pretos + legenda e JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from marcador_pontos.definitions import JSON_VERSION, POINT_MARKERS, PROTOCOL_ID


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


def export_annotated_points(
    source_path: Path,
    points_by_id: dict[str, tuple[float, float]],
    output_png: Path,
    output_json: Path,
) -> None:
    """points_by_id: marker_id -> (x, y) em pixels da imagem original."""
    img = Image.open(source_path).convert("L")
    w, h = img.size
    draw = ImageDraw.Draw(img)
    font = _load_font(16)
    font_small = _load_font(12)

    arm = max(3, min(w, h) // 150 or 3)
    stroke = max(2, min(w, h) // 500 or 2)

    for m in POINT_MARKERS:
        pt = points_by_id.get(m.id)
        if not pt:
            continue
        x, y = float(pt[0]), float(pt[1])
        draw.line([(x - arm, y), (x + arm, y)], fill=0, width=stroke)
        draw.line([(x, y - arm), (x, y + arm)], fill=0, width=stroke)
        draw.ellipse(
            [x - arm - 1, y - arm - 1, x + arm + 1, y + arm + 1],
            outline=0,
            width=stroke,
        )

        label = m.letter
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx, ty = x - tw / 2, y - arm - th - 10
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

    for m in POINT_MARKERS:
        pt = points_by_id.get(m.id)
        if not pt:
            continue
        x, y = float(pt[0]), float(pt[1])
        payload["markers"].append(
            {
                "family": "point",
                "id": m.id,
                "letter": m.letter,
                "label_pt": m.label_pt,
                "points": [[x, y]],
            }
        )

    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _legend_lines() -> list[str]:
    return [f"{m.letter} — {m.label_pt}" for m in POINT_MARKERS]


def _draw_legend(
    draw: ImageDraw.ImageDraw,
    size: tuple[int, int],
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> None:
    w, h = size
    lines = [
        "EasyFeet — Marcador de pontos (referências)",
        "Versão do registo: " + JSON_VERSION,
        "Tipo de dados: pontos anatómicos",
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
