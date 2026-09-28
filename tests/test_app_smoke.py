"""无窗口环境下验证程序能启动并进入主菜单。"""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.app import GameApp  # noqa: E402
from src.state_machine import StateID  # noqa: E402


def test_app_reaches_main_menu_without_assets(tmp_path) -> None:
    app = GameApp(settings_path=tmp_path / "settings.json")

    exit_code = app.run(max_frames=10)

    assert exit_code == 0
    assert app.machine.current_id is StateID.MAIN_MENU
