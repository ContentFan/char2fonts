# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "fonttools",
# ]
# ///
"""
char2fonts: Find which fonts contain specific characters.
"""

import sys
import unicodedata
from pathlib import Path
from functools import lru_cache

from fontTools.ttLib import TTFont


def discover_fonts(font_dir: str = "/usr/share/fonts/") -> list[Path]:
    """Discover all TTF font files in the specified directory."""
    return list(Path(font_dir).rglob("*.ttf"))


def char_in_font(unicode_char: str, font: TTFont) -> bool:
    """Check if a Unicode character is supported by the given font."""
    if "cmap" not in font:
        return False

    for cmap in font["cmap"].tables:
        if cmap.isUnicode():
            if ord(unicode_char) in cmap.cmap:
                return True
    return False


def get_font_name(font: TTFont) -> str:
    """Extract a human-readable name from the font."""
    try:
        # Try to get the font name from the name table
        if "name" in font:
            for record in font["name"].names:
                # Family name (nameID 1) or Full name (nameID 4)
                if record.nameID in (1, 4) and record.platformID == 3 and record.platEncID == 1:
                    return record.toUnicode()
        return "Unknown font"
    except Exception:
        return "Unknown font"


def get_char_description(char: str) -> str:
    """Get a human-readable description of a character."""
    try:
        name = unicodedata.name(char)
        return f"{char} (U+{ord(char):04X} {name})"
    except ValueError:
        # Character has no Unicode name
        return f"{char} (U+{ord(char):04X})"


@lru_cache(maxsize=512)
def load_font(fontpath: str) -> TTFont | None:
    """Load a font file with caching to avoid repeated disk I/O."""
    try:
        return TTFont(fontpath)
    except Exception:
        return None


def find_fonts_for_char(char: str, font_paths: list[Path]) -> None:
    """Find and display all fonts that contain the given character."""
    print(f"\nSearching for: {get_char_description(char)}")
    print("-" * 70)

    found = False
    for fontpath in font_paths:
        font = load_font(str(fontpath))
        if font and char_in_font(char, font):
            font_name = get_font_name(font)
            print(f"  {font_name} → {fontpath}")
            found = True

    if not found:
        print("  No fonts found containing this character.")


def main():
    """Main entry point."""
    if not sys.argv[1:]:
        print("Usage: python char2font.py <character> [<character> ...]")
        print("Find which fonts contain specific Unicode characters.")
        sys.exit(1)

    print("Discovering fonts...")
    font_paths = discover_fonts()
    print(f"Found {len(font_paths)} fonts.\n")

    for char in sys.argv[1:]:
        find_fonts_for_char(char, font_paths)


if __name__ == "__main__":
    main()
