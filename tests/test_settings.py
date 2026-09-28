"""应用设置容错与持久化测试。"""

from __future__ import annotations

import json

from src.settings_model import AppSettings, load_settings, save_settings


def test_missing_settings_returns_defaults(tmp_path) -> None:
    assert load_settings(tmp_path / "missing.json") == AppSettings()


def test_settings_round_trip(tmp_path) -> None:
    path = tmp_path / "settings.json"
    original = AppSettings(30, 40, True, (1600, 900), "gamepad", "offline")

    save_settings(path, original)

    assert load_settings(path) == original
    assert not path.with_suffix(".json.tmp").exists()


def test_corrupt_settings_returns_defaults(tmp_path) -> None:
    path = tmp_path / "settings.json"
    path.write_text("{broken", encoding="utf-8")
    assert load_settings(path) == AppSettings()


def test_invalid_values_are_normalized(tmp_path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps(
            {
                "music_volume": 999,
                "sfx_volume": -3,
                "fullscreen": 1,
                "resolution": [111, 222],
                "input_mode": "unknown",
                "ai_mode": "online",
            }
        ),
        encoding="utf-8",
    )

    loaded = load_settings(path)

    assert loaded.music_volume == 100
    assert loaded.sfx_volume == 0
    assert loaded.resolution == (1280, 720)
    assert loaded.input_mode == "auto"
    assert loaded.ai_mode == "offline"


def test_serialized_settings_do_not_contain_api_key() -> None:
    serialized = json.dumps(AppSettings().to_dict())
    assert "key" not in serialized.lower()
