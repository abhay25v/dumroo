"""
loader.py
---------
Loads and preprocesses the student dataset into a pandas DataFrame.
- Parses dates for `quiz_date` and `submission_date`.
- Ensures expected columns are present.
"""
from __future__ import annotations
import json
import os
from typing import Optional
import pandas as pd

EXPECTED_COLUMNS = [
    "student_name",
    "grade",
    "class",
    "region",
    "homework_submitted",
    "quiz_score",
    "quiz_date",
    "submission_date",
]


def load_students_dataset(path: Optional[str] = None) -> pd.DataFrame:
    """Load dataset from JSON file and preprocess.

    Args:
        path: Optional custom path to the dataset JSON. If None, uses config.DATASET_PATH.

    Returns:
        A pandas DataFrame with parsed dates and normalized dtypes.
    """
    from src.config import DATASET_PATH

    dataset_path = path or DATASET_PATH
    if not os.path.isfile(dataset_path):
        raise FileNotFoundError(f"Dataset not found at: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # Validate expected columns
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset missing columns: {missing}")

    # Normalize dtypes
    df["student_name"] = df["student_name"].astype(str)
    df["grade"] = df["grade"].astype(str)
    df["class"] = df["class"].astype(str)
    df["region"] = df["region"].astype(str)

    # Normalize homework_submitted to lower-case yes/no
    df["homework_submitted"] = df["homework_submitted"].astype(str).str.strip().str.lower()

    # Scores
    df["quiz_score"] = pd.to_numeric(df["quiz_score"], errors="coerce")

    # Dates
    for col in ["quiz_date", "submission_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df
