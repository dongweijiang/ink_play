"""第 1 轮用于验证暂停流程的地图占位状态。"""

from __future__ import annotations

import pygame

from src.constants import CYAN_GLOW, INK, PAPER, VERMILION
from src.state_machine import BaseState, StateID, StateMachine
from src.states.shared import StateServices
from src.ui.widgets import draw_footer, draw_title


class MapPlaceholderState(BaseState):
    """不含地图规则的演示场景；正式地图留到第 5 轮。"""

    def __init__(self, machine: StateMachine, services: StateServices) -> None:
        self.machine = machine
        self.services = services

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.machine.request(StateID.PAUSED, remember_current=True)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(INK)
        draw_title(surface, self.services.resources, "旅程骨架", "第 1 轮：状态机演示场景")
        points = [(250, 510), (450, 410), (650, 500), (850, 345), (1040, 250)]
        for start, end in zip(points, points[1:]):
            pygame.draw.line(surface, CYAN_GLOW, start, end, 4)
        for index, point in enumerate(points, start=1):
            pygame.draw.circle(surface, PAPER, point, 30)
            pygame.draw.circle(surface, VERMILION, point, 30, 4)
            number = self.services.resources.font(22).render(str(index), True, INK)
            surface.blit(number, number.get_rect(center=point))
        message = self.services.resources.font(27).render(
            "正式地图与战斗尚未实现；此页面只验证暂停与缩放。", True, PAPER
        )
        surface.blit(message, message.get_rect(center=(640, 610)))
        draw_footer(surface, self.services.resources, "按 Esc 打开暂停菜单 · F11 切换全屏")
