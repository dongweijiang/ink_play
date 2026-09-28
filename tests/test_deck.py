"""战斗牌堆区域和固定随机种子测试。"""

from __future__ import annotations

import random

from src.domain.card import CardDefinition, CardType, TargetType
from src.domain.deck import BattleDeck
from src.domain.effects import Effect, EffectType


def make_catalog(count: int = 6) -> dict[str, CardDefinition]:
    return {
        f"card_{index}": CardDefinition(
            f"card_{index}",
            f"测试牌{index}",
            CardType.SKILL,
            1,
            TargetType.SELF,
            (Effect(EffectType.BLOCK, index + 1, primary=True),),
        )
        for index in range(count)
    }


def test_same_seed_produces_same_draw_order() -> None:
    catalog = make_catalog()
    ids = list(catalog)
    first_rng = random.Random(2048)
    second_rng = random.Random(2048)
    first = BattleDeck.build(ids, catalog, first_rng)
    second = BattleDeck.build(ids, catalog, second_rng)
    assert first.draw(6, first_rng).drawn_ids == second.draw(6, second_rng).drawn_ids


def test_empty_draw_pile_shuffles_discard_pile() -> None:
    catalog = make_catalog(3)
    rng = random.Random(7)
    deck = BattleDeck.build(list(catalog), catalog, rng)
    deck.draw(3, rng)
    deck.discard_pile = deck.hand
    deck.hand = []
    report = deck.draw(2, rng)
    assert len(report.drawn_ids) == 2
    assert report.reshuffles == 1


def test_hand_overflow_goes_to_discard() -> None:
    catalog = make_catalog(3)
    rng = random.Random(1)
    deck = BattleDeck.build(list(catalog), catalog, rng)
    report = deck.draw(3, rng, hand_limit=1)
    assert len(deck.hand) == 1
    assert len(deck.discard_pile) == 2
    assert report.overflow_count == 2
