"""Test-only providers used to verify business logic remains hardware-agnostic."""
from app.ai.interfaces.contracts import AnswerEvaluation, EvaluationInput

class MockCPUProvider:
    name = "mock-cpu"
    def evaluate_answer(self, request: EvaluationInput) -> AnswerEvaluation:
        return AnswerEvaluation(70, 80, 60, ["mock strength"], ["mock improvement"], ["mock evidence"], [], evaluator=self.name)

class MockSnapdragonProvider:
    name = "mock-snapdragon"
    def evaluate_answer(self, request: EvaluationInput) -> AnswerEvaluation:
        return AnswerEvaluation(70, 80, 60, ["mock strength"], ["mock improvement"], ["mock evidence"], [], evaluator=self.name)
