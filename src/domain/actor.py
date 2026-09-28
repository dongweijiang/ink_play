"""玩家、敌人与公开行动意图。"""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.effects import Effect


@dataclass(frozen=True, slots=True)
class DamageResult:
    """一次伤害结算中被格挡和实际损失的生命。"""

    blocked: int
    health_lost: int


@dataclass(slots=True)
class ActorState:
    """玩家和敌人共享的生命与格挡行为。"""

    name: str
    max_hp: int
    current_hp: int
    block: int = 0

    def __post_init__(self) -> None:
        if self.max_hp < 1:
            raise ValueError("最大生命至少为 1")
        self.current_hp = max(0, min(self.current_hp, self.max_hp))
        self.block = max(0, self.block)

    @property
    def is_alive(self) -> bool:
        return self.current_hp > 0

    def gain_block(self, amount: int) -> None:
        """获得非负格挡。"""
        if amount < 0:
            raise ValueError("格挡增量不能为负数")
        self.block += amount

    def take_damage(self, amount: int) -> DamageResult:
        """先消耗格挡，再扣除生命。"""
        if amount < 0:
            raise ValueError("伤害不能为负数")
        blocked = min(self.block, amount)
        self.block -= blocked
        health_lost = min(self.current_hp, amount - blocked)
        self.current_hp -= health_lost
        return DamageResult(blocked, health_lost)

    def lose_health(self, amount: int) -> int:
        """无视格挡损失生命，并返回实际损失量。"""
        if amount < 0:
            raise ValueError("生命损失不能为负数")
        lost = min(self.current_hp, amount)
        self.current_hp -= lost
        return lost


@dataclass(slots=True)
class PlayerState(ActorState):
    """玩家的战斗资源。"""

    energy: int = 0


@dataclass(frozen=True, slots=True)
class EnemyIntent:
    """敌人下一次行动的公开名称与顺序效果。"""

    id: str
    name: str
    effects: tuple[Effect, ...]

    def __post_init__(self) -> None:
        if not self.id or not self.name or not self.effects:
            raise ValueError("敌人意图必须包含 ID、名称和效果")


@dataclass(frozen=True, slots=True)
class EnemyDefinition:
    """敌人模板及其循环意图。"""

    id: str
    name: str
    max_hp: int
    intent_cycle: tuple[EnemyIntent, ...]

    def __post_init__(self) -> None:
        if not self.id or not self.name:
            raise ValueError("敌人 ID 和名称不能为空")
        if self.max_hp < 1:
            raise ValueError("敌人最大生命至少为 1")
        if not self.intent_cycle:
            raise ValueError("敌人至少需要一个行动意图")


@dataclass(slots=True, kw_only=True)
class EnemyState(ActorState):
    """战斗中的敌人实例。"""

    definition: EnemyDefinition
    intent_index: int = 0

    @classmethod
    def from_definition(cls, definition: EnemyDefinition) -> EnemyState:
        return cls(
            name=definition.name,
            max_hp=definition.max_hp,
            current_hp=definition.max_hp,
            definition=definition,
        )

    @property
    def current_intent(self) -> EnemyIntent:
        """返回当前已公开意图。"""
        return self.definition.intent_cycle[self.intent_index]

    def advance_intent(self) -> None:
        """循环到下一意图。"""
        self.intent_index = (self.intent_index + 1) % len(self.definition.intent_cycle)
