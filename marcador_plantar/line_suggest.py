"""Sugestão de linhas A–D a partir da silhueta da pegada (PCA + larguras por faixa).

Usa apenas NumPy + PIL. Pressupõe pegada mais escura que o fundo (plantografia típica).
"""

from __future__ import annotations

import numpy as np
from PIL import Image

from marcador_plantar.definitions import LINE_MARKERS


def _pil_to_gray_u8(im: Image.Image) -> np.ndarray:
    if im.mode == "RGBA":
        rgb = Image.new("RGB", im.size, (255, 255, 255))
        rgb.paste(im, mask=im.split()[3])
        g = np.asarray(rgb.convert("L"), dtype=np.uint8)
    else:
        g = np.asarray(im.convert("L"), dtype=np.uint8)
    return g


def _otsu_threshold(gray: np.ndarray) -> int:
    """Limiar de Otsu em uint8 0–255."""
    hist = np.bincount(gray.ravel(), minlength=256).astype(np.float64)
    total = gray.size
    sum_all = np.dot(np.arange(256), hist)
    sum_b = 0.0
    w_b = 0.0
    max_var = -1.0
    thresh = 127
    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (sum_all - sum_b) / w_f
        var_between = w_b * w_f * (m_b - m_f) ** 2
        if var_between > max_var:
            max_var = var_between
            thresh = t
    return int(thresh)


def _dilate_xy(mask: np.ndarray, iterations: int = 2) -> np.ndarray:
    """Dilatação 8-vizinhos (fecha pequenos buracos)."""
    m = mask.astype(bool)
    h, w = m.shape
    for _ in range(iterations):
        nxt = m.copy()
        ys, xs = np.where(m)
        for y, x in zip(ys, xs):
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w:
                        nxt[yy, xx] = True
        m = nxt
    return m


def _foot_mask(gray: np.ndarray) -> np.ndarray:
    t = _otsu_threshold(gray)
    m_dark = gray < t
    m_light = gray > t
    if m_dark.mean() > 0.88:
        m = m_light
    elif m_light.mean() > 0.88:
        m = m_dark
    else:
        m = m_dark if m_dark.mean() < m_light.mean() else m_light
    m = _dilate_xy(m, iterations=2)
    return m


def _chord_at_s(
    mask: np.ndarray, mu: np.ndarray, v: np.ndarray, u: np.ndarray, s0: float
) -> tuple[float, tuple[float, float], tuple[float, float]] | None:
    """Comprimento da corda perpendicular ao eixo em s0; devolve (width, p_left, p_right)."""
    h, w = mask.shape
    p0 = mu + v * float(s0)
    max_r = int(max(h, w) * 1.2)
    hits: list[tuple[float, float, float]] = []
    for k in range(-max_r, max_r + 1):
        x = int(round(p0[0] + u[0] * k))
        y = int(round(p0[1] + u[1] * k))
        if 0 <= x < w and 0 <= y < h and mask[y, x]:
            proj = float(x) * u[0] + float(y) * u[1]
            hits.append((proj, float(x), float(y)))
    if len(hits) < 2:
        return None
    hits.sort(key=lambda t: t[0])
    _, x1, y1 = hits[0]
    _, x2, y2 = hits[-1]
    width = float(np.hypot(x2 - x1, y2 - y1))
    return width, (x1, y1), (x2, y2)


