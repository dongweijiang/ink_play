"""战斗效果的最小数据表示。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EffectType(str, Enum):
    """第 2 轮支持的基础效果原语。"""

    DAMAGE = "damage"
    BLOCK = "block"
    DRAW = "draw"
    GAIN_ENERGY = "gain_energy"
    LOSE_HEALTH = "lose_health"


@dataclass(frozen=True, slots=True)
class Effect:
    """按卡牌或意图中的排列顺序结算一个效果。"""

    type: EffectType
    amount: int
    hits: int = 1
    primary: bool = False

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("效果数值不能为负数")
        if self.hits < 1:
            raise ValueError("效果段数至少为 1")
        if self.type is not EffectType.DAMAGE and self.hits != 1:
            raise ValueError("只有伤害效果可以包含多段")
