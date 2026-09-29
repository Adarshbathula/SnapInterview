import re
FILLER_PATTERN = re.compile(r"\b(um+|uh+|like|you know|basically|actually)\b", re.I)
def communication_metrics(text: str, duration_seconds: float | None = None, segments: list[dict] | None = None) -> dict:
    words = re.findall(r"\b[\w+#.-]+\b", text)
    fillers = FILLER_PATTERN.findall(text)
    duration = max(0.0, float(duration_seconds or 0))
    gaps=[]
    if segments:
        ordered=sorted(segments,key=lambda x:float(x.get("start",0)))
        gaps=[max(0.0,float(b.get("start",0))-float(a.get("end",0))) for a,b in zip(ordered,ordered[1:])]
    long_gaps=[gap for gap in gaps if gap>=1.5]
    return {
        "word_count": len(words),
        "duration_seconds": duration,
        "words_per_minute": round(len(words) / (duration / 60), 1) if duration > 0 else None,
        "filler_words": len(fillers),
        "long_pauses": len(long_gaps) if segments else None,
        "long_pause_seconds": round(sum(long_gaps),2) if segments else None,
        "note": "Transcript/audio timing metrics only; long pauses are estimated from ASR word timestamps at a 1.5-second gap. These are not psychological assessments.",
    }
