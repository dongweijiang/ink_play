"""集中管理字体、图片与缺失资源占位。"""

from __future__ import annotations

import logging
from pathlib import Path

import pygame

from src.constants import ASSET_ROOT, INK, PAPER, VERMILION

LOGGER = logging.getLogger(__name__)


class ResourceManager:
    """缓存已加载资源，并为缺失文件提供可见占位。"""

    def __init__(self, asset_root: Path = ASSET_ROOT) -> None:
        self.asset_root = asset_root
        self._fonts: dict[int, pygame.font.Font] = {}
        self._images: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}

    def font(self, size: int) -> pygame.font.Font:
        """返回可显示中文的字体；无随附字体时尝试系统字体。"""
        if size not in self._fonts:
            bundled = next(self.asset_root.joinpath("fonts").glob("*.ttf"), None)
            if bundled is not None:
                self._fonts[size] = pygame.font.Font(str(bundled), size)
            else:
                match = pygame.font.match_font(
                    ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial Unicode MS"]
                )
                self._fonts[size] = pygame.font.Font(match, size)
        return self._fonts[size]

    def image(self, relative_path: str, size: tuple[int, int]) -> pygame.Surface:
        """载入并缩放图片；失败时返回带叉号的占位图。"""
        key = (relative_path, size)
        if key in self._images:
            return self._images[key]
        path = self.asset_root / relative_path
        try:
            loaded = pygame.image.load(path).convert_alpha()
            image = pygame.transform.smoothscale(loaded, size)
        except (FileNotFoundError, pygame.error, OSError) as exc:
            LOGGER.warning("资源不可用，使用占位图：%s (%s)", path, exc)
            image = self.placeholder(size, path.stem or "missing")
        self._images[key] = image
        return image

    def placeholder(self, size: tuple[int, int], label: str) -> pygame.Surface:
        """生成水墨风格的明确缺失资源占位。"""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(PAPER)
        pygame.draw.rect(surface, INK, surface.get_rect(), 3)
        pygame.draw.line(surface, VERMILION, (8, 8), (size[0] - 8, size[1] - 8), 4)
        pygame.draw.line(surface, VERMILION, (size[0] - 8, 8), (8, size[1] - 8), 4)
        font = self.font(max(14, min(24, size[1] // 6)))
        text = font.render(label[:16], True, INK)
        surface.blit(text, text.get_rect(center=surface.get_rect().center))
        return surface
