from enum import StrEnum

class InterviewState(StrEnum):
    CREATED = "created"
    QUESTION_ASKED = "question_asked"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    FOLLOWUP_DECISION = "followup_decision"
    COMPLETE = "complete"

TRANSITIONS = {
    InterviewState.CREATED: {InterviewState.QUESTION_ASKED, InterviewState.COMPLETE},
    InterviewState.QUESTION_ASKED: {InterviewState.RECORDING, InterviewState.ANALYZING, InterviewState.COMPLETE},
    InterviewState.RECORDING: {InterviewState.TRANSCRIBING, InterviewState.QUESTION_ASKED},
    InterviewState.TRANSCRIBING: {InterviewState.ANALYZING},
    InterviewState.ANALYZING: {InterviewState.FOLLOWUP_DECISION},
    InterviewState.FOLLOWUP_DECISION: {InterviewState.QUESTION_ASKED, InterviewState.COMPLETE},
    InterviewState.COMPLETE: set(),
}

def transition(current: InterviewState, target: InterviewState) -> InterviewState:
    if target not in TRANSITIONS[current]:
        raise ValueError(f"Invalid interview transition: {current.value} -> {target.value}")
    return target
