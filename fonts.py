"""Cross-platform font lookup for the overlay builders.

The overlay scripts were written on Windows against literal paths like
"C:/Windows/Fonts/arialbd.ttf", which makes them unrunnable anywhere else. They
now ask for a family here instead. Each family lists the Windows file first,
then the usual macOS and Linux equivalents, so a clone renders the same
overlays on any of the three as long as one of those faces is installed.

Override any single family with an environment variable, e.g.
    OVERLAY_FONT_ARIALBD=/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf
"""
import os

# Ordered by preference. The first path that exists wins.
FAMILIES = {
    "arial": [
        "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "arialbd": [
        "C:/Windows/Fonts/arialbd.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "impact": [
        "C:/Windows/Fonts/impact.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
        # No free Impact clone ships by default; a heavy sans keeps the meme
        # caption legible even though the letterforms differ.
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "consolab": [
        "C:/Windows/Fonts/consolab.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
    ],
    "georgiab": [
        "C:/Windows/Fonts/georgiab.ttf",
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Georgia_Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ],
}


def font_path(family: str) -> str:
    """Absolute path to an installed font for `family`.

    Raises rather than falling back to PIL's bitmap default, because a silent
    fallback produces overlays at the wrong size and they only get noticed
    after a full render.
    """
    override = os.environ.get(f"OVERLAY_FONT_{family.upper()}")
    if override:
        return override
    for path in FAMILIES[family]:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"No font found for {family!r}. Install one of: {FAMILIES[family]}, "
        f"or set OVERLAY_FONT_{family.upper()} to a .ttf path."
    )


if __name__ == "__main__":
    for name in FAMILIES:
        try:
            print(f"{name:10} {font_path(name)}")
        except FileNotFoundError as exc:
            print(f"{name:10} MISSING - {exc}")
