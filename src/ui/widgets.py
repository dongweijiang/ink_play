"""第 1 轮所需的基础按钮与文字绘制。"""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from src.constants import CYAN_GLOW, DISABLED, GOLD, INK, INK_SOFT, PAPER, VERMILION
from src.resources import ResourceManager


@dataclass(slots=True)
class Button:
    """支持鼠标和焦点导航的按钮。"""

    rect: pygame.Rect
    label: str
    enabled: bool = True
    focused: bool = False

    def contains(self, position: tuple[int, int]) -> bool:
        return self.enabled and self.rect.collidepoint(position)

    def draw(
        self,
        surface: pygame.Surface,
        resources: ResourceManager,
        mouse_position: tuple[int, int] | None,
    ) -> None:
        hovered = mouse_position is not None and self.contains(mouse_position)
        fill = PAPER if self.enabled else (68, 69, 70)
        border = CYAN_GLOW if (self.focused or hovered) else INK_SOFT
        text_color = INK if self.enabled else DISABLED
        pygame.draw.rect(surface, (10, 12, 16), self.rect.move(5, 6), border_radius=8)
        pygame.draw.rect(surface, fill, self.rect, border_radius=8)
        pygame.draw.rect(surface, border, self.rect, 3, border_radius=8)
        if self.focused:
            pygame.draw.rect(surface, GOLD, self.rect.inflate(8, 8), 2, border_radius=11)
        font = resources.font(28)
        text = font.render(self.label, True, text_color)
        surface.blit(text, text.get_rect(center=self.rect.center))


def draw_title(
    surface: pygame.Surface,
    resources: ResourceManager,
    title: str,
    subtitle: str,
) -> None:
    """绘制统一标题区。"""
    title_image = resources.font(66).render(title, True, PAPER)
    surface.blit(title_image, title_image.get_rect(center=(640, 95)))
    subtitle_image = resources.font(24).render(subtitle, True, CYAN_GLOW)
    surface.blit(subtitle_image, subtitle_image.get_rect(center=(640, 148)))
    pygame.draw.line(surface, VERMILION, (430, 175), (850, 175), 3)


def draw_footer(surface: pygame.Surface, resources: ResourceManager, text: str) -> None:
    """绘制操作提示。"""
    image = resources.font(20).render(text, True, (175, 178, 181))
    surface.blit(image, image.get_rect(center=(640, 690)))
