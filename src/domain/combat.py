"""完整战斗快照及操作结果。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.domain.actor import EnemyIntent, EnemyState, PlayerState
from src.domain.deck import BattleDeck


class CombatPhase(str, Enum):
    PLAYER = "player"
    ENEMY = "enemy"
    FINISHED = "finished"


class CombatOutcome(str, Enum):
    ONGOING = "ongoing"
    VICTORY = "victory"
    DEFEAT = "defeat"


@dataclass(frozen=True, slots=True)
class PlayResult:
    """出牌请求的结果，失败不会改变战斗状态。"""

    success: bool
    message: str


@dataclass(slots=True)
class CombatState:
    """UI 可只读展示的单一战斗状态。"""

    player: PlayerState
    enemies: list[EnemyState]
    deck: BattleDeck
    seed: int
    base_energy: int = 3
    cards_per_turn: int = 5
    hand_limit: int = 10
    turn: int = 0
    cards_played_this_turn: int = 0
    phase: CombatPhase = CombatPhase.PLAYER
    outcome: CombatOutcome = CombatOutcome.ONGOING

    @property
    def visible_intents(self) -> tuple[EnemyIntent | None, ...]:
        """按敌人位置返回存活敌人的公开意图。"""
        return tuple(enemy.current_intent if enemy.is_alive else None for enemy in self.enemies)
