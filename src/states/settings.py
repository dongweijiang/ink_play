"""设置菜单状态。"""

from __future__ import annotations

import pygame

from src.constants import INK, SUPPORTED_RESOLUTIONS
from src.state_machine import StateID, StateMachine
from src.states.menu_base import MenuState
from src.states.shared import StateServices
from src.ui.widgets import Button, draw_footer, draw_title


class SettingsState(MenuState):
    """调整音量、显示和输入偏好。"""

    def __init__(self, machine: StateMachine, services: StateServices) -> None:
        super().__init__()
        self.machine = machine
        self.services = services
        self.buttons = [
            Button(pygame.Rect(410, 205 + index * 64, 460, 48), "") for index in range(7)
        ]
        self.buttons[5].enabled = False
        self.actions = [
            lambda: self._adjust_volume("music_volume"),
            lambda: self._adjust_volume("sfx_volume"),
            self._toggle_fullscreen,
            self._cycle_resolution,
            self._cycle_input,
            lambda: None,
            self._back,
        ]
        self._refresh_labels()

    def enter(self) -> None:
        self._refresh_labels()
        super().enter()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._back()
            return
        super().handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(INK)
        draw_title(surface, self.services.resources, "设置", "所有设置均可在离线模式使用")
        for button in self.buttons:
            button.draw(surface, self.services.resources, self.mouse_position)
        draw_footer(surface, self.services.resources, "点击项目切换 · Esc 保存并返回")

    def _adjust_volume(self, field: str) -> None:
        current = getattr(self.services.settings, field)
        setattr(self.services.settings, field, (current + 10) % 110)
        self._refresh_labels()

    def _toggle_fullscreen(self) -> None:
        self.services.settings.fullscreen = not self.services.settings.fullscreen
        self.services.apply_display()
        self._refresh_labels()

    def _cycle_resolution(self) -> None:
        current = self.services.settings.resolution
        index = SUPPORTED_RESOLUTIONS.index(current) if current in SUPPORTED_RESOLUTIONS else 0
        self.services.settings.resolution = SUPPORTED_RESOLUTIONS[(index + 1) % len(SUPPORTED_RESOLUTIONS)]
        self.services.apply_display()
        self._refresh_labels()

    def _cycle_input(self) -> None:
        modes = ("auto", "keyboard_mouse", "gamepad")
        index = modes.index(self.services.settings.input_mode)
        self.services.settings.input_mode = modes[(index + 1) % len(modes)]
        self._refresh_labels()

    def _back(self) -> None:
        self.services.persist_settings()
        self.machine.request(StateID.MAIN_MENU)

    def _refresh_labels(self) -> None:
        settings = self.services.settings
        input_labels = {"auto": "自动", "keyboard_mouse": "键鼠", "gamepad": "手柄"}
        width, height = settings.resolution
        labels = [
            f"音乐音量：{settings.music_volume}%",
            f"音效音量：{settings.sfx_volume}%",
            f"全屏：{'开' if settings.fullscreen else '关'}",
            f"窗口分辨率：{width}×{height}",
            f"输入方式：{input_labels[settings.input_mode]}",
            "AI 识别：离线（第 7 轮开放）",
            "保存并返回",
        ]
        for button, label in zip(self.buttons, labels, strict=True):
            button.label = label
