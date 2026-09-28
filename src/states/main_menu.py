"""主菜单状态。"""

from __future__ import annotations

import pygame

from src.constants import INK, INK_SOFT, PAPER_DARK
from src.state_machine import StateID, StateMachine
from src.states.menu_base import MenuState
from src.states.shared import StateServices
from src.ui.widgets import Button, draw_footer, draw_title


class MainMenuState(MenuState):
    """新旅程、设置和退出入口；继续游戏在第 5 轮前禁用。"""

    def __init__(self, machine: StateMachine, services: StateServices) -> None:
        super().__init__()
        self.machine = machine
        self.services = services
        self.notice = ""
        labels = ["继续游戏（暂无存档）", "新旅程", "设置", "图鉴", "制作人员", "退出游戏"]
        self.buttons = [
            Button(pygame.Rect(470, 205 + index * 70, 340, 52), label, enabled=index != 0)
            for index, label in enumerate(labels)
        ]
        self.actions = [
            lambda: None,
            lambda: self.machine.request(StateID.RUN_MAP),
            lambda: self.machine.request(StateID.SETTINGS),
            lambda: self._show_notice("图鉴将在内容数据完成后开放。"),
            lambda: self._show_notice("学生团队名单可在最终交付前填写。"),
            self.services.quit_game,
        ]

    def enter(self) -> None:
        super().enter()
        self.notice = ""
        self.machine.clear_resume()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.services.quit_game()
            return
        super().handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(INK)
        for x in range(0, 1280, 80):
            pygame.draw.line(surface, INK_SOFT, (x, 0), (x - 220, 720), 1)
        draw_title(surface, self.services.resources, "墨痕登塔", "INKBOUND SPIRE · 工程骨架")
        for button in self.buttons:
            button.draw(surface, self.services.resources, self.mouse_position)
        if self.notice:
            notice = self.services.resources.font(21).render(self.notice, True, PAPER_DARK)
            surface.blit(notice, notice.get_rect(center=(640, 640)))
        draw_footer(surface, self.services.resources, "方向键/鼠标选择 · Enter 确认 · F11 全屏")

    def _show_notice(self, message: str) -> None:
        self.notice = message
