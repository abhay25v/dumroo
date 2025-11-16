"""
nlp_parser.py
-------------
Natural-language parsing to a structured intent using a rule-based approach
with optional enhancement via LangChain + OpenAI.

Output structure (ParseResult):
- intent: 'homework' | 'quizzes' | 'performance'
- filters: dict with optional keys: grade (e.g., 'Grade 8'), classes (list), region (str), homework_submitted ('yes'/'no')
- date_range: dict with 'type': 'last_week' | 'next_week' | 'this_week' | 'custom' | None,
              and optional 'start'/'end' as pandas.Timestamp
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

from src.config import OPENAI_API_KEY, OPENAI_MODEL


@dataclass
class ParseResult:
    intent: str
    filters: Dict[str, Any] = field(default_factory=dict)
    date_range: Dict[str, Any] = field(default_factory=dict)


def _monday_of_week(dt: datetime) -> datetime:
    return dt - timedelta(days=dt.weekday())


def _sunday_of_week(dt: datetime) -> datetime:
    return _monday_of_week(dt) + timedelta(days=6)


def _compute_range(keyword: str, now: Optional[datetime] = None) -> Dict[str, Any]:
    now = now or datetime.now()
    if keyword == "last_week":
        end = _sunday_of_week(now - timedelta(weeks=1))
        start = end - timedelta(days=6)
        return {"type": "last_week", "start": pd.Timestamp(start.date()), "end": pd.Timestamp(end.date())}
    if keyword == "this_week":
        start = _monday_of_week(now)
        end = _sunday_of_week(now)
        return {"type": "this_week", "start": pd.Timestamp(start.date()), "end": pd.Timestamp(end.date())}
    if keyword == "next_week":
        start = _monday_of_week(now + timedelta(weeks=1))
        end = start + timedelta(days=6)
        return {"type": "next_week", "start": pd.Timestamp(start.date()), "end": pd.Timestamp(end.date())}
    return {"type": None}


def _rule_based_parse(text: str) -> ParseResult:
    t = text.strip().lower()

    # Determine intent
    if any(k in t for k in ["homework", "submit", "submission", "submitted", "haven't submitted", "didn't submit"]):
        intent = "homework"
    elif any(k in t for k in ["quiz", "quizzes", "score", "performance"]):
        # Treat 'performance' as quiz performance by default
        intent = "quizzes"
        if "performance" in t:
            intent = "performance"
    else:
        # Default to quizzes listing
        intent = "quizzes"

    filters: Dict[str, Any] = {}

    # Homework submitted status
    if intent == "homework":
        if any(neg in t for neg in ["not submitted", "didn't submit", "didnt submit", "haven't submitted", "havent submitted", "no submission"]):
            filters["homework_submitted"] = "no"
        elif "submitted" in t:
            filters["homework_submitted"] = "yes"

    # Grade extraction like "grade 8" or "class 8a"
    grade_match = re.search(r"grade\s*(\d+)", t)
    if grade_match:
        filters["grade"] = f"Grade {grade_match.group(1)}"

    # Class extraction like 8A or 8B
    class_match = re.search(r"\b(\d{1,2}[a-z])\b", t)
    if class_match:
        filters.setdefault("classes", []).append(class_match.group(1).upper())

    # Region extraction
    reg_match = re.search(r"\b(north|south|east|west)\b", t)
    if reg_match:
        filters["region"] = reg_match.group(1).capitalize()

    # Date range extraction
    if "last week" in t:
        date_range = _compute_range("last_week")
    elif "this week" in t:
        date_range = _compute_range("this_week")
    elif "next week" in t:
        date_range = _compute_range("next_week")
    else:
        date_range = {"type": None}

    return ParseResult(intent=intent, filters=filters, date_range=date_range)


def _llm_enhance(text: str, seed: ParseResult) -> ParseResult:
    """Optionally enhance rule-based parse via LangChain + OpenAI.
    If no API key or library missing, returns seed.
    """
    if not OPENAI_API_KEY:
        return seed

    try:
        # Lazy imports to avoid slowing down startup when LLM is unused
        from langchain_openai import ChatOpenAI
        from langchain.prompts import PromptTemplate
    except Exception:
        return seed

    prompt_tmpl = PromptTemplate(
        template=(
            """
            You are a parser. Convert the user question into a compact JSON with keys:
            intent: one of [homework, quizzes, performance]
            filters: may include grade (e.g., "Grade 8"), classes (list), region (capitalized), homework_submitted ("yes"/"no")
            date_range: one of last_week, this_week, next_week, or null
            Only output JSON. Example:
            {"intent":"quizzes","filters":{"grade":"Grade 8"},"date_range":"last_week"}
            Question: {question}
            """
        ),
        input_variables=["question"],
    )

    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)
    try:
        msg = llm.invoke(prompt_tmpl.format(question=text))
        content = msg.content.strip()
        # Very defensive parsing
        import json as _json
        parsed = _json.loads(content)
        intent = parsed.get("intent", seed.intent)
        filters = seed.filters.copy()
        for k, v in (parsed.get("filters") or {}).items():
            filters[k] = v
        dr = parsed.get("date_range")
        if isinstance(dr, str) and dr in {"last_week", "this_week", "next_week"}:
            date_range = _compute_range(dr)
        else:
            date_range = seed.date_range
        return ParseResult(intent=intent, filters=filters, date_range=date_range)
    except Exception:
        return seed


def parse_natural_language(text: str) -> ParseResult:
    """Parse a plain-English query into a structured ParseResult.

    Uses a deterministic rule-based parser, then optionally refines via LLM.
    """
    seed = _rule_based_parse(text)
    return _llm_enhance(text, seed)
