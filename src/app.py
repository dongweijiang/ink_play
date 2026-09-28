"""pygame 初始化、逻辑画布、主循环与状态装配。"""

from __future__ import annotations

import logging
from pathlib import Path

import pygame

from src.constants import (
    FPS,
    LOGICAL_SIZE,
    LOG_ROOT,
    SAVE_ROOT,
    SHADOW,
    WINDOW_TITLE,
)
from src.resources import ResourceManager
from src.settings_model import AppSettings, load_settings, save_settings
from src.state_machine import StateID, StateMachine
from src.states.boot_state import BootState
from src.states.main_menu import MainMenuState
from src.states.map_state import MapPlaceholderState
from src.states.pause_state import PauseState
from src.states.settings import SettingsState
from src.states.shared import StateServices
from src.ui.layout import Viewport, calculate_viewport, window_to_logical

LOGGER = logging.getLogger(__name__)


def configure_logging(log_root: Path = LOG_ROOT) -> None:
    """配置控制台与轮次开发日志，不记录任何密钥。"""
    log_root.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_root / "inkbound_spire.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )


class GameApp:
    """拥有窗口和状态机的桌面应用。"""

    def __init__(self, settings_path: Path | None = None) -> None:
        configure_logging()
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.settings_path = settings_path or SAVE_ROOT / "settings.json"
        self.settings: AppSettings = load_settings(self.settings_path)
        self.running = True
        self._screen = pygame.Surface((1, 1))
        self._logical_surface = pygame.Surface(LOGICAL_SIZE)
        self._viewport = Viewport(0, 0, LOGICAL_SIZE[0], LOGICAL_SIZE[1], 1.0)
        self._clock = pygame.time.Clock()
        self.resources = ResourceManager()
        self.machine = StateMachine()
        self._apply_display()
        self._register_states()
        self.machine.start(StateID.BOOT)
        LOGGER.info("应用已启动，逻辑画布 %sx%s", *LOGICAL_SIZE)

    def run(self, *, max_frames: int | None = None) -> int:
        """运行主循环；`max_frames` 仅供自动冒烟验证。"""
        frames = 0
        try:
            while self.running and (max_frames is None or frames < max_frames):
                dt = min(self._clock.tick(FPS) / 1000.0, 0.1)
                for event in pygame.event.get():
                    if self._handle_global_event(event):
                        continue
                    mapped_event = self._map_pointer_event(event)
                    self.machine.current.handle_event(mapped_event)
                    if self.machine.has_pending_change:
                        break
                if not self.running:
                    break
                self.machine.current.update(dt)
                self.machine.commit()
                self.machine.current.draw(self._logical_surface)
                self._present()
                frames += 1
            return 0
        except Exception:
            LOGGER.exception("主循环发生未处理错误")
            return 1
        finally:
            pygame.quit()

    def stop(self) -> None:
        """请求在本帧安全退出。"""
        self.running = False

    def _register_states(self) -> None:
        services = StateServices(
            resources=self.resources,
            settings=self.settings,
            quit_game=self.stop,
            apply_display=self._apply_display,
            persist_settings=self._persist_settings,
        )
        self.machine.register(StateID.BOOT, BootState(self.machine, services))
        self.machine.register(StateID.MAIN_MENU, MainMenuState(self.machine, services))
        self.machine.register(StateID.SETTINGS, SettingsState(self.machine, services))
        self.machine.register(StateID.RUN_MAP, MapPlaceholderState(self.machine, services))
        self.machine.register(StateID.PAUSED, PauseState(self.machine, services))

    def _handle_global_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.QUIT:
            self.stop()
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            self.settings.fullscreen = not self.settings.fullscreen
            self._apply_display()
            self._persist_settings()
            return True
        if event.type in {pygame.WINDOWSIZECHANGED, pygame.WINDOWRESIZED}:
            self._update_viewport()
            return True
        return False

    def _map_pointer_event(self, event: pygame.event.Event) -> pygame.event.Event:
        if event.type not in {pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP}:
            return event
        logical_position = window_to_logical(event.pos, self._viewport)
        attributes = dict(event.dict)
        attributes["pos"] = logical_position or (-10_000, -10_000)
        return pygame.event.Event(event.type, attributes)

    def _apply_display(self) -> None:
        flags = pygame.FULLSCREEN if self.settings.fullscreen else pygame.RESIZABLE
        self._screen = pygame.display.set_mode(self.settings.resolution, flags)
        self._update_viewport()

    def _update_viewport(self) -> None:
        self._viewport = calculate_viewport(self._screen.get_size(), LOGICAL_SIZE)

    def _present(self) -> None:
        self._screen.fill(SHADOW)
        if (self._viewport.width, self._viewport.height) == LOGICAL_SIZE:
            frame = self._logical_surface
        else:
            frame = pygame.transform.smoothscale(
                self._logical_surface, (self._viewport.width, self._viewport.height)
            )
        self._screen.blit(frame, (self._viewport.x, self._viewport.y))
        pygame.display.flip()

    def _persist_settings(self) -> None:
        try:
            save_settings(self.settings_path, self.settings)
        except OSError as exc:
            LOGGER.error("设置无法保存，当前会话仍可继续：%s", exc)
