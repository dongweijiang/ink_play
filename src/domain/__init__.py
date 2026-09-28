"""不依赖 pygame 的游戏规则数据模型。"""

from src.domain.actor import EnemyDefinition, EnemyIntent, EnemyState, PlayerState
from src.domain.card import CardDefinition, CardInstance, CardType, TargetType
from src.domain.combat import CombatOutcome, CombatPhase, CombatState, PlayResult
from src.domain.effects import Effect, EffectType

__all__ = [
    "CardDefinition",
    "CardInstance",
    "CardType",
    "CombatOutcome",
    "CombatPhase",
    "CombatState",
    "Effect",
    "EffectType",
    "EnemyDefinition",
    "EnemyIntent",
    "EnemyState",
    "PlayResult",
    "PlayerState",
    "TargetType",
]
