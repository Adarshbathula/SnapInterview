"""Hardware-agnostic AI contracts. Keep runtime-specific objects out of this module."""
from dataclasses import dataclass, field
from typing import Protocol, Any


@dataclass
class EvaluationInput:
    question: str
    answer: str
    expected_concepts: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnswerEvaluation:
    technical_accuracy: int
    relevance: int
    completeness: int
    strengths: list[str]
    improvements: list[str]
    evidence: list[str]
    missing_concepts: list[str]
    follow_up_question: str | None = None
    evaluator: str = "unknown"


class LLMProvider(Protocol):
    name: str
    def evaluate_answer(self, request: EvaluationInput) -> AnswerEvaluation: ...


class SpeechRecognizer(Protocol):
    name: str
    def transcribe(self, audio: bytes, content_type: str, language: str | None = None) -> dict[str, Any]: ...


class EmbeddingProvider(Protocol):
    name: str
    def embed(self, text: str) -> list[float]: ...


class VisionAnalyzer(Protocol):
    name: str
    def analyze(self, frame: bytes) -> dict[str, float]: ...
