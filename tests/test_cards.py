"""卡牌、效果和角色基础模型测试。"""

from __future__ import annotations

import pytest

from src.domain.actor import PlayerState
from src.domain.card import CardDefinition, CardInstance, CardType, TargetType
from src.domain.effects import Effect, EffectType


def damage(amount: int, *, primary: bool = True) -> Effect:
    return Effect(EffectType.DAMAGE, amount, primary=primary)


def test_card_requires_exactly_one_primary_effect() -> None:
    with pytest.raises(ValueError, match="主要效果"):
        CardDefinition(
            "invalid",
            "无主效果",
            CardType.ATTACK,
            1,
            TargetType.SINGLE_ENEMY,
            (damage(3, primary=False),),
        )


def test_card_cost_never_falls_below_zero() -> None:
    definition = CardDefinition(
        "free", "减费测试", CardType.SKILL, 1, TargetType.SELF, (Effect(EffectType.BLOCK, 1, primary=True),)
    )
    card = CardInstance("free:0", definition, cost_modifier=-5)
    assert card.cost == 0


def test_damage_uses_block_before_health() -> None:
    actor = PlayerState("测试者", 20, 20, block=6)
    result = actor.take_damage(9)
    assert result.blocked == 6
    assert result.health_lost == 3
    assert actor.block == 0
    assert actor.current_hp == 17


def test_health_loss_ignores_block() -> None:
    actor = PlayerState("测试者", 20, 20, block=99)
    actor.lose_health(4)
    assert actor.current_hp == 16
    assert actor.block == 99


def test_multihit_is_only_valid_for_damage() -> None:
    with pytest.raises(ValueError, match="多段"):
        Effect(EffectType.BLOCK, 4, hits=2)
