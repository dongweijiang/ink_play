"""无界面战斗引擎的回合、出牌、意图和胜负测试。"""

from __future__ import annotations

from src.domain.actor import EnemyDefinition, EnemyIntent
from src.domain.card import CardDefinition, CardInstance, CardType, TargetType
from src.domain.combat import CombatOutcome, CombatPhase
from src.domain.effects import Effect, EffectType
from src.systems.combat_system import CombatSystem


def card(
    card_id: str,
    effect_type: EffectType,
    amount: int,
    *,
    cost: int = 1,
    target: TargetType = TargetType.SINGLE_ENEMY,
    exhaust: bool = False,
    retain: bool = False,
    hits: int = 1,
) -> CardDefinition:
    card_type = CardType.ATTACK if effect_type is EffectType.DAMAGE else CardType.SKILL
    return CardDefinition(
        card_id,
        card_id,
        card_type,
        cost,
        target,
        (Effect(effect_type, amount, hits=hits, primary=True),),
        exhaust=exhaust,
        retain=retain,
    )


def intent(intent_id: str, effect_type: EffectType, amount: int, *, hits: int = 1) -> EnemyIntent:
    return EnemyIntent(
        intent_id,
        intent_id,
        (Effect(effect_type, amount, hits=hits, primary=True),),
    )


def enemy(
    enemy_id: str = "dummy",
    hp: int = 30,
    intents: tuple[EnemyIntent, ...] | None = None,
) -> EnemyDefinition:
    return EnemyDefinition(
        enemy_id,
        enemy_id,
        hp,
        intents or (intent("hit", EffectType.DAMAGE, 6),),
    )


def create_system(
    cards: list[CardDefinition],
    deck_ids: list[str],
    enemies: list[EnemyDefinition] | None = None,
    *,
    player_hp: int = 30,
    energy: int = 3,
) -> CombatSystem:
    return CombatSystem.create(
        card_definitions=cards,
        deck_ids=deck_ids,
        enemy_definitions=enemies or [enemy()],
        seed=42,
        player_hp=player_hp,
        base_energy=energy,
        cards_per_turn=len(deck_ids),
    )


def hand_id(system: CombatSystem, definition_id: str) -> str:
    return next(
        item.instance_id
        for item in system.state.deck.hand
        if item.definition.id == definition_id
    )


def test_battle_starts_with_energy_hand_and_visible_intent() -> None:
    strike = card("strike", EffectType.DAMAGE, 6)
    system = create_system([strike], ["strike"])
    assert system.state.turn == 1
    assert system.state.player.energy == 3
    assert len(system.state.deck.hand) == 1
    assert system.state.visible_intents[0].id == "hit"


def test_insufficient_energy_does_not_move_card_or_count_play() -> None:
    costly = card("costly", EffectType.DAMAGE, 10, cost=4)
    system = create_system([costly], ["costly"], energy=3)
    instance_id = hand_id(system, "costly")
    result = system.play_card(instance_id, 0)
    assert not result.success
    assert system.state.player.energy == 3
    assert system.state.cards_played_this_turn == 0
    assert system.state.deck.find_in_hand(instance_id) is not None


def test_invalid_target_does_not_consume_resources() -> None:
    strike = card("strike", EffectType.DAMAGE, 6)
    system = create_system([strike], ["strike"])
    result = system.play_card(hand_id(system, "strike"), 99)
    assert not result.success
    assert system.state.player.energy == 3


def test_attack_damage_is_absorbed_by_enemy_block() -> None:
    strike = card("strike", EffectType.DAMAGE, 8)
    blocker = enemy(intents=(intent("guard", EffectType.BLOCK, 5),))
    system = create_system([strike], ["strike", "strike"], [blocker])
    system.end_player_turn()
    assert system.state.enemies[0].block == 5
    system.play_card(hand_id(system, "strike"), 0)
    assert system.state.enemies[0].block == 0
    assert system.state.enemies[0].current_hp == 27


def test_player_block_absorbs_multihit_enemy_attack() -> None:
    guard = card("guard", EffectType.BLOCK, 5, target=TargetType.SELF)
    attacker = enemy(intents=(intent("double", EffectType.DAMAGE, 4, hits=2),))
    system = create_system([guard], ["guard"], [attacker])
    system.play_card(hand_id(system, "guard"))
    system.end_player_turn()
    assert system.state.player.current_hp == 27


def test_enemy_intent_advances_after_action() -> None:
    wait = card("wait", EffectType.BLOCK, 0, cost=0, target=TargetType.SELF)
    foe = enemy(intents=(
        intent("first", EffectType.DAMAGE, 2),
        intent("second", EffectType.DAMAGE, 3),
    ))
    system = create_system([wait], ["wait", "wait"], [foe])
    system.end_player_turn()
    assert system.state.player.current_hp == 28
    assert system.state.visible_intents[0].id == "second"
    assert system.state.turn == 2


