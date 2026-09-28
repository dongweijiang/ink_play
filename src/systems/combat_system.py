"""不依赖 pygame 的回合制战斗规则。"""

from __future__ import annotations

import random
from collections.abc import Iterable

from src.domain.actor import ActorState, EnemyDefinition, EnemyState, PlayerState
from src.domain.card import CardDefinition, CardInstance, TargetType
from src.domain.combat import CombatOutcome, CombatPhase, CombatState, PlayResult
from src.domain.deck import BattleDeck
from src.domain.effects import Effect, EffectType


class CombatSystem:
    """验证玩家命令并按固定顺序修改战斗状态。"""

    def __init__(self, state: CombatState, rng: random.Random) -> None:
        self.state = state
        self._rng = rng

    @classmethod
    def create(
        cls,
        *,
        card_definitions: Iterable[CardDefinition],
        deck_ids: list[str],
        enemy_definitions: Iterable[EnemyDefinition],
        seed: int,
        player_hp: int = 72,
        base_energy: int = 3,
        cards_per_turn: int = 5,
        hand_limit: int = 10,
    ) -> CombatSystem:
        """创建并立即开始一场可复现的战斗。"""
        definitions = tuple(card_definitions)
        catalog = {card.id: card for card in definitions}
        if len(catalog) == 0:
            raise ValueError("至少需要一个卡牌定义")
        if len(catalog) != len(definitions):
            raise ValueError("卡牌 ID 不能重复")
        enemies = [EnemyState.from_definition(definition) for definition in enemy_definitions]
        if not enemies:
            raise ValueError("至少需要一个敌人")
        rng = random.Random(seed)
        deck = BattleDeck.build(deck_ids, catalog, rng)
        state = CombatState(
            player=PlayerState("砚行者", player_hp, player_hp),
            enemies=enemies,
            deck=deck,
            seed=seed,
            base_energy=base_energy,
            cards_per_turn=cards_per_turn,
            hand_limit=hand_limit,
        )
        system = cls(state, rng)
        system._start_player_turn()
        return system

    def play_card(self, instance_id: str, target_index: int | None = None) -> PlayResult:
        """尝试打出手牌；非法操作不消耗卡牌、能量或计数。"""
        if self.state.outcome is not CombatOutcome.ONGOING or not self.state.player.is_alive:
            return PlayResult(False, "战斗已经结束")
        if self.state.phase is not CombatPhase.PLAYER:
            return PlayResult(False, "当前不是玩家回合")
        card = self.state.deck.find_in_hand(instance_id)
        if card is None:
            return PlayResult(False, "手牌中没有这张牌")
        targets = self._resolve_card_targets(card, target_index)
        if targets is None:
            return PlayResult(False, "目标无效")
        if self.state.player.energy < card.cost:
            return PlayResult(False, "能量不足")

        self.state.player.energy -= card.cost
        card = self.state.deck.remove_from_hand(instance_id)
        self.state.cards_played_this_turn += 1
        for effect in card.definition.effects:
            self._resolve_player_effect(effect, targets)
            self._update_outcome()
            if self.state.outcome is not CombatOutcome.ONGOING:
                break

        if card.definition.exhaust:
            self.state.deck.exhaust_pile.append(card)
        else:
            self.state.deck.discard_pile.append(card)
        return PlayResult(True, "已打出")

    def end_player_turn(self) -> PlayResult:
        """弃置手牌并依次执行所有存活敌人的公开意图。"""
        if self.state.outcome is not CombatOutcome.ONGOING:
            return PlayResult(False, "战斗已经结束")
        if self.state.phase is not CombatPhase.PLAYER:
            return PlayResult(False, "当前不是玩家回合")

        self.state.deck.discard_unretained_hand()
        self.state.phase = CombatPhase.ENEMY
        for enemy in self.state.enemies:
            if not enemy.is_alive:
                continue
            enemy.block = 0
            intent = enemy.current_intent
            for effect in intent.effects:
                self._resolve_enemy_effect(enemy, effect)
                self._update_outcome()
                if self.state.outcome is not CombatOutcome.ONGOING:
                    message = (
                        "敌人行动后玩家倒下"
                        if self.state.outcome is CombatOutcome.DEFEAT
                        else "敌人行动后战斗胜利"
                    )
                    return PlayResult(True, message)
            enemy.advance_intent()

        self._update_outcome()
        if self.state.outcome is CombatOutcome.ONGOING:
            self._start_player_turn()
        return PlayResult(True, "回合结束")

    def _start_player_turn(self) -> None:
        self.state.turn += 1
        if self.state.turn > 1:
            self.state.player.block = 0
        self.state.player.energy = max(0, self.state.base_energy)
        self.state.cards_played_this_turn = 0
        self.state.phase = CombatPhase.PLAYER
        self.state.deck.draw(
            self.state.cards_per_turn,
            self._rng,
            self.state.hand_limit,
        )

    def _resolve_card_targets(
        self, card: CardInstance, target_index: int | None
    ) -> list[ActorState] | None:
        target_type = card.definition.target
        if target_type is TargetType.SINGLE_ENEMY:
            if target_index is None or not 0 <= target_index < len(self.state.enemies):
                return None
            enemy = self.state.enemies[target_index]
            return [enemy] if enemy.is_alive else None
        if target_type is TargetType.ALL_ENEMIES:
            return [enemy for enemy in self.state.enemies if enemy.is_alive]
        if target_type is TargetType.SELF:
            return [self.state.player]
        return []

    def _resolve_player_effect(self, effect: Effect, targets: list[ActorState]) -> None:
        if effect.type is EffectType.DAMAGE:
            for target in targets:
                self._deal_damage(target, effect.amount, effect.hits)
        elif effect.type is EffectType.BLOCK:
            self.state.player.gain_block(effect.amount)
        elif effect.type is EffectType.DRAW:
            self.state.deck.draw(effect.amount, self._rng, self.state.hand_limit)
        elif effect.type is EffectType.GAIN_ENERGY:
            self.state.player.energy += effect.amount
        elif effect.type is EffectType.LOSE_HEALTH:
            self.state.player.lose_health(effect.amount)
        else:
            raise ValueError(f"不支持的玩家效果：{effect.type}")

    def _resolve_enemy_effect(self, enemy: EnemyState, effect: Effect) -> None:
        if effect.type is EffectType.DAMAGE:
            self._deal_damage(self.state.player, effect.amount, effect.hits)
        elif effect.type is EffectType.BLOCK:
            enemy.gain_block(effect.amount)
        elif effect.type is EffectType.LOSE_HEALTH:
            enemy.lose_health(effect.amount)
        else:
            raise ValueError(f"敌人意图不支持效果：{effect.type}")

    @staticmethod
    def _deal_damage(target: ActorState, amount: int, hits: int) -> None:
        for _ in range(hits):
            if not target.is_alive:
                break
            target.take_damage(amount)

    def _update_outcome(self) -> None:
        if not self.state.player.is_alive:
            self.state.outcome = CombatOutcome.DEFEAT
            self.state.phase = CombatPhase.FINISHED
        elif not any(enemy.is_alive for enemy in self.state.enemies):
            self.state.outcome = CombatOutcome.VICTORY
            self.state.phase = CombatPhase.FINISHED
