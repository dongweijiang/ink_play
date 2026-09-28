"""逻辑画布缩放与输入坐标测试。"""

from __future__ import annotations

import pytest

from src.ui.layout import calculate_viewport, window_to_logical


def test_wide_window_adds_side_bars() -> None:
    viewport = calculate_viewport((1600, 720), (1280, 720))
    assert (viewport.x, viewport.y, viewport.width, viewport.height) == (160, 0, 1280, 720)
    assert window_to_logical((160, 0), viewport) == (0, 0)
    assert window_to_logical((159, 100), viewport) is None


def test_larger_window_maps_pointer_to_logical_canvas() -> None:
    viewport = calculate_viewport((2560, 1440), (1280, 720))
    assert window_to_logical((1280, 720), viewport) == (640, 360)


def test_invalid_dimensions_are_rejected() -> None:
    with pytest.raises(ValueError):
        calculate_viewport((0, 720), (1280, 720))
