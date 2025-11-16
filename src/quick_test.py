r"""
Quick CLI test to validate core pipeline without launching Streamlit.
Usage:
    .\.venv\Scripts\python.exe src/quick_test.py "Which students haven’t submitted homework?"
If no arg provided, runs 3 example queries for Admin 'Amit'.
"""
from __future__ import annotations
import sys
from src.config import get_admin_by_name
from src.loader import load_students_dataset
from src.rbac import filter_by_admin_scope, Admin as RBACAdmin
from src.nlp_parser import parse_natural_language
from src.query_engine import apply_parsed_filters, build_filter_summary

admin = get_admin_by_name("Amit")
if not admin:
    raise SystemExit("Admin 'Amit' not found in config")

queries = sys.argv[1:]
if not queries:
    queries = [
        "Which students haven’t submitted homework?",
        "Show performance for Grade 8 last week",
        "List upcoming quizzes for next week",
    ]

print("Loading dataset...")
df = load_students_dataset()
rbac_admin = RBACAdmin(name=admin.name, allowed_grades=admin.allowed_grades, allowed_classes=admin.allowed_classes, region=admin.region)
scoped = filter_by_admin_scope(df, rbac_admin)

for q in queries:
    parsed = parse_natural_language(q)
    result = apply_parsed_filters(scoped, parsed)
    print("\nQuery:", q)
    print("Parsed:", build_filter_summary(parsed))
    print("Rows:", len(result))
    print(result.head(5).to_string(index=False))
