#!/usr/bin/env python3
"""Regenerate the manager icons. Dependency: python -m pip install Pillow."""

from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "manager/app/src/main/res"


def main():
    with Image.open(ROOT / "branding/manager-icon.png") as source:
        icon = ImageOps.fit(ImageOps.exif_transpose(source).convert("RGB"), (640, 640))
    destination = RES / "drawable-nodpi"
    destination.mkdir(exist_ok=True)
    icon.save(destination / "ic_launcher_foreground.png", optimize=True)
    # Android themed icons tint the alpha mask, so discard the white background.
    alpha = ImageOps.invert(ImageOps.grayscale(icon))
    monochrome = Image.new("RGBA", icon.size, (0, 0, 0, 0))
    monochrome.putalpha(alpha)
    monochrome.save(destination / "ic_launcher_monochrome_image.png", optimize=True)
    for density, size in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96),
                          ("xxhdpi", 144), ("xxxhdpi", 192)):
        directory = RES / f"mipmap-{density}"
        directory.mkdir(exist_ok=True)
        icon.resize((size, size), Image.Resampling.LANCZOS).save(
            directory / "ic_launcher.png", optimize=True)
    print("Generated launcher, adaptive foreground, splash and themed icon images")


if __name__ == "__main__":
    main()
