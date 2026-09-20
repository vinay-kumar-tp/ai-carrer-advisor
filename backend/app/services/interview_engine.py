"""Conversational mock-interview engine.

Two responsibilities:

1. **Drive the conversation** — decide the next interviewer line given the
   transcript so far (adaptive follow-ups that react to the candidate's answer).
2. **Grade the session** — turn the finished transcript into a structured
   performance report (score breakdown, strengths, priorities, per-question
   evidence) that mirrors the target product design.

Every AI call has a deterministic local fallback so the feature works even with
no ``GEMINI_API_KEY`` configured.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional

from app.ai import gemini

# ─── Catalogs (drive the setup dropdowns in the UI) ──────────────

STANDARD_JOB_TITLES = [
    "Junior Developer/Trainee",
    "Machine Learning Intern",
    "Java/Python Developer",
    "Mern Stack Developer",
    "Backend Python Engineer",
    "Quantitative Analyst",
    "Backend Engineer - Node JS",
    "Frontend Engineer - React JS/ Next JS",
    "Machine Learning Engineer - Python",
    "Flutter Developer",
    "Software Engineer (Java)",
    "Data Analyst",
    "DevOps Engineer",
    "Cloud Engineer - AWS",
    "Full Stack Developer",
    "QA / Automation Engineer",
    "Product Manager",
    "Business Analyst",
    "UI/UX Designer",
    "Tax Manager",
    "Senior Accountant",
    "Accounting Clerk",
    "Credit Analyst",
    "Bookkeeper",
    "Accounts Receivable Clerk",
]

SKILLS = [
    "AWS", "Big Data", "Business Development", "Business Intelligence",
    "Business Strategy", "C#", "C++", "Change Management", "Conflict Resolution",
    "Data Analysis", "Django", "Docker", "FastAPI", "Flutter", "Go", "GraphQL",
    "Java", "JavaScript", "Kubernetes", "Leadership", "Machine Learning",
    "MongoDB", "Next.js", "Node.js", "PostgreSQL", "Product Management",
    "Python", "React", "Redis", "REST APIs", "SQL", "System Design",
    "Troubleshooting", "Twitter Marketing", "TypeScript", "UI/UX Design",
    "Visual Basic", "VMware", "Web Design", "Web Development", "Windows Server",
]

DIFFICULTY_LEVELS = ["mixed", "easy", "medium", "hard"]
QUESTION_MIXES = ["technical_behavioral", "behavioral"]

# Interviewer persona shown in the UI.
INTERVIEWER_NAME = "Arjun"

# How many *scored* questions before we wrap up (Q1 is an unscored warm-up).
DEFAULT_TOTAL_QUESTIONS = 8
# Bounds when a caller requests a custom length.
MIN_TOTAL_QUESTIONS = 3
MAX_TOTAL_QUESTIONS = 20


def total_questions_for(config: dict) -> int:
    """Resolve how many scored questions this session runs, honouring an
    optional per-session override while staying within sane bounds."""
    raw = (config or {}).get("num_questions")
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return DEFAULT_TOTAL_QUESTIONS
    return max(MIN_TOTAL_QUESTIONS, min(MAX_TOTAL_QUESTIONS, n))


# ─── Setup helpers ───────────────────────────────────────────────

def build_context_label(config: dict) -> str:
    """A short human title for the practice session, e.g. 'Backend Python Engineer'."""
    source = config.get("source")
    if source == "skill" and config.get("skill"):
        return config["skill"]
    if config.get("job_title"):
        return config["job_title"]
    if source == "resume":
        return "Resume-based Interview"
    return "Software Engineer"


def _difficulty_hint(difficulty: str) -> str:
    return {
        "easy": "Keep questions approachable and foundational.",
        "medium": "Ask solid mid-level questions with some depth.",
        "hard": "Ask challenging, senior-level questions that probe edge cases and trade-offs.",
        "mixed": "Vary difficulty from warm-up to challenging as the conversation goes.",
    }.get(difficulty, "Ask solid mid-level questions.")


def _mix_hint(question_mix: str) -> str:
    if question_mix == "behavioral":
        return "Focus purely on behavioural and situational questions (STAR-style)."
    return "Blend technical/domain questions with behavioural ones."


def _system_prompt(config: dict) -> str:
    label = build_context_label(config)
    jd = (config.get("job_description") or "").strip()
    jd_block = f"\nJob description context:\n{jd[:1500]}" if jd else ""
    return (
        f"You are {INTERVIEWER_NAME}, a warm but rigorous technical interviewer running a "
        f"voice mock interview for a '{label}' role. "
        f"{_difficulty_hint(config.get('difficulty', 'mixed'))} "
        f"{_mix_hint(config.get('question_mix', 'technical_behavioral'))} "
        "Speak naturally, one question at a time, like a real conversation. "
        "React to what the candidate actually said: acknowledge briefly, then either dig deeper "
        "with a follow-up or move to the next area. Keep each turn to 1-3 sentences. "
        "Never list multiple questions at once. Do not give feedback or scores during the interview."
        f"{jd_block}"
    )


# ─── Opening line ────────────────────────────────────────────────

def opening_question(config: dict, candidate_name: str) -> str:
    label = build_context_label(config)
    first = candidate_name.split(" ")[0] if candidate_name else "there"
    return (
        f"Hi {first}, good to meet you. Before we discuss the {label} role, "
        "tell me briefly about your background and what you are aiming for."
    )


# ─── Adaptive next question ──────────────────────────────────────

_LOCAL_BANK = {
    "technical": [
        "Let's talk fundamentals — walk me through a concept you use daily and why it matters.",
        "Can you describe how you'd design a component of this system to scale?",
        "Tell me about a bug that was hard to track down and how you isolated it.",
        "How do you decide between two competing technical approaches?",
        "What does 'production ready' mean to you for the work you do?",
    ],
    "behavioral": [
        "Tell me about a time you disagreed with a teammate. How did it resolve?",
        "Describe a deadline you were at risk of missing. What did you do?",
        "When did you last learn something quickly under pressure?",
        "Tell me about a project you're proud of and your specific contribution.",
        "How do you handle feedback that you don't initially agree with?",
    ],
}


async def next_interviewer_turn(config: dict, transcript: list[dict], turn_index: int) -> str:
    """Return the interviewer's next line, adapting to the transcript.

    ``turn_index`` is the number of scored questions already asked (0-based for
    the one we're about to ask).
    """
    ai_line = await _ai_next_turn(config, transcript, turn_index)
    if ai_line:
        return ai_line

    # Local fallback: alternate technical / behavioural from the bank.
    mix = config.get("question_mix", "technical_behavioral")
    if mix == "behavioral":
        pool = _LOCAL_BANK["behavioral"]
    else:
        pool = _LOCAL_BANK["technical"] if turn_index % 2 == 0 else _LOCAL_BANK["behavioral"]
    return pool[turn_index % len(pool)]


async def _ai_next_turn(config: dict, transcript: list[dict], turn_index: int) -> Optional[str]:
    convo = "\n".join(
        f"{'Interviewer' if m['role'] == 'interviewer' else 'Candidate'}: {m['content']}"
        for m in transcript
    )
    total = total_questions_for(config)
    remaining = max(total - turn_index, 0)
    prompt = (
        f"{convo}\n\n"
        f"This is question {turn_index + 1} of {total} "
        f"({remaining} left after this). "
        "Respond ONLY with your next spoken line as the interviewer (no labels, no quotes). "
        "React to the candidate's last answer, then ask exactly one question."
    )
    return await gemini.generate_text(
        prompt, system=_system_prompt(config), temperature=0.8, max_output_tokens=200
    )


# ─── Report generation ───────────────────────────────────────────

def _clamp(value: Any, lo: int, hi: int, default: int = 0) -> int:
    try:
        return max(lo, min(hi, int(round(float(value)))))
    except (TypeError, ValueError):
        return default


def _band(score: int) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Strong"
    if score >= 55:
        return "Competent"
    if score >= 35:
        return "Developing"
    return "Beginner"


def _qa_pairs(transcript: list[dict]) -> list[dict]:
    """Pair each interviewer question with the candidate's following answer."""
    pairs: list[dict] = []
    pending_q: Optional[str] = None
    for msg in transcript:
        if msg["role"] == "interviewer":
            pending_q = msg["content"]
        elif msg["role"] == "candidate":
            pairs.append({"question": pending_q or "", "answer": msg["content"]})
            pending_q = None
    if pending_q is not None:
        pairs.append({"question": pending_q, "answer": ""})
    return pairs


async def generate_report(config: dict, transcript: list[dict]) -> dict:
    ai_report = await _ai_report(config, transcript)
    if ai_report:
        return _normalize_report(ai_report, config, transcript)
    return _local_report(config, transcript)


async def _ai_report(config: dict, transcript: list[dict]) -> Optional[dict]:
    label = build_context_label(config)
    pairs = _qa_pairs(transcript)
    qa_text = "\n\n".join(
        f"Q{i+1}: {p['question']}\nA{i+1}: {p['answer'] or '(no answer given)'}"
        for i, p in enumerate(pairs)
    )
    schema = """
Return STRICT JSON with this shape:
{
  "overall_score": 0-100,
  "recruiter_perspective": "2-4 sentence recruiter-voice summary",
  "breakdown": {
    "response_quality": {"score": 0-50, "dimensions": {"relevance":0-10,"domain_knowledge":0-10,"articulation":0-10}},
    "behavioural_competency": {"score": 0-30, "dimensions": {"problem_solving":0-10,"attitude":0-10,"learning_agility":0-10,"analytical_thinking":0-10}},
    "speech_quality": {"score": 0-20, "dimensions": {"confidence":0-10,"filler_control":0-10,"pace":0-10}}
  },
  "strengths": ["short strength phrases"],
  "areas_for_improvement": [{"topic":"...","detail":"...","evidence_q": 2}],
  "priorities": [{"topic":"...","summary":"...","what_to_study":["...","..."],"practice_drill":"...","evidence_q": 2}],
  "questions": [{"index":1,"question":"...","answer":"...","score":0-30,"is_warmup":true,"evidence":"one line coaching note"}]
}
Notes: Q1 is an unscored warm-up (is_warmup true, score 0). Be honest and specific; cite weak or missing answers. Sum of the three breakdown scores should equal overall_score.
"""
    prompt = (
        f"You are an expert interview evaluator grading a mock interview for a '{label}' role.\n"
        f"Transcript (question/answer pairs):\n{qa_text}\n\n{schema}"
    )
    return await gemini.generate_json(prompt, temperature=0.3, max_output_tokens=2600)


# ─── Local (no-AI) heuristic scoring ─────────────────────────────

_FILLERS = ("um", "uh", "like", "you know", "basically", "actually", "sort of", "kind of")


def _analyze_answer(answer: str) -> dict:
    text = (answer or "").strip()
    words = re.findall(r"[A-Za-z']+", text)
    wc = len(words)
    lower = text.lower()
    filler_count = sum(lower.count(f) for f in _FILLERS)
    no_answer = wc == 0 or bool(
        re.search(r"\b(i don't know|no idea|never (?:heard|of this)|sorry.*never|not sure)\b", lower)
    )
    # crude 0-30 answer quality from length + no-answer signal
    if no_answer:
        quality = 0
    elif wc < 8:
        quality = 6
    elif wc < 25:
        quality = 16
    elif wc < 60:
        quality = 23
    else:
        quality = 27
    return {"wc": wc, "fillers": filler_count, "no_answer": no_answer, "quality": quality}


def _local_report(config: dict, transcript: list[dict]) -> dict:
    label = build_context_label(config)
    pairs = _qa_pairs(transcript)

    questions: list[dict] = []
    scored_qualities: list[int] = []
    total_words = 0
    total_fillers = 0
    weak_topics: list[str] = []

    for i, p in enumerate(pairs):
        analysis = _analyze_answer(p["answer"])
        total_words += analysis["wc"]
        total_fillers += analysis["fillers"]
        is_warmup = i == 0
        score = 0 if is_warmup else analysis["quality"]
        if not is_warmup:
            scored_qualities.append(analysis["quality"])
            if analysis["quality"] <= 10:
                weak_topics.append(_topic_from_question(p["question"], label))
        if analysis["no_answer"] and not is_warmup:
            evidence = "No substantive answer was captured — practice articulating even a partial approach."
        elif analysis["wc"] < 25 and not is_warmup:
            evidence = "Answer was brief; add a concrete example and explain your reasoning."
        elif is_warmup:
            evidence = "Warm-up introduction — not scored."
        else:
            evidence = "Reasonable answer; tighten structure and quantify impact."
        questions.append({
            "index": i + 1,
            "question": p["question"],
            "answer": p["answer"],
            "score": score,
            "is_warmup": is_warmup,
            "evidence": evidence,
        })

    n = max(len(scored_qualities), 1)
    avg_quality = sum(scored_qualities) / n  # 0-30 scale
    ratio = avg_quality / 30.0

    response_quality = _clamp(ratio * 50, 0, 50)
    behavioural = _clamp(ratio * 30, 0, 30)
    # speech: confidence from answer length, filler penalty, pace estimate
    filler_pct = (total_fillers / total_words * 100) if total_words else 0
    confidence = _clamp(ratio * 10 + 2, 0, 10)
    filler_control = _clamp(10 - filler_pct, 0, 10, default=5)
    pace = 5
    speech = confidence + filler_control + pace
    overall = _clamp(response_quality + behavioural + speech, 0, 100)

    unique_weak = list(dict.fromkeys(weak_topics)) or [label]
    priorities = []
    for idx, topic in enumerate(unique_weak[:3]):
        ev_q = next((q["index"] for q in questions if _topic_from_question(q["question"], label) == topic and not q["is_warmup"]), 2)
        priorities.append({
            "topic": topic,
            "summary": f"Answers on {topic} were weak or missing — build a verified strength here first.",
            "what_to_study": [f"Core concepts of {topic}", f"Real-world application of {topic}"],
            "practice_drill": f"Explain {topic} out loud in 60 seconds, then give one concrete example from your experience.",
            "evidence_q": ev_q,
        })

    areas = [
        {
            "topic": pr["topic"],
            "detail": pr["summary"],
            "evidence_q": pr["evidence_q"],
        }
        for pr in priorities
    ]

    strengths = []
    if overall >= 35:
        strengths.append(f"Foundation being built in {label}")
    if filler_control >= 7:
        strengths.append("Clear speech with few filler words")
    if not strengths:
        strengths.append(f"Foundation being built — start with priority one: {unique_weak[0]}")

    return {
        "overall_score": overall,
        "band": _band(overall),
        "recruiter_perspective": _local_recruiter_note(label, overall, unique_weak),
        "breakdown": {
            "response_quality": {
                "score": response_quality,
                "dimensions": {
                    "relevance": _clamp(ratio * 10, 0, 10),
                    "domain_knowledge": _clamp(ratio * 10, 0, 10),
                    "articulation": _clamp(ratio * 10, 0, 10),
                },
            },
            "behavioural_competency": {
                "score": behavioural,
                "dimensions": {
                    "problem_solving": _clamp(ratio * 10, 0, 10),
                    "attitude": _clamp(ratio * 10, 0, 10),
                    "learning_agility": _clamp(ratio * 10, 0, 10),
                    "analytical_thinking": _clamp(ratio * 10, 0, 10),
                },
            },
            "speech_quality": {
                "score": speech,
                "dimensions": {
                    "confidence": confidence,
                    "filler_control": filler_control,
                    "pace": pace,
                },
                "meta": {
                    "filler_pct": round(filler_pct, 1),
                    "words_per_min": _estimate_wpm(total_words, len(scored_qualities)),
                },
            },
        },
        "strengths": strengths,
        "areas_for_improvement": areas,
        "priorities": priorities,
        "questions": questions,
    }


def _topic_from_question(question: str, fallback: str) -> str:
    q = (question or "").lower()
    for skill in SKILLS:
        if skill.lower() in q:
            return skill
    for kw, topic in (
        ("memory", "Memory management"),
        ("database", "Database design"),
        ("schema", "Schema design"),
        ("scale", "Scalability"),
        ("api", "API design"),
        ("test", "Testing"),
    ):
        if kw in q:
            return topic
    return fallback


def _estimate_wpm(total_words: int, num_answers: int) -> int:
    if not num_answers:
        return 0
    # assume ~ each answer took the words / 2 seconds heuristic; keep it simple
    avg_words = total_words / num_answers
    return int(min(180, max(80, avg_words * 1.6)))


def _local_recruiter_note(label: str, overall: int, weak: list[str]) -> str:
    if overall < 35:
        return (
            f"The candidate demonstrated limited strength in {label} topics. Several answers were "
            f"missing or lacked depth (notably {', '.join(weak[:2])}). Recommend focused practice before "
            "a real interview."
        )
    if overall < 60:
        return (
            f"The candidate shows a developing grasp of {label}. Some answers were on track but "
            "needed more structure and concrete examples. A few focused drills would raise readiness."
        )
    return (
        f"The candidate presented a solid understanding of {label}, communicated clearly, and "
        "backed answers with reasoning. Minor polish on structure would make responses even stronger."
    )


# ─── Normalizing an AI report to the guaranteed shape ────────────

def _normalize_report(raw: Any, config: dict, transcript: list[dict]) -> dict:
    if not isinstance(raw, dict):
        return _local_report(config, transcript)

    breakdown = raw.get("breakdown") or {}
    rq = (breakdown.get("response_quality") or {})
    bc = (breakdown.get("behavioural_competency") or {})
    sq = (breakdown.get("speech_quality") or {})

    rq_score = _clamp(rq.get("score"), 0, 50)
    bc_score = _clamp(bc.get("score"), 0, 30)
    sq_score = _clamp(sq.get("score"), 0, 20)
    overall = _clamp(raw.get("overall_score", rq_score + bc_score + sq_score), 0, 100)

    def dims(source: dict, keys: list[str]) -> dict:
        return {k: _clamp((source.get("dimensions") or {}).get(k), 0, 10) for k in keys}

    questions = raw.get("questions")
    if not isinstance(questions, list) or not questions:
        questions = _local_report(config, transcript)["questions"]
    else:
        for q in questions:
            q["score"] = 0 if q.get("is_warmup") else _clamp(q.get("score"), 0, 30)

    return {
        "overall_score": overall,
        "band": _band(overall),
        "recruiter_perspective": str(raw.get("recruiter_perspective") or "").strip()
            or _local_recruiter_note(build_context_label(config), overall, []),
        "breakdown": {
            "response_quality": {
                "score": rq_score,
                "dimensions": dims(rq, ["relevance", "domain_knowledge", "articulation"]),
            },
            "behavioural_competency": {
                "score": bc_score,
                "dimensions": dims(bc, ["problem_solving", "attitude", "learning_agility", "analytical_thinking"]),
            },
            "speech_quality": {
                "score": sq_score,
                "dimensions": dims(sq, ["confidence", "filler_control", "pace"]),
                "meta": sq.get("meta") or {},
            },
        },
        "strengths": [str(s) for s in (raw.get("strengths") or [])][:5] or ["Foundation being built"],
        "areas_for_improvement": raw.get("areas_for_improvement") or [],
        "priorities": raw.get("priorities") or [],
        "questions": questions,
    }
