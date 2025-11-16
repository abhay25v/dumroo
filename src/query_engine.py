"""
query_engine.py
----------------
Maps a parsed query (from nlp_parser) to pandas filtering operations
and returns a filtered DataFrame.
"""
from __future__ import annotations
from typing import Dict, Any, Optional
import pandas as pd
from src.nlp_parser import ParseResult


def _apply_date_range(df: pd.DataFrame, column: str, date_range: Dict[str, Any]) -> pd.DataFrame:
    if not date_range or not date_range.get("type"):
        return df
    start = date_range.get("start")
    end = date_range.get("end")
    if start is not None:
        df = df[df[column] >= pd.to_datetime(start)]
    if end is not None:
        df = df[df[column] <= pd.to_datetime(end)]
    return df


def build_filter_summary(parsed: ParseResult) -> str:
    parts = [f"intent={parsed.intent}"]
    if parsed.filters:
        parts.append(f"filters={parsed.filters}")
    if parsed.date_range and parsed.date_range.get("type"):
        parts.append(
            f"date_range={parsed.date_range['type']}({parsed.date_range.get('start')}→{parsed.date_range.get('end')})"
        )
    return "; ".join(parts)


def apply_parsed_filters(df: pd.DataFrame, parsed: ParseResult) -> pd.DataFrame:
    """Apply parsed filters and date ranges to the RBAC-scoped DataFrame.

    Notes:
    - For quizzes/performance intents, date_range applies to 'quiz_date'.
    - For homework intent, if filtering for submitted=yes, date_range applies to 'submission_date'.
      If submitted=no, date_range is ignored as submission_date is typically null.
    """
    if df.empty:
        return df

    # Static filters first
    f = parsed.filters or {}

    if "grade" in f:
        df = df[df["grade"].eq(f["grade"])]

    if "classes" in f and f["classes"]:
        df = df[df["class"].isin([c.upper() for c in f["classes"]])]

    if "region" in f:
        df = df[df["region"].eq(f["region"]) ]

    if parsed.intent == "homework":
        if "homework_submitted" in f:
            df = df[df["homework_submitted"].eq(str(f["homework_submitted"]).lower())]
        # Apply date range only if looking at submitted homework
        if f.get("homework_submitted", "") == "yes":
            df = _apply_date_range(df, "submission_date", parsed.date_range)
    else:
        # quizzes or performance -> filter by quiz_date range
        df = _apply_date_range(df, "quiz_date", parsed.date_range)

    return df
