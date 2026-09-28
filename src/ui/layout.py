"""逻辑画布与实际窗口之间的坐标变换。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Viewport:
    """保持宽高比的 letterbox 视口。"""

    x: int
    y: int
    width: int
    height: int
    scale: float


def calculate_viewport(
    window_size: tuple[int, int], logical_size: tuple[int, int]
) -> Viewport:
    """计算逻辑画布在窗口中的最大等比矩形。"""
    window_width, window_height = window_size
    logical_width, logical_height = logical_size
    if min(window_width, window_height, logical_width, logical_height) <= 0:
        raise ValueError("窗口和逻辑画布尺寸必须为正数")
    scale = min(window_width / logical_width, window_height / logical_height)
    width = max(1, round(logical_width * scale))
    height = max(1, round(logical_height * scale))
    return Viewport(
        x=(window_width - width) // 2,
        y=(window_height - height) // 2,
        width=width,
        height=height,
        scale=scale,
    )


def window_to_logical(
    position: tuple[int, int], viewport: Viewport
) -> tuple[int, int] | None:
    """将鼠标坐标映射到逻辑画布；黑边区域返回 None。"""
    x, y = position
    if not (viewport.x <= x < viewport.x + viewport.width):
        return None
    if not (viewport.y <= y < viewport.y + viewport.height):
        return None
    return (
        int((x - viewport.x) / viewport.scale),
        int((y - viewport.y) / viewport.scale),
    )
