# Dumroo Admin – AI-Powered Natural Language Query

This is a minimal, extensible system that turns plain-English questions into filtered results over a student dataset using Pandas with optional LangChain + OpenAI parsing. Role-based access control (RBAC) ensures each admin only sees scoped data.

## Features
- Natural-language → structured intent → Pandas filters
- RBAC scoping by grade, class, and region
- Streamlit demo UI (input + admin selector + results)
- Sample dataset (`dataset/students.json`, ~36 rows)
- Modular code to later swap in a real DB

## Project Structure
- `dataset/students.json`: sample data
- `src/config.py`: dataset path, admin roles, optional OpenAI model
- `src/loader.py`: load + preprocess JSON dataset into pandas
- `src/rbac.py`: RBAC filters enforcing grade/class/region
- `src/nlp_parser.py`: rule-based parser with optional LangChain + OpenAI enhancement
- `src/query_engine.py`: maps parsed intent to Pandas filters
- `src/app.py`: Streamlit UI wrapper
- `requirements.txt`

## Setup (Windows PowerShell)
```powershell
# 1) Create and activate a virtual environment (recommended)
python -m venv .venv
. .\.venv\Scripts\Activate.ps1

# 2) Install dependencies
pip install -r requirements.txt

# 3) (Optional) Enable LLM parsing
$env:OPENAI_API_KEY = "<your_openai_api_key>"
# To persist, you can also create a .env file with OPENAI_API_KEY=...

# 4) Run the Streamlit app
streamlit run src/app.py
```

### Faster start
- Use the venv binary directly to avoid PATH issues:
```powershell
.\.venv\Scripts\streamlit.exe run src/app.py
```
- One-liner helper script:
```powershell
./run.ps1
```
- Quick CLI validation (no UI):
```powershell
.\.venv\Scripts\python.exe src/quick_test.py "Which students haven’t submitted homework?"
```

## Example Admins
Defined in `src/config.py`:
- `Amit`: Grade 8, classes 8A/8B, region East
- `Riya`: Grade 7, class 7A, region West
- `Kabir`: Grade 9, classes 9A/9B, region North

RBAC filter enforced:
- `grade ∈ allowed_grades AND class ∈ allowed_classes AND region == admin.region`

## Example Queries
Try these in the app:
- "Which students haven’t submitted homework?"
- "Show performance for Grade 8 last week"
- "List upcoming quizzes for next week"

## How It Works
- `parse_natural_language()` returns a `ParseResult` with `intent`, `filters`, and optional `date_range` (last/this/next week)
- `query_engine.apply_parsed_filters()` turns that into Pandas filtering over the RBAC-scoped DataFrame
- If `OPENAI_API_KEY` is set, LangChain+OpenAI is used to refine the rule-based parse; otherwise parsing is deterministic. LangChain is lazily imported only when used for faster startup.

## Swap Dataset Later
- Place a compatible JSON at `dataset/students.json` or set the `DATASET_PATH` environment variable.
- Fields required: `student_name`, `grade`, `class`, `region`, `homework_submitted` (yes/no), `quiz_score`, `quiz_date`, `submission_date`.

## Notes
- This demo focuses on filtering, not aggregation. "Performance" is treated as quiz filtering; you can extend to compute stats.
- Dates (last/this/next week) are resolved relative to the current date.
