"""启动检查状态。"""

from __future__ import annotations

import pygame

from src.constants import INK, PAPER
from src.state_machine import BaseState, StateID, StateMachine
from src.states.shared import StateServices


class BootState(BaseState):
    """完成最小资源检查后转入主菜单。"""

    def __init__(self, machine: StateMachine, services: StateServices) -> None:
        self.machine = machine
        self.services = services
        self._elapsed = 0.0

    def enter(self) -> None:
        self._elapsed = 0.0
        self.services.resources.font(24)

    def update(self, dt: float) -> None:
        self._elapsed += dt
        if self._elapsed >= 0.08:
            self.machine.request(StateID.MAIN_MENU)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(INK)
        text = self.services.resources.font(30).render("墨迹正在苏醒……", True, PAPER)
        surface.blit(text, text.get_rect(center=surface.get_rect().center))
