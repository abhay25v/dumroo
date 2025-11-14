"""
Streamlit demo app for the AI-powered natural language query system.

Features:
- Select an admin role (RBAC enforced)
- Ask a question in plain English
- Show parsed query and final pandas filters
- Display filtered results
"""
from __future__ import annotations
import json
import streamlit as st
from .config import ADMINS, get_admin_by_name, DATASET_PATH, OPENAI_API_KEY
from .loader import load_students_dataset
from .rbac import filter_by_admin_scope, Admin as RBACAdmin
from .nlp_parser import parse_natural_language
from .query_engine import apply_parsed_filters, build_filter_summary

st.set_page_config(page_title="Dumroo Admin AI Query", layout="wide")
st.title("Dumroo Admin - AI Query")

with st.sidebar:
    st.header("Admin Role")
    admin_name = st.selectbox("Select Admin", options=[a.name for a in ADMINS], index=0)
    admin = get_admin_by_name(admin_name)

    st.markdown("---")
    st.caption(f"Dataset: `{DATASET_PATH}`")
    if OPENAI_API_KEY:
        st.success("OpenAI API key detected: LLM parsing enabled")
    else:
        st.warning("No OpenAI API key set: using rule-based parsing only")

# Example queries for convenience
examples = [
    "Which students haven’t submitted homework?",
    "Show performance for Grade 8 last week",
    "List upcoming quizzes for next week",
]

col1, col2 = st.columns([3, 1])
with col1:
    user_query = st.text_input("Ask a question", value="", placeholder=examples[0])
with col2:
    example = st.selectbox("Examples", options=["(none)"] + examples, index=0)
    if example != "(none)" and not user_query:
        user_query = example

run = st.button("Run Query", type="primary")

if run:
    try:
        df = load_students_dataset()
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.stop()

    # Enforce RBAC scope first
    rbac_admin = RBACAdmin(name=admin.name, allowed_grades=admin.allowed_grades, allowed_classes=admin.allowed_classes, region=admin.region)
    scoped = filter_by_admin_scope(df, rbac_admin)

    # Parse NL query
    parsed = parse_natural_language(user_query)

    # Apply parsed filters on the RBAC-scoped data
    result = apply_parsed_filters(scoped, parsed)

    st.subheader("Parsed Query")
    st.code(json.dumps({
        "intent": parsed.intent,
        "filters": parsed.filters,
        "date_range": {
            "type": parsed.date_range.get("type"),
            "start": str(parsed.date_range.get("start")) if parsed.date_range.get("start") is not None else None,
            "end": str(parsed.date_range.get("end")) if parsed.date_range.get("end") is not None else None,
        },
        "summary": build_filter_summary(parsed),
    }, indent=2), language="json")

    st.subheader("Results")
    st.write(f"Rows: {len(result)}")
    st.dataframe(result.sort_values(by=["grade", "class", "student_name"]).reset_index(drop=True))

    if result.empty:
        st.info("No matching records found within your RBAC scope.")

st.markdown("---")
st.caption("Tip: Set OPENAI_API_KEY to enable LLM-based parsing via LangChain.")
