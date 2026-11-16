"""Safe creative-memory and user-asset profiles for ShortGPT SuperTest.

Read-only files travel with the repository across ephemeral GitHub Actions runs.
They do not train the AI model or add permanent neural memory.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from PIL import Image, ImageOps

LOCATIONS = ("toilet", "school", "garden", "street", "office", "park")
DEFAULT_COLORS = {
    "shirt": "#4a9dba",
    "skin": "#f4c5a2",
    "hair": "#272e38",
    "pants": "#1f2732",
    "shoes": "#232b37",
}
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


class AssetError(ValueError):
    pass


@dataclass
class AssetPack:
    root: Path | None = None
    character: dict = field(default_factory=lambda: dict(DEFAULT_COLORS))
    layout: dict = field(default_factory=lambda: {"door_x": 0.73, "start_x": 0.18})
    notes: str = ""
    notes_files: tuple[str, ...] = ()

    def find_background(self, location: str) -> Path | None:
        if self.root is None or location not in LOCATIONS:
            return None
        for suffix in ("png", "jpg", "jpeg", "webp"):
            p = self.root / f"background_{location}.{suffix}"
            if p.is_file():
                verify_file(p, self.root)
                return p
        return None

    def background(self, location: str, size: tuple[int, int]) -> Image.Image | None:
        p = self.find_background(location)
        if p is None:
            return None
        with Image.open(p) as im:
            return ImageOps.fit(im.convert("RGB"), size, method=Image.Resampling.LANCZOS)


def verify_file(file: Path, root: Path) -> None:
    root = root.resolve()
    if file.is_symlink() or not file.resolve().is_relative_to(root):
        raise AssetError("Asset paths cannot be symlinks or escape the profile folder")
    if file.stat().st_size > 12 * 1024 * 1024:
        raise AssetError("Asset image exceeds 12 MiB; resize/compress before uploading")
    with Image.open(file) as im:
        if im.format not in ("PNG", "JPEG", "WEBP"):
            raise AssetError("Only PNG/JPEG/WEBP images are supported")
        if im.width > 4096 or im.height > 4096 or im.width * im.height > 12000000:
            raise AssetError("Asset image is too large (max 12 megapixels)")
        im.verify()


def read_text(root: Path, name: str, limit: int = 2200) -> str:
    p = root / name
    if not p.exists():
        return ""
    if p.is_symlink() or not p.resolve().is_relative_to(root):
        raise AssetError("Invalid creative memory file path")
    if p.stat().st_size > limit * 3:
        raise AssetError("Creative memory text file is too large: " + name)
    return p.read_text(encoding="utf-8")[:limit].strip()


def load_asset_pack(path: Path | str | None = None) -> AssetPack:
    if path is None:
        return AssetPack()
    root = Path(path).resolve()
    if not root.is_dir():
        raise AssetError("Asset profile directory does not exist: " + str(root))
    pack = AssetPack(root=root)
    settings_file = root / "settings.json"
    if settings_file.exists():
        if settings_file.is_symlink() or settings_file.stat().st_size > 16384:
            raise AssetError("Invalid settings.json (max 16 KB)")
        data = json.loads(settings_file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise AssetError("settings.json must contain one JSON object")
        colors = data.get("character", {})
        if not isinstance(colors, dict):
            raise AssetError("character must be an object")
        for key, value in colors.items():
            if key not in DEFAULT_COLORS:
                raise AssetError("Unsupported character attribute: " + str(key))
            if not isinstance(value, str) or not HEX_COLOR.fullmatch(value):
                raise AssetError("Character colors must be 6-digit hexadecimal colors")
            pack.character[key] = value
        layout = data.get("layout", {})
        if not isinstance(layout, dict):
            raise AssetError("layout must be an object")
        for key, value in layout.items():
            if key not in ("door_x", "start_x"):
                raise AssetError("Unsupported layout key: " + str(key))
            if isinstance(value, bool) or not isinstance(value, (float, int)):
                raise AssetError("Layout coordinates must be numeric")
            if not 0.05 <= float(value) <= 0.95:
                raise AssetError("Layout positions must be within 0.05..0.95")
            pack.layout[key] = float(value)
        if pack.layout["door_x"] - pack.layout["start_x"] < 0.15:
            raise AssetError("door_x must be sufficiently ahead of start_x")

    sections = []
    names = []
    for fname in ("style.md", "story_bible.md", "memory.md"):
        v = read_text(root, fname)
        if v:
            sections.append(fname + ":\n" + v)
            names.append(fname)
    skills_root = root / "skills"
    if skills_root.is_dir():
        if skills_root.is_symlink():
            raise AssetError("skills cannot be a symlink")
        for f in sorted(skills_root.glob("*.md"))[:6]:
            content = read_text(skills_root, "ignored") if False else read_text(skills_root, f.name, 1100)
            if content:
                sections.append("skills/" + f.name + ":\n" + content)
                names.append("skills/" + f.name)
    pack.notes = "\n\n".join(sections)[:6500]
    pack.notes_files = tuple(names)
    return pack


def profile_info(pack: AssetPack) -> dict:
    return {
        "path": str(pack.root) if pack.root is not None else None,
        "character_colors": dict(pack.character),
        "layout": dict(pack.layout),
        "memory_documents": list(pack.notes_files),
        "available_backgrounds": [place for place in LOCATIONS if pack.find_background(place)],
    }
