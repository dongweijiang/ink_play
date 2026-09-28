"""使用极简自动策略运行一场纯规则战斗。"""

from __future__ import annotations

import sys

from src.domain.actor import EnemyDefinition, EnemyIntent
from src.domain.card import CardDefinition, CardType, TargetType
from src.domain.combat import CombatOutcome
from src.domain.effects import Effect, EffectType
from src.systems.combat_system import CombatSystem


def build_demo() -> CombatSystem:
    """建立不依赖 JSON 和 pygame 的规则演示战斗。"""
    strike = CardDefinition(
        "demo_strike",
        "试锋",
        CardType.ATTACK,
        1,
        TargetType.SINGLE_ENEMY,
        (Effect(EffectType.DAMAGE, 7, primary=True),),
    )
    guard = CardDefinition(
        "demo_guard",
        "试守",
        CardType.SKILL,
        1,
        TargetType.SELF,
        (Effect(EffectType.BLOCK, 5, primary=True),),
    )
    enemy = EnemyDefinition(
        "demo_wraith",
        "纸影（测试）",
        38,
        (
            EnemyIntent("slash", "抓击 6", (Effect(EffectType.DAMAGE, 6, primary=True),)),
            EnemyIntent("guard", "聚纸 5", (Effect(EffectType.BLOCK, 5, primary=True),)),
            EnemyIntent("lunge", "扑击 9", (Effect(EffectType.DAMAGE, 9, primary=True),)),
        ),
    )
    return CombatSystem.create(
        card_definitions=(strike, guard),
        deck_ids=["demo_strike"] * 5 + ["demo_guard"] * 5,
        enemy_definitions=(enemy,),
        seed=20260928,
        player_hp=45,
    )


def main() -> int:
    """自动优先出攻击牌，打印每回合摘要并返回结果码。"""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    system = build_demo()
    while system.state.outcome is CombatOutcome.ONGOING:
        state = system.state
        print(
            f"回合 {state.turn} | 玩家 {state.player.current_hp}/{state.player.max_hp} "
            f"能量 {state.player.energy} | 敌人 {state.enemies[0].current_hp}/{state.enemies[0].max_hp} "
            f"意图 {state.visible_intents[0].name}"
        )
        ordered = sorted(
            list(state.deck.hand),
            key=lambda item: item.definition.type is CardType.SKILL,
        )
        for item in ordered:
            target = 0 if item.definition.target is TargetType.SINGLE_ENEMY else None
            system.play_card(item.instance_id, target)
            if state.outcome is not CombatOutcome.ONGOING:
                break
        if state.outcome is CombatOutcome.ONGOING:
            system.end_player_turn()
    print(f"战斗结果：{system.state.outcome.value}，玩家剩余生命 {system.state.player.current_hp}")
    return 0 if system.state.outcome is CombatOutcome.VICTORY else 1


if __name__ == "__main__":
    raise SystemExit(main())
