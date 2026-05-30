from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Logo_EasyFeet.png"
TARGET = ROOT / "Imagens" / "EasyFeet"
SYMBOL_SOURCE = TARGET / "easyfeet_symbol.png"


def resize_keep_aspect(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    result = image.copy()
    result.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (35, 0, 8))
    x = (size[0] - result.width) // 2
    y = (size[1] - result.height) // 2
    canvas.paste(result, (x, y))
    return canvas


def add_safe_padding(image: Image.Image, padding_ratio: float = 0.16) -> Image.Image:
    """Add breathing room around artwork to avoid visual clipping in icons."""
    w, h = image.size
    pad_x = int(w * padding_ratio)
    pad_y = int(h * padding_ratio)
    canvas = Image.new("RGB", (w + 2 * pad_x, h + 2 * pad_y), (35, 0, 8))
    canvas.paste(image, (pad_x, pad_y))
    return canvas


def make_background_transparent(image: Image.Image, tolerance: int = 26) -> Image.Image:
    """Chroma-key the dominant corner background color to transparent."""
    rgba = image.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    bg = px[0, 0][:3]

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if (
                abs(r - bg[0]) <= tolerance
                and abs(g - bg[1]) <= tolerance
                and abs(b - bg[2]) <= tolerance
            ):
                px[x, y] = (r, g, b, 0)
            else:
                px[x, y] = (r, g, b, a)
    return rgba


def resize_keep_aspect_transparent(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    result = image.copy()
    result.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    x = (size[0] - result.width) // 2
    y = (size[1] - result.height) // 2
    canvas.paste(result, (x, y), result if result.mode == "RGBA" else None)
    return canvas


def crop_symbol_square(image: Image.Image) -> Image.Image:
    w, h = image.size
    # Crop the upper central symbol area of the current logo.
    left = int(w * 0.30)
    top = int(h * 0.08)
    right = int(w * 0.70)
    bottom = int(h * 0.57)
    cropped = image.crop((left, top, right, bottom))

    side = max(cropped.size)
    canvas = Image.new("RGB", (side, side), (35, 0, 8))
    x = (side - cropped.width) // 2
    y = (side - cropped.height) // 2
    canvas.paste(cropped, (x, y))
    return canvas


def save_sizes(base: Image.Image, names_and_sizes: list[tuple[str, tuple[int, int]]]) -> None:
    for filename, size in names_and_sizes:
        output = resize_keep_aspect(base, size)
        output.save(TARGET / filename, optimize=True)
        print(f"Generated: {TARGET / filename}")


def save_ico(base: Image.Image, filename: str) -> None:
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icon_with_margin = add_safe_padding(base, padding_ratio=0.18)
    icon_base = resize_keep_aspect(icon_with_margin, (256, 256))
    output_path = TARGET / filename
    # Use BMP payload for maximum compatibility with native Windows viewers (e.g. Paint).
    icon_base.save(output_path, format="ICO", sizes=icon_sizes, bitmap_format="bmp")
    print(f"Generated: {output_path}")


def save_ico_transparent(base: Image.Image, filename: str) -> None:
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    transparent = make_background_transparent(base)
    icon_base = resize_keep_aspect_transparent(transparent, (256, 256))
    output_path = TARGET / filename
    # PNG payload keeps alpha channel for transparent icon backgrounds.
    icon_base.save(output_path, format="ICO", sizes=icon_sizes)
    print(f"Generated: {output_path}")


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Source logo not found: {SOURCE}")

    TARGET.mkdir(parents=True, exist_ok=True)
    logo = Image.open(SOURCE).convert("RGB")
    logo.save(TARGET / "easyfeet_logo_original.png", optimize=True)
    print(f"Generated: {TARGET / 'easyfeet_logo_original.png'}")

    # Square brand assets.
    save_sizes(
        logo,
        [
            ("easyfeet_logo_square_1024.png", (1024, 1024)),
            ("easyfeet_logo_square_512.png", (512, 512)),
            ("easyfeet_logo_square_256.png", (256, 256)),
            ("easyfeet_logo_square_128.png", (128, 128)),
        ],
    )

    # Header style assets.
    save_sizes(
        logo,
        [
            ("easyfeet_logo_header_1600x500.png", (1600, 500)),
            ("easyfeet_logo_header_1200x300.png", (1200, 300)),
        ],
    )

    # Symbol/icon assets.
    # Prefer a manually prepared symbol file to avoid auto-crop issues.
    if SYMBOL_SOURCE.exists():
        symbol = Image.open(SYMBOL_SOURCE).convert("RGB")
        print(f"Using custom symbol source: {SYMBOL_SOURCE}")
    else:
        symbol = crop_symbol_square(logo)
        print("Custom symbol not found, using auto-cropped symbol from main logo.")

    symbol.save(TARGET / "easyfeet_symbol_original.png", optimize=True)
    print(f"Generated: {TARGET / 'easyfeet_symbol_original.png'}")
    save_sizes(
        symbol,
        [
            ("easyfeet_symbol_1024.png", (1024, 1024)),
            ("easyfeet_symbol_512.png", (512, 512)),
            ("easyfeet_symbol_256.png", (256, 256)),
            ("easyfeet_symbol_128.png", (128, 128)),
            ("easyfeet_favicon_48.png", (48, 48)),
            ("easyfeet_favicon_32.png", (32, 32)),
        ],
    )
    save_ico(symbol, "easyfeet_app_icon.ico")
    save_ico(logo, "easyfeet_app_icon_full_logo.ico")
    save_ico_transparent(symbol, "easyfeet_app_icon_transparente.ico")


if __name__ == "__main__":
    main()