def suggest_abcd_segments(im: Image.Image) -> dict[str, tuple[tuple[float, float], tuple[float, float]]]:
    """
    Calcula segmentos A–D em coordenadas de pixels da imagem original (igual ao desenho manual).

    Raises:
        ValueError: se não houver máscara utilizável.
    """
    gray = _pil_to_gray_u8(im)
    h, w = gray.shape
    if h < 24 or w < 24:
        raise ValueError("Imagem demasiado pequena.")

    # Processamento em escala reduzida para robustez e velocidade
    max_side = 520
    scale = min(1.0, max_side / max(h, w))
    if scale < 1.0:
        nh, nw = int(round(h * scale)), int(round(w * scale))
        small = np.array(Image.fromarray(gray).resize((nw, nh), Image.Resampling.LANCZOS))
    else:
        small = gray
        nh, nw = h, w
        scale = 1.0

    mask = _foot_mask(small)
    area = int(mask.sum())
    if area < 120:
        raise ValueError("Não foi possível isolar a pegada (área demasiado pequena). Ajuste contraste ou use a heurística simples.")

    ys, xs = np.where(mask)
    pts = np.stack([xs.astype(np.float64), ys.astype(np.float64)], axis=1)
    mu_s = pts.mean(axis=0)
    centered = pts - mu_s
    cov = np.cov(centered.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    v_s = eigvecs[:, int(np.argmax(eigvals))]
    nrm = float(np.linalg.norm(v_s)) or 1.0
    v_s = v_s / nrm
    u_s = np.array([-float(v_s[1]), float(v_s[0])])

    s_proj = centered @ v_s
    s_min = float(s_proj.min())
    s_max = float(s_proj.max())
    rng = s_max - s_min + 1e-6

    n_samples = 72
    ss = np.linspace(s_min + 0.02 * rng, s_max - 0.02 * rng, n_samples)
    widths: list[float] = []
    chords: list[tuple[tuple[float, float], tuple[float, float]] | None] = []
    for s0 in ss:
        ch = _chord_at_s(mask, mu_s, v_s, u_s, float(s0))
        if ch is None:
            widths.append(0.0)
            chords.append(None)
        else:
            w0, a, b = ch
            widths.append(w0)
            chords.append((a, b))
    widths_np = np.array(widths, dtype=np.float64)

    # Faixas ao longo do eixo (mesma ideia das regras textuais: antepé / médio / retropé)
    i0 = int(n_samples * 0.52)
    i1 = int(n_samples * 0.98)
    slice_fore = slice(max(i0, 0), i1)
    i_mid0 = int(n_samples * 0.12)
    i_mid1 = int(n_samples * 0.62)
    slice_mid = slice(i_mid0, max(i_mid1, i_mid0 + 2))
    slice_hind = slice(0, int(n_samples * 0.42))

    def pick_argmax(sl: slice) -> int:
        seg = widths_np[sl]
        if seg.size == 0:
            return n_samples // 2
        if float(np.max(seg)) < 1.0:
            return (sl.start or 0) + seg.size // 2
        rel = int(np.argmax(seg))
        start = sl.start or 0
        return start + rel

    def pick_argmin(sl: slice) -> int:
        seg = widths_np[sl]
        if seg.size == 0:
            return n_samples // 2
        if float(np.min(seg)) == float(np.max(seg)):
            return (sl.start or 0) + seg.size // 2
        rel = int(np.argmin(seg))
        start = sl.start or 0
        return start + rel

    iB = pick_argmax(slice_fore)
    iC = pick_argmin(slice_mid)
    iD = pick_argmax(slice_hind)

    def to_full(p: tuple[float, float]) -> tuple[float, float]:
        return (p[0] / scale, p[1] / scale)

    s_lo = s_min + 0.03 * rng
    s_hi = s_max - 0.03 * rng
    ch_a0 = _chord_at_s(mask, mu_s, v_s, u_s, s_lo)
    ch_a1 = _chord_at_s(mask, mu_s, v_s, u_s, s_hi)
    if ch_a0 and ch_a1:
        _, al0, bl0 = ch_a0
        _, al1, bl1 = ch_a1
        mid_lo = ((al0[0] + bl0[0]) * 0.5, (al0[1] + bl0[1]) * 0.5)
        mid_hi = ((al1[0] + bl1[0]) * 0.5, (al1[1] + bl1[1]) * 0.5)
        seg_a = (to_full(mid_lo), to_full(mid_hi))
    else:
        ys2, xs2 = np.where(mask)
        seg_a = (
            to_full((float(xs2.min()), float(ys2.mean()))),
            to_full((float(xs2.max()), float(ys2.mean()))),
        )

    def seg_from_chord(idx: int) -> tuple[tuple[float, float], tuple[float, float]]:
        ch = chords[idx]
        if ch is None:
            # fallback: linha curta no centro
            cx, cy = float(mu_s[0] / scale), float(mu_s[1] / scale)
            return (cx - 10, cy), (cx + 10, cy)
        return to_full(ch[0]), to_full(ch[1])

    seg_b = seg_from_chord(iB)
    seg_c = seg_from_chord(iC)
    seg_d = seg_from_chord(iD)

    out: dict[str, tuple[tuple[float, float], tuple[float, float]]] = {}
    out[LINE_MARKERS[0].id] = seg_a
    out[LINE_MARKERS[1].id] = seg_b
    out[LINE_MARKERS[2].id] = seg_c
    out[LINE_MARKERS[3].id] = seg_d
    return out
