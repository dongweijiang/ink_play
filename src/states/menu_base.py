"""菜单状态的焦点和鼠标交互基类。"""

from __future__ import annotations

from collections.abc import Callable

import pygame

from src.state_machine import BaseState
from src.ui.widgets import Button


class MenuState(BaseState):
    """提供方向键、Enter 和鼠标一致的按钮导航。"""

    def __init__(self) -> None:
        self.buttons: list[Button] = []
        self.actions: list[Callable[[], None]] = []
        self.focus_index = 0
        self.mouse_position: tuple[int, int] | None = None

    def enter(self) -> None:
        self.focus_index = self._first_enabled_index()
        self._sync_focus()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.mouse_position = event.pos
            for index, button in enumerate(self.buttons):
                if button.contains(event.pos):
                    self.focus_index = index
                    self._sync_focus()
                    break
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for index, button in enumerate(self.buttons):
                if button.contains(event.pos):
                    self.focus_index = index
                    self._sync_focus()
                    self.actions[index]()
                    return
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._move_focus(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._move_focus(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.buttons[self.focus_index].enabled:
                    self.actions[self.focus_index]()

    def _first_enabled_index(self) -> int:
        for index, button in enumerate(self.buttons):
            if button.enabled:
                return index
        raise RuntimeError("菜单至少需要一个可用按钮")

    def _move_focus(self, direction: int) -> None:
        for _ in self.buttons:
            self.focus_index = (self.focus_index + direction) % len(self.buttons)
            if self.buttons[self.focus_index].enabled:
                self._sync_focus()
                return

    def _sync_focus(self) -> None:
        for index, button in enumerate(self.buttons):
            button.focused = index == self.focus_index and button.enabled
