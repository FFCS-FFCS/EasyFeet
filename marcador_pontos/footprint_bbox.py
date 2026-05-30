"""Deteção simples da região da pegada (P&B) para sugerir pontos dentro da silhueta."""

from __future__ import annotations

from PIL import Image


def _to_grayscale(src: Image.Image) -> Image.Image:
    if src.mode == "RGBA":
        rgb = Image.new("RGB", src.size, (255, 255, 255))
        rgb.paste(src, mask=src.split()[3])
        return rgb.convert("L")
    return src.convert("L")


def detect_plantar_bbox(
    pil_image: Image.Image,
    *,
    area_min_frac: float = 0.03,
    area_max_frac: float = 0.92,
    inset_frac: float = 0.02,
) -> tuple[int, int, int, int]:
    """
    Devolve (left, top, right, bottom) em pixels da imagem original.
    Usa pixels mais escuros que um limiar adaptativo (fundo claro → pegada mais escura).
    Se não encontrar região plausível, usa margens sobre a imagem inteira.
    """
    gray = _to_grayscale(pil_image)
    w, h = gray.size
    if w < 8 or h < 8:
        return 0, 0, w, h

    def bbox_for_thr(thr: int) -> tuple[int, int, int, int] | None:
        mask = gray.point(lambda p, t=thr: 255 if p < t else 0)
        return mask.getbbox()

    chosen: tuple[int, int, int, int] | None = None
    for thr in (250, 246, 242, 236, 228, 218, 205, 190):
        bb = bbox_for_thr(thr)
        if bb is None:
            continue
        l, t, r, b = bb
        area = (r - l) * (b - t)
        amin = area_min_frac * w * h
        amax = area_max_frac * w * h
        if area < amin or area > amax:
            continue
        chosen = bb
        break

    if chosen is None:
        # Pegada muito clara ou foto sem contraste: caixa útil central.
        mx = int(w * 0.06)
        my = int(h * 0.06)
        return mx, my, w - mx, h - my

    l, t, r, b = chosen
    iw, ih = r - l, b - t
    ins_x = max(1, int(iw * inset_frac))
    ins_y = max(1, int(ih * inset_frac))
    l = min(l + ins_x, r - 2)
    t = min(t + ins_y, b - 2)
    r = max(r - ins_x, l + 2)
    b = max(b - ins_y, t + 2)
    return l, t, r, b


def map_norm_to_image(
    bbox: tuple[int, int, int, int], nx: float, ny: float
) -> tuple[float, float]:
    """(nx,ny) em [0,1] dentro da caixa: 0,0 = canto sup.-esq. da caixa (tipico antepé no topo)."""
    l, t, r, b = bbox
    fw = float(r - l)
    fh = float(b - t)
    return l + nx * fw, t + ny * fh
