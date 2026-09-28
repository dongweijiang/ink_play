"""《墨痕登塔》桌面程序入口。"""

from __future__ import annotations

from src.app import GameApp


def main() -> int:
    """启动游戏并在正常退出时返回零。"""
    return GameApp().run()


if __name__ == "__main__":
    raise SystemExit(main())
