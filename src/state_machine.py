"""显式、延迟提交的界面状态机。"""

from __future__ import annotations

from enum import Enum, auto
from typing import Protocol

import pygame


class StateID(Enum):
    """完整产品使用的稳定状态标识。"""

    BOOT = auto()
    MAIN_MENU = auto()
    SETTINGS = auto()
    RUN_MAP = auto()
    COMBAT = auto()
    CARD_REWARD = auto()
    DRAWING = auto()
    DRAWING_RESULT = auto()
    EVENT = auto()
    SHOP = auto()
    REST = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()


class GameState(Protocol):
    """所有界面状态必须满足的生命周期协议。"""

    def enter(self) -> None: ...

    def handle_event(self, event: pygame.event.Event) -> None: ...

    def update(self, dt: float) -> None: ...

    def draw(self, surface: pygame.Surface) -> None: ...

    def exit(self) -> None: ...


class BaseState:
    """提供空生命周期钩子的状态基类。"""

    def enter(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        del event

    def update(self, dt: float) -> None:
        del dt

    def draw(self, surface: pygame.Surface) -> None:
        del surface

    def exit(self) -> None:
        pass


class StateMachine:
    """在帧末统一提交切换，避免旧状态继续处理同一事件。"""

    def __init__(self) -> None:
        self._states: dict[StateID, GameState] = {}
        self._current_id: StateID | None = None
        self._pending_id: StateID | None = None
        self._remember_current = False
        self._resume_id: StateID | None = None

    @property
    def current_id(self) -> StateID | None:
        return self._current_id

    @property
    def has_pending_change(self) -> bool:
        """当前帧是否已有待提交切换。"""
        return self._pending_id is not None

    @property
    def current(self) -> GameState:
        if self._current_id is None:
            raise RuntimeError("状态机尚未启动")
        return self._states[self._current_id]

    def register(self, state_id: StateID, state: GameState) -> None:
        """注册一个状态实例，重复 ID 会被拒绝。"""
        if state_id in self._states:
            raise ValueError(f"状态已注册：{state_id.name}")
        self._states[state_id] = state

    def start(self, state_id: StateID) -> None:
        """立即进入首个状态。"""
        self._ensure_registered(state_id)
        if self._current_id is not None:
            raise RuntimeError("状态机已启动")
        self._current_id = state_id
        self.current.enter()

    def request(self, state_id: StateID, *, remember_current: bool = False) -> None:
        """请求在当前帧结束后切换状态。"""
        self._ensure_registered(state_id)
        self._pending_id = state_id
        self._remember_current = remember_current

    def request_resume(self) -> None:
        """请求返回进入暂停前的状态。"""
        if self._resume_id is None:
            raise RuntimeError("没有可恢复的状态")
        self._pending_id = self._resume_id
        self._remember_current = False

    def commit(self) -> bool:
        """提交待处理切换；有切换时返回 True。"""
        if self._pending_id is None:
            return False
        next_id = self._pending_id
        if self._remember_current and self._current_id is not None:
            self._resume_id = self._current_id
        self._pending_id = None
        self._remember_current = False
        if next_id == self._current_id:
            return False
        if self._current_id is not None:
            self.current.exit()
        self._current_id = next_id
        self.current.enter()
        return True

    def clear_resume(self) -> None:
        """离开局内流程时清除暂停返回点。"""
        self._resume_id = None

    def _ensure_registered(self, state_id: StateID) -> None:
        if state_id not in self._states:
            raise KeyError(f"状态未注册：{state_id.name}")
