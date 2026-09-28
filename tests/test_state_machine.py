"""状态机生命周期与暂停恢复测试。"""

from __future__ import annotations

from src.state_machine import BaseState, StateID, StateMachine


class RecordingState(BaseState):
    def __init__(self) -> None:
        self.events: list[str] = []

    def enter(self) -> None:
        self.events.append("enter")

    def exit(self) -> None:
        self.events.append("exit")


def build_machine() -> tuple[StateMachine, dict[StateID, RecordingState]]:
    machine = StateMachine()
    states = {
        StateID.MAIN_MENU: RecordingState(),
        StateID.RUN_MAP: RecordingState(),
        StateID.PAUSED: RecordingState(),
    }
    for state_id, state in states.items():
        machine.register(state_id, state)
    return machine, states


def test_transition_is_deferred_until_commit() -> None:
    machine, states = build_machine()
    machine.start(StateID.MAIN_MENU)

    machine.request(StateID.RUN_MAP)

    assert machine.current_id is StateID.MAIN_MENU
    assert machine.has_pending_change
    assert machine.commit()
    assert machine.current_id is StateID.RUN_MAP
    assert states[StateID.MAIN_MENU].events == ["enter", "exit"]
    assert states[StateID.RUN_MAP].events == ["enter"]


def test_pause_can_resume_previous_state() -> None:
    machine, _ = build_machine()
    machine.start(StateID.RUN_MAP)
    machine.request(StateID.PAUSED, remember_current=True)
    machine.commit()

    machine.request_resume()
    machine.commit()

    assert machine.current_id is StateID.RUN_MAP


def test_duplicate_registration_is_rejected() -> None:
    machine = StateMachine()
    machine.register(StateID.MAIN_MENU, RecordingState())

    try:
        machine.register(StateID.MAIN_MENU, RecordingState())
    except ValueError as exc:
        assert "MAIN_MENU" in str(exc)
    else:
        raise AssertionError("重复状态 ID 应被拒绝")


def test_all_required_state_ids_exist() -> None:
    expected = {
        "BOOT", "MAIN_MENU", "SETTINGS", "RUN_MAP", "COMBAT", "CARD_REWARD",
        "DRAWING", "DRAWING_RESULT", "EVENT", "SHOP", "REST", "PAUSED",
        "GAME_OVER", "VICTORY",
    }
    assert {state.name for state in StateID} == expected
