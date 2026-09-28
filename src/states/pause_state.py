"""暂停菜单状态。"""

from __future__ import annotations

import pygame

from src.constants import INK
from src.state_machine import StateID, StateMachine
from src.states.menu_base import MenuState
from src.states.shared import StateServices
from src.ui.widgets import Button, draw_footer, draw_title


class PauseState(MenuState):
    """返回此前局内状态，或安全离开当前演示。"""

    def __init__(self, machine: StateMachine, services: StateServices) -> None:
        super().__init__()
        self.machine = machine
        self.services = services
        labels = ["继续", "返回主菜单", "退出游戏"]
        self.buttons = [
            Button(pygame.Rect(470, 275 + index * 78, 340, 56), label)
            for index, label in enumerate(labels)
        ]
        self.actions = [self.machine.request_resume, self._to_menu, self.services.quit_game]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.machine.request_resume()
            return
        super().handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(INK)
        draw_title(surface, self.services.resources, "旅程暂停", "墨迹会停在原处")
        for button in self.buttons:
            button.draw(surface, self.services.resources, self.mouse_position)
        draw_footer(surface, self.services.resources, "Esc 继续 · 设置将在主菜单中保留")

    def _to_menu(self) -> None:
        self.machine.clear_resume()
        self.machine.request(StateID.MAIN_MENU)
