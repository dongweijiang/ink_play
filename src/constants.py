"""应用级常量；业务规则常量将在规则层中单独定义。"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSET_ROOT = PROJECT_ROOT / "assets"
SAVE_ROOT = PROJECT_ROOT / "saves"
LOG_ROOT = PROJECT_ROOT / "logs"

WINDOW_TITLE = "墨痕登塔 · Inkbound Spire"
LOGICAL_SIZE = (1280, 720)
FPS = 60
SUPPORTED_RESOLUTIONS = ((1280, 720), (1600, 900), (1920, 1080))

PAPER = (238, 231, 207)
PAPER_DARK = (205, 195, 166)
INK = (27, 29, 34)
INK_SOFT = (63, 67, 75)
VERMILION = (207, 63, 48)
CYAN_GLOW = (62, 202, 211)
GOLD = (222, 174, 76)
DISABLED = (118, 116, 108)
SHADOW = (14, 16, 20)
