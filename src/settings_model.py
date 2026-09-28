"""与存档分离的本地显示和音量设置。"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.constants import LOGICAL_SIZE, SUPPORTED_RESOLUTIONS

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class AppSettings:
    """玩家可修改且不包含秘密信息的应用设置。"""

    music_volume: int = 70
    sfx_volume: int = 80
    fullscreen: bool = False
    resolution: tuple[int, int] = LOGICAL_SIZE
    input_mode: str = "auto"
    ai_mode: str = "offline"

    def normalized(self) -> AppSettings:
        """返回限制到安全取值范围的设置副本。"""
        resolution = self.resolution if self.resolution in SUPPORTED_RESOLUTIONS else LOGICAL_SIZE
        input_mode = self.input_mode if self.input_mode in {"auto", "keyboard_mouse", "gamepad"} else "auto"
        return AppSettings(
            music_volume=max(0, min(100, int(self.music_volume))),
            sfx_volume=max(0, min(100, int(self.sfx_volume))),
            fullscreen=bool(self.fullscreen),
            resolution=resolution,
            input_mode=input_mode,
            ai_mode="offline",
        )

    def to_dict(self) -> dict[str, Any]:
        """生成可安全写入 JSON 的普通字典。"""
        data = asdict(self.normalized())
        data["resolution"] = list(data["resolution"])
        return data


def load_settings(path: Path) -> AppSettings:
    """载入设置；不存在或损坏时记录原因并返回默认值。"""
    if not path.exists():
        return AppSettings()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        resolution_raw = raw.get("resolution", LOGICAL_SIZE)
        settings = AppSettings(
            music_volume=raw.get("music_volume", 70),
            sfx_volume=raw.get("sfx_volume", 80),
            fullscreen=raw.get("fullscreen", False),
            resolution=tuple(resolution_raw),
            input_mode=raw.get("input_mode", "auto"),
            ai_mode=raw.get("ai_mode", "offline"),
        )
        return settings.normalized()
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        LOGGER.warning("设置文件无法读取，将使用默认设置：%s", exc)
        return AppSettings()


def save_settings(path: Path, settings: AppSettings) -> None:
    """先写临时文件再替换，避免设置文件写到一半。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(
        json.dumps(settings.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(temp_path, path)
