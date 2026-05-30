from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def _row_bounds(mask: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ys = np.where(mask.any(axis=1))[0]
    left = np.full(mask.shape[0], -1, dtype=int)
    right = np.full(mask.shape[0], -1, dtype=int)
    for y in ys:
        xs = np.where(mask[y])[0]
        left[y] = xs.min()
        right[y] = xs.max()
    return ys, left, right


def annotate_footprint(input_path: Path, output_path: Path) -> None:
    image = Image.open(input_path).convert("L")
    arr = np.array(image)

    # Footprint is darker than background on plantigraph image.
    mask = arr < 235
    ys, left, right = _row_bounds(mask)
    if ys.size == 0:
        raise ValueError(f"No footprint detected in {input_path}")

    y_min, y_max = int(ys.min()), int(ys.max())
    h = y_max - y_min + 1

    # Regions along vertical axis.
    fore_start, fore_end = y_min, y_min + int(h * 0.35)
    mid_start, mid_end = y_min + int(h * 0.35), y_min + int(h * 0.72)
    heel_start, heel_end = y_min + int(h * 0.72), y_max

    widths = right - left + 1

    def region_extrema(y0: int, y1: int, mode: str = "max") -> int:
        region_ys = ys[(ys >= y0) & (ys <= y1)]
        if region_ys.size == 0:
            return int((y0 + y1) // 2)
        region_widths = widths[region_ys]
        idx = int(np.argmax(region_widths) if mode == "max" else np.argmin(region_widths))
        return int(region_ys[idx])

    y_fore = region_extrema(fore_start, fore_end, "max")
    y_mid = region_extrema(mid_start, mid_end, "min")
    y_heel = region_extrema(heel_start, heel_end, "max")

    def center_at(y: int) -> tuple[int, int]:
        return int((left[y] + right[y]) / 2), int(y)

    fore_center = center_at(y_fore)
    heel_center = center_at(y_heel)
    mid_center = center_at(y_mid)

    rgb = image.convert("RGB")
    draw = ImageDraw.Draw(rgb)

    # Horizontal width references.
    draw.line([(int(left[y_fore]), y_fore), (int(right[y_fore]), y_fore)], fill=(0, 180, 255), width=4)
    draw.line([(int(left[y_mid]), y_mid), (int(right[y_mid]), y_mid)], fill=(255, 180, 0), width=4)
    draw.line([(int(left[y_heel]), y_heel), (int(right[y_heel]), y_heel)], fill=(120, 255, 120), width=4)

    # Longitudinal axis from heel to forefoot.
    draw.line([heel_center, fore_center], fill=(255, 0, 80), width=4)

    # Midfoot marker.
    r = 8
    draw.ellipse(
        [(mid_center[0] - r, mid_center[1] - r), (mid_center[0] + r, mid_center[1] + r)],
        outline=(255, 220, 0),
        width=3,
    )

    # Pixel scale reference (not physical scale).
    margin = 30
    bar_len = 100
    bar_y = y_max + margin if (y_max + margin + 20) < arr.shape[0] else arr.shape[0] - 30
    bar_x0 = 30
    bar_x1 = bar_x0 + bar_len
    draw.line([(bar_x0, bar_y), (bar_x1, bar_y)], fill=(0, 0, 0), width=4)
    draw.line([(bar_x0, bar_y - 5), (bar_x0, bar_y + 5)], fill=(0, 0, 0), width=3)
    draw.line([(bar_x1, bar_y - 5), (bar_x1, bar_y + 5)], fill=(0, 0, 0), width=3)
    draw.text((bar_x1 + 10, bar_y - 10), "100 px", fill=(0, 0, 0))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rgb.save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Annotate plantar footprint images with reference lines.")
    parser.add_argument("folder", help="Folder containing footprint images.")
    args = parser.parse_args()

    base = Path(args.folder)
    if not base.exists():
        raise FileNotFoundError(f"Folder not found: {base}")

    candidates = []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        candidates.extend(base.glob(ext))
    candidates = [p for p in candidates if "_annotado" not in p.stem.lower()]
    if not candidates:
        raise ValueError(f"No footprint images found in: {base}")

    for src in sorted(candidates):
        dst = src.with_name(f"{src.stem}_annotado{src.suffix}")
        annotate_footprint(src, dst)
        print(f"Generated: {dst}")


if __name__ == "__main__":
    main()
