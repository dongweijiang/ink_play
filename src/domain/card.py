"""卡牌定义与战斗内卡牌实例。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.domain.effects import Effect


class CardType(str, Enum):
    ATTACK = "attack"
    SKILL = "skill"


class TargetType(str, Enum):
    SINGLE_ENEMY = "single_enemy"
    ALL_ENEMIES = "all_enemies"
    SELF = "self"
    NONE = "none"


@dataclass(frozen=True, slots=True)
class CardDefinition:
    """不会在战斗中变化的卡牌模板。"""

    id: str
    name: str
    type: CardType
    cost: int
    target: TargetType
    effects: tuple[Effect, ...]
    exhaust: bool = False
    retain: bool = False

    def __post_init__(self) -> None:
        if not self.id or not self.name:
            raise ValueError("卡牌 ID 和名称不能为空")
        if self.cost < 0:
            raise ValueError("卡牌费用不能为负数")
        if not self.effects:
            raise ValueError("卡牌至少需要一个效果")
        if sum(effect.primary for effect in self.effects) != 1:
            raise ValueError("卡牌必须且只能有一个主要效果")


@dataclass(slots=True)
class CardInstance:
    """牌堆中的独立卡牌，可携带本场费用修正。"""

    instance_id: str
    definition: CardDefinition
    cost_modifier: int = 0

    @property
    def cost(self) -> int:
        """返回最低为零的当前费用。"""
        return max(0, self.definition.cost + self.cost_modifier)
