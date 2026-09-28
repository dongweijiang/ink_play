"""状态之间共享的应用服务。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from src.resources import ResourceManager
from src.settings_model import AppSettings


@dataclass(slots=True)
class StateServices:
    """向状态提供资源和受控的应用操作。"""

    resources: ResourceManager
    settings: AppSettings
    quit_game: Callable[[], None]
    apply_display: Callable[[], None]
    persist_settings: Callable[[], None]
