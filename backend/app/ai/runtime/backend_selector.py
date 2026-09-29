"""Select only providers implemented and validated in this build; requested accelerators fall back honestly."""
import os
from app.ai.providers.rule_based import RuleBasedEvaluator


def select_evaluator():
    requested = os.getenv("AI_BACKEND", "auto").lower()
    evaluator = RuleBasedEvaluator()
    if requested in {"auto", "cpu", "local"}:
        return evaluator, {"requested": requested, "active": evaluator.name, "fallback": False, "message": None}
    return evaluator, {
        "requested": requested,
        "active": evaluator.name,
        "fallback": True,
        "message": f"Requested backend '{requested}' is not implemented in this build; using the local rubric evaluator.",
    }
