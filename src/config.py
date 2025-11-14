"""
Configuration for dataset path, admin roles, and optional LLM setup.
Loads environment variables from a .env file if present.
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# Dataset path (relative to repo root)
DATASET_PATH = os.getenv("DATASET_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset", "students.json"))

# OpenAI settings (optional). If not set, the system falls back to rule-based parsing.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

@dataclass
class Admin:
    name: str
    allowed_grades: List[str]
    allowed_classes: List[str]
    region: str

# Example admin roles; you can add more as needed.
ADMINS: List[Admin] = [
    Admin(name="Amit", allowed_grades=["Grade 8"], allowed_classes=["8A", "8B"], region="East"),
    Admin(name="Riya", allowed_grades=["Grade 7"], allowed_classes=["7A"], region="West"),
    Admin(name="Kabir", allowed_grades=["Grade 9"], allowed_classes=["9A", "9B"], region="North"),
]

# Utility to get admin by name (used by UI)
def get_admin_by_name(name: str) -> Admin | None:
    for a in ADMINS:
        if a.name == name:
            return a
    return None
