"""Question packs are configuration-like data, independent of inference providers."""
QUESTION_BANK = {
    "Software Engineering": [
        ("How would you design a URL shortener that handles high read traffic?", ["cache", "database", "idempotency", "scale"]),
        ("Explain how you would find a cycle in a linked list.", ["slow", "fast", "pointer", "complexity"]),
        ("What trade-offs would you consider when choosing a relational database?", ["schema", "transaction", "consistency", "query"]),
        ("How do you make an API reliable when a downstream service is unavailable?", ["retry", "timeout", "circuit breaker", "fallback"]),
        ("Describe a technical decision you would revisit and what you learned.", ["context", "trade-off", "impact", "lesson"]),
    ],
    "Python": [
        ("What is the difference between a list and a generator in Python?", ["lazy", "memory", "iteration", "yield"]),
        ("How do Python decorators work, and when would you use one?", ["function", "wrapper", "callable", "metadata"]),
        ("How would you investigate a slow Python endpoint?", ["profile", "measure", "database", "bottleneck"]),
    ],
    "Java": [("Explain how garbage collection works in Java and one trade-off.", ["heap", "object", "collection", "pause"]), ("What problem do interfaces solve in Java design?", ["contract", "implementation", "polymorphism", "decouple"])],
    "Data Structures & Algorithms": [("Explain the time and space complexity of binary search.", ["sorted", "log", "mid", "space"]), ("How would you choose between a hash map and a balanced tree?", ["lookup", "ordered", "complexity", "collision"])],
    "Machine Learning": [("Compare classification and regression in supervised learning.", ["label", "classification", "regression", "target"]), ("How would you diagnose overfitting in a model?", ["validation", "regularization", "training", "generalization"])],
    "Artificial Intelligence": [("How does retrieval-augmented generation reduce unsupported answers?", ["retrieval", "context", "ground", "source"]), ("What is the difference between a model parameter and a hyperparameter?", ["learned", "training", "configuration", "validation"])],
    "Data Science": [("How would you handle missing values in a dataset?", ["missing", "imputation", "bias", "analysis"]), ("How do you explain a model result to a non-technical stakeholder?", ["metric", "baseline", "uncertainty", "impact"])],
    "Backend Development": [("How would you design rate limiting for a public API?", ["limit", "token bucket", "redis", "client"]), ("What makes a database migration safe to deploy?", ["backward compatible", "rollback", "staged", "data"])],
    "System Design": [("Design a notification service that supports retries and user preferences.", ["queue", "retry", "idempotency", "preference"]), ("How would you scale a service while preserving observability?", ["metrics", "logs", "trace", "bottleneck"])],
    "HR / Behavioral": [("Tell me about a time you received difficult feedback.", ["situation", "action", "result", "learning"]), ("Describe a disagreement on a team and how you handled it.", ["listen", "evidence", "decision", "outcome"])],
}

CATEGORIES = list(QUESTION_BANK.keys())
DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"]

def make_questions(category: str, count: int, resume_skills: list[str] | None = None):
    bank = QUESTION_BANK.get(category, QUESTION_BANK["Software Engineering"])
    questions = [{"text": q, "concepts": c, "kind": "technical"} for q, c in bank]
    for skill in (resume_skills or [])[:2]:
        questions.insert(0, {"text": f"You listed {skill} on your resume. Tell me about a project where you used it and one trade-off you encountered.", "concepts": [skill.lower(), "project", "trade-off", "result"], "kind": "resume"})
    if len(questions) < count:
        questions = questions * (count // len(questions) + 1)
    return questions[:count]