def test_dead_enemy_cannot_act() -> None:
    finisher = card("finish", EffectType.DAMAGE, 99)
    harmless = enemy("harmless", intents=(intent("guard", EffectType.BLOCK, 3),))
    system = create_system(
        [finisher],
        ["finish"],
        [enemy("danger", hp=10), harmless],
    )
    system.play_card(hand_id(system, "finish"), 0)
    system.end_player_turn()
    assert system.state.player.current_hp == 30
    assert system.state.enemies[0].intent_index == 0


def test_killing_last_enemy_ends_battle_and_blocks_more_cards() -> None:
    finisher = card("finish", EffectType.DAMAGE, 99, cost=0)
    system = create_system([finisher], ["finish", "finish"], [enemy(hp=10)])
    first, second = [item.instance_id for item in system.state.deck.hand]
    assert system.play_card(first, 0).success
    assert system.state.outcome is CombatOutcome.VICTORY
    assert system.state.phase is CombatPhase.FINISHED
    assert not system.play_card(second, 0).success


def test_player_death_stops_remaining_enemies_and_future_play() -> None:
    wait = card("wait", EffectType.BLOCK, 0, cost=0, target=TargetType.SELF)
    lethal = enemy("lethal", intents=(intent("lethal", EffectType.DAMAGE, 99),))
    later = enemy("later", intents=(intent("later_hit", EffectType.DAMAGE, 1),))
    system = create_system([wait], ["wait"], [lethal, later], player_hp=20)
    previous_hand_id = hand_id(system, "wait")
    system.end_player_turn()
    assert system.state.outcome is CombatOutcome.DEFEAT
    assert later.intent_cycle[0].id == "later_hit"
    assert system.state.enemies[1].intent_index == 0
    assert not system.play_card(previous_hand_id).success


def test_all_enemy_attack_hits_each_living_enemy() -> None:
    sweep = card(
        "sweep", EffectType.DAMAGE, 5, target=TargetType.ALL_ENEMIES
    )
    system = create_system([sweep], ["sweep"], [enemy("a"), enemy("b")])
    system.play_card(hand_id(system, "sweep"))
    assert [foe.current_hp for foe in system.state.enemies] == [25, 25]


def test_exhaust_and_retain_use_their_own_zones() -> None:
    vanish = card(
        "vanish", EffectType.BLOCK, 1, cost=0, target=TargetType.SELF, exhaust=True
    )
    keep = card(
        "keep", EffectType.BLOCK, 1, cost=0, target=TargetType.SELF, retain=True
    )
    system = create_system([vanish, keep], ["vanish", "keep"])
    system.play_card(hand_id(system, "vanish"))
    system.end_player_turn()
    assert [item.definition.id for item in system.state.deck.exhaust_pile] == ["vanish"]
    assert any(item.definition.id == "keep" for item in system.state.deck.hand)


def test_energy_and_card_counter_reset_each_turn() -> None:
    boost = card("boost", EffectType.GAIN_ENERGY, 2, cost=1, target=TargetType.SELF)
    system = create_system([boost], ["boost"])
    system.play_card(hand_id(system, "boost"))
    assert system.state.player.energy == 4
    assert system.state.cards_played_this_turn == 1
    system.end_player_turn()
    assert system.state.player.energy == 3
    assert system.state.cards_played_this_turn == 0


def test_draw_effect_reshuffles_discard_during_card_resolution() -> None:
    draw_card = card("draw", EffectType.DRAW, 1, cost=0, target=TargetType.SELF)
    filler = card("filler", EffectType.BLOCK, 1, cost=0, target=TargetType.SELF)
    system = create_system([draw_card, filler], ["draw"])
    system.state.deck.discard_pile.append(CardInstance("filler:manual", filler))

    system.play_card(hand_id(system, "draw"))

    assert [item.definition.id for item in system.state.deck.hand] == ["filler"]


def test_enemy_death_during_own_intent_stops_remaining_effects() -> None:
    wait = card("wait", EffectType.BLOCK, 0, cost=0, target=TargetType.SELF)
    self_destruct = EnemyDefinition(
        "self_destruct",
        "self_destruct",
        5,
        (
            EnemyIntent(
                "burst",
                "burst",
                (
                    Effect(EffectType.LOSE_HEALTH, 5, primary=True),
                    Effect(EffectType.DAMAGE, 99),
                ),
            ),
        ),
    )
    system = create_system([wait], ["wait"], [self_destruct], player_hp=20)

    system.end_player_turn()

    assert system.state.outcome is CombatOutcome.VICTORY
    assert system.state.player.current_hp == 20
