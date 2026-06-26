from __future__ import annotations

import pytest

from app.hal import orchestrator as hal_orchestrator


@pytest.fixture(autouse=True)
def enable_hal_ask_model_routing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HAL_ASK_MODEL_ROUTING", "1")


def test_should_escalate_primary_answer_on_empty_or_marker() -> None:
    assert hal_orchestrator._should_escalate_primary_answer("") is True
    assert hal_orchestrator._should_escalate_primary_answer("   ") is True
    assert hal_orchestrator._should_escalate_primary_answer("[NEEDS_ESCALATION]") is True
    assert hal_orchestrator._should_escalate_primary_answer("cannot determine from the provided context") is True


def test_should_not_escalate_primary_answer_for_normal_response() -> None:
    answer = (
        "Latest daily gross production is $7,759 based on verified SoftDent metrics. "
        "Next step: review the provider summary with billing."
    )
    assert hal_orchestrator._should_escalate_primary_answer(answer) is False


def test_should_not_escalate_primary_answer_only_because_it_is_long() -> None:
    answer = "Verified context supports the recommendation. " * 20
    assert hal_orchestrator._should_escalate_primary_answer(answer) is False


def test_answer_hal_question_escalates_from_24b_to_30b(monkeypatch: pytest.MonkeyPatch) -> None:
    context_bundle = {
        "state": {},
        "patient_context": {"matched": False},
        "sanitized": {"findings": []},
        "sanitized_question": "What needs attention today?",
        "hardware_context": [],
        "hardware_review_actions": [],
        "softdent_aggregate_context": [],
        "live_report_context": [],
        "combined_context": [],
        "operating_picture": {"summary": "Operating picture"},
    }

    def fake_collect(**kwargs):
        del kwargs
        return context_bundle

    def fake_generate(*, profile_alias: str, prompt: str, num_predict_cap: int):
        del prompt, num_predict_cap
        if profile_alias == "chat":
            return "[NEEDS_ESCALATION]", None
        if profile_alias == "chat_second_opinion":
            return "Escalated deeper review answer for staff.", None
        return None, "unexpected profile"

    monkeypatch.setattr(hal_orchestrator, "_collect_hal_question_context", fake_collect)
    monkeypatch.setattr(hal_orchestrator, "_generate_profile_answer", fake_generate)

    payload = hal_orchestrator.answer_hal_question(
        question="What needs attention today?",
        actor="hal_operator",
    )

    assert payload["answer"] == "Escalated deeper review answer for staff."
    assert payload["voice_profile"]["label"] == "HAL needed a deeper review"
    assert payload["mode"].endswith(":deeper-review")


def test_answer_hal_question_falls_back_to_deterministic_when_models_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(hal_orchestrator, "_try_hal_model_answer_with_escalation", lambda **kwargs: None)

    payload = hal_orchestrator.answer_hal_question(
        question="Summarize the top two action items",
        actor="hal_operator",
    )

    assert payload["mode"] == hal_orchestrator.HAL_MODE
    assert payload["answer"]
    assert "deterministic server facts first" in payload["guardrails"]
