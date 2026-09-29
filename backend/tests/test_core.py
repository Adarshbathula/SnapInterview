from app.ai.interfaces.contracts import EvaluationInput
from app.ai.providers.rule_based import RuleBasedEvaluator
from app.hardware.detector import detect_hardware
from app.interview.catalog import CATEGORIES, make_questions
from app.interview.state_machine import InterviewState, transition
from app.analytics.communication import communication_metrics
from app.ai.providers.mock import MockCPUProvider, MockSnapdragonProvider
from app.ai.runtime.backend_selector import select_evaluator


def test_catalog_supports_requested_categories():
    assert "Python" in CATEGORIES
    assert make_questions("Python", 5)


def test_evaluator_is_deterministic_and_evidence_based():
    evaluator = RuleBasedEvaluator()
    result = evaluator.evaluate_answer(EvaluationInput("Explain RAG", "RAG uses retrieval to add context and ground answers with sources.", ["retrieval", "context", "ground", "source"]))
    assert result.technical_accuracy > 0
    assert not result.missing_concepts
    assert result.evaluator == "local-rubric (development)"
    assert result.evidence


def test_empty_answer_is_handled():
    result = RuleBasedEvaluator().evaluate_answer(EvaluationInput("Question", " ", ["concept"]))
    assert result.technical_accuracy == 0


def test_hardware_detector_does_not_claim_unverified_npu():
    info = detect_hardware()
    assert "execution_providers" in info
    assert isinstance(info["npu_runtime_detected"], bool)


def test_communication_metrics_are_transcript_based():
    metrics = communication_metrics("Um, I used Python and, like, measured the result.", 30)
    assert metrics["word_count"] > 0
    assert metrics["filler_words"] == 2
    assert metrics["words_per_minute"] is not None
    assert metrics["long_pauses"] is None
    timed=communication_metrics("one two three",3,[{"start":0.0,"end":0.4},{"start":2.5,"end":2.9}])
    assert timed["long_pauses"]==1


def test_interview_state_machine_rejects_invalid_transition():
    assert transition(InterviewState.CREATED, InterviewState.QUESTION_ASKED) == InterviewState.QUESTION_ASKED
    try:
        transition(InterviewState.CREATED, InterviewState.ANALYZING)
    except ValueError:
        pass
    else:
        assert False, "invalid transition must fail"


def test_business_contract_accepts_mock_cpu_and_snapdragon_providers():
    request = EvaluationInput("Explain caching", "A cache stores a recent result.")
    for provider in (MockCPUProvider(), MockSnapdragonProvider()):
        result = provider.evaluate_answer(request)
        assert result.technical_accuracy == 70
        assert result.evaluator == provider.name


def test_unavailable_specialized_backend_falls_back_honestly(monkeypatch):
    monkeypatch.setenv("AI_BACKEND", "snapdragon")
    provider, status = select_evaluator()
    assert status["fallback"] is True
    assert "not implemented" in status["message"]
    assert provider.name == "local-rubric (development)"
