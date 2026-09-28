"""抽牌、弃牌、洗牌、保留与消散区域。"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from src.domain.card import CardDefinition, CardInstance


@dataclass(frozen=True, slots=True)
class DrawReport:
    """一次抽牌操作的可测试结果。"""

    drawn_ids: tuple[str, ...]
    overflow_count: int
    reshuffles: int


@dataclass(slots=True)
class BattleDeck:
    """一场战斗内的四个卡牌区域。"""

    draw_pile: list[CardInstance] = field(default_factory=list)
    discard_pile: list[CardInstance] = field(default_factory=list)
    hand: list[CardInstance] = field(default_factory=list)
    exhaust_pile: list[CardInstance] = field(default_factory=list)

    @classmethod
    def build(
        cls,
        deck_ids: list[str],
        catalog: dict[str, CardDefinition],
        rng: random.Random,
    ) -> BattleDeck:
        """由永久牌组 ID 创建唯一实例并完成初始洗牌。"""
        cards: list[CardInstance] = []
        for index, card_id in enumerate(deck_ids):
            if card_id not in catalog:
                raise KeyError(f"牌组引用未知卡牌：{card_id}")
            cards.append(CardInstance(f"{card_id}:{index}", catalog[card_id]))
        rng.shuffle(cards)
        return cls(draw_pile=cards)

    def draw(self, count: int, rng: random.Random, hand_limit: int = 10) -> DrawReport:
        """抽指定数量；牌堆空时洗入弃牌，手牌溢出则进入弃牌。"""
        if count < 0 or hand_limit < 1:
            raise ValueError("抽牌数不能为负，手牌上限至少为 1")
        drawn: list[str] = []
        overflow = 0
        reshuffles = 0
        for _ in range(count):
            if not self.draw_pile:
                if not self.discard_pile:
                    break
                self.draw_pile = self.discard_pile
                self.discard_pile = []
                rng.shuffle(self.draw_pile)
                reshuffles += 1
            card = self.draw_pile.pop()
            if len(self.hand) >= hand_limit:
                self.discard_pile.append(card)
                overflow += 1
            else:
                self.hand.append(card)
                drawn.append(card.instance_id)
        return DrawReport(tuple(drawn), overflow, reshuffles)

    def find_in_hand(self, instance_id: str) -> CardInstance | None:
        """按实例 ID 查找手牌。"""
        return next((card for card in self.hand if card.instance_id == instance_id), None)

    def remove_from_hand(self, instance_id: str) -> CardInstance:
        """从手牌移除并返回指定实例。"""
        for index, card in enumerate(self.hand):
            if card.instance_id == instance_id:
                return self.hand.pop(index)
        raise KeyError(f"手牌中不存在卡牌：{instance_id}")

    def discard_unretained_hand(self) -> None:
        """回合结束时保留带保留关键词的卡，弃置其余卡。"""
        retained: list[CardInstance] = []
        for card in self.hand:
            if card.definition.retain:
                retained.append(card)
            else:
                self.discard_pile.append(card)
        self.hand = retained
