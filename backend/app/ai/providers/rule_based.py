"""Deterministic development evaluator. This is not an LLM or a validated grading model."""
import re
from app.ai.interfaces.contracts import AnswerEvaluation, EvaluationInput


class RuleBasedEvaluator:
    name = "local-rubric (development)"

    def evaluate_answer(self, request: EvaluationInput) -> AnswerEvaluation:
        answer = request.answer.strip()
        words = re.findall(r"\b[\w+#.-]+\b", answer.lower())
        if not words:
            return AnswerEvaluation(0, 0, 0, [], ["Add an answer before requesting feedback."], [], request.expected_concepts, evaluator=self.name)
        normalized = " " + " ".join(words) + " "
        present = [term for term in request.expected_concepts if term.lower() in normalized]
        missing = [term for term in request.expected_concepts if term.lower() not in normalized]
        coverage = len(present) / max(1, len(request.expected_concepts))
        length_factor = min(1.0, len(words) / 55)
        accuracy = round(min(95, 35 + coverage * 60)) if request.expected_concepts else round(min(90, 45 + length_factor * 40))
        relevance = round(min(95, 48 + min(len(words), 90) * 0.45))
        completeness = round(min(95, 25 + coverage * 55 + length_factor * 15))
        evidence = []
        if present:
            evidence.append("Your answer mentioned: " + ", ".join(present[:5]) + ".")
        if len(words) < 20:
            evidence.append("The transcript is brief; an example or explanation would make the reasoning easier to assess.")
        elif len(words) > 180:
            evidence.append("The answer is lengthy; consider leading with the main point before adding detail.")
        else:
            evidence.append(f"The answer contains {len(words)} words and addresses the prompt.")
        improvements = []
        if missing:
            improvements.append("Consider covering: " + ", ".join(missing[:4]) + ".")
        if len(words) < 35:
            improvements.append("Add a concrete example and explain why the approach works.")
        if not improvements:
            improvements.append("Make the explanation even stronger by connecting the concept to a practical trade-off.")
        strengths = ["You responded directly to the question."]
        if present:
            strengths = [f"You correctly included {present[0]}."]
        follow_up = None
        if missing:
            follow_up = f"Can you explain {missing[0]} and how it relates to your answer?"
        return AnswerEvaluation(accuracy, relevance, completeness, strengths, improvements, evidence, missing, follow_up, self.name)
