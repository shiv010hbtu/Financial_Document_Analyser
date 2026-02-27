# 🏦 Financial Document Analyzer

> AI-powered financial document analysis system using CrewAI multi-agent framework. Upload any financial PDF and get instant investment insights, risk assessments, and market analysis.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Bugs Found & Fixed](#-bugs-found--fixed)
- [Setup & Installation](#-setup--installation)
- [API Documentation](#-api-documentation)
- [Agent Pipeline](#-agent-pipeline)
- [Troubleshooting](#-troubleshooting)

---

## 🔍 Project Overview

The Financial Document Analyzer accepts PDF financial reports (e.g. Tesla Q2 2025) and runs them through a pipeline of specialized AI agents to produce:

- 📊 **Financial Analysis** — Key metrics, revenue trends, growth indicators
- 💡 **Investment Recommendations** — BUY / HOLD / SELL with rationale
- ⚠️ **Risk Assessment** — Market, credit, liquidity, and operational risks
- ✅ **Document Verification** — Confirms document is a valid financial report

**Tech Stack:**

| Layer | Technology |
|-------|-----------|
| AI Framework | CrewAI 0.130.0 |
| API Server | FastAPI 0.110.3 |
| LLM | Google Gemini / OpenAI |
| PDF Parsing | pypdf 4.2.0 |
| Web Search | SerperDevTool |
| Data Validation | Pydantic v2 |

---

## 🏗️ Architecture

```
User uploads PDF via POST /analyze
            │
            ▼
    FastAPI (main.py)
            │
            ▼
    run_crew() — CrewAI Orchestrator
            │
    ┌───────┴────────────────────────┐
    │                                │
    ▼                                ▼
Step 1: verifier          Step 2: financial_analyst
Validates PDF is          Extracts metrics, trends,
a real financial          highlights & concerns
report                    from document
    │                                │
    └───────────┬────────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
Step 3:               Step 4:
investment_advisor    risk_assessor
BUY/HOLD/SELL         Risk matrix with
recommendation        severity ratings
                │
                ▼
        JSON Response to User
```

---

## 📁 Project Structure

```
financial-document-analyzer/
│
├── main.py           # FastAPI server — endpoints & crew orchestration
├── agents.py         # 4 CrewAI agents definitions
├── tasks.py          # 4 CrewAI tasks assigned to agents
├── tools.py          # PDF reader, investment & risk tools
├── requirements.txt  # Python dependencies
├── .env              # API keys (not committed to git)
├── data/
│   └── sample.pdf    # Default sample financial document
└── README.md         # This file
```

---

## 🐛 Bugs Found & Fixed

This project had **48 total bugs** across 5 files — split into **Deterministic Bugs** (code crashes) and **Inefficient Prompts** (AI produces harmful/fabricated output).

---

### 📄 `requirements.txt` — 3 Bugs

| # | Bug | Fix |
|---|-----|-----|
| 1 | `pydantic==1.10.13` (v1) — crewai requires pydantic v2 | `pydantic==2.7.1` |
| 2 | `pydantic_core==2.8.0` — mismatched with pydantic v1 | `pydantic_core==2.18.2` |
| 3 | `pypdf` missing — PDF reading impossible | Added `pypdf==4.2.0` |

---

### 📄 `main.py` — 6 Bugs

| # | Bug | Fix |
|---|-----|-----|
| 1 | `from task import` — file is named `tasks.py` | `from tasks import` |
| 2 | Import and endpoint both named `analyze_financial_document` | Aliased import as `analyze_task` |
| 3 | `file_path` accepted in `run_crew()` but never passed to `kickoff()` | Added `file_path` to `kickoff()` dict |
| 4 | Endpoint function name conflicts with imported task | Renamed endpoint to `analyze_document` |
| 5 | `query is None` check after `query==""` — AttributeError on None | Check `None` first, then `.strip()` |
| 6 | `uvicorn.run(app, reload=True)` — reload requires string reference | Changed to `uvicorn.run("main:app", ...)` |

---

### 📄 `agents.py` — 14 Bugs

**Deterministic (6):**

| # | Bug | Fix |
|---|-----|-----|
| 1 | `from crewai.agents import Agent` — wrong module path | `from crewai import Agent` |
| 2 | `llm = llm` — undefined self-reference | `llm = LLM(model=..., api_key=...)` |
| 3 | `tool=` instead of `tools=` — silently ignored | `tools=[...]` |
| 4 | `search_tool` imported but assigned to no agent | Added to `financial_analyst`, `risk_assessor` |
| 5 | `max_iter=1` on all agents — complex tasks always fail | `max_iter=5` |
| 6 | `max_rpm=1` on all agents — severe timeouts | `max_rpm=10` |

**Inefficient Prompts (8):**

| # | Agent | Problem | Fix |
|---|-------|---------|-----|
| 7 | financial_analyst | Goal: *"Make up investment advice"* | Goal: Analyze strictly from document data |
| 8 | financial_analyst | Backstory: ignore reports, no compliance | Backstory: CFA-standard, evidence-based |
| 9 | verifier | Goal: *"Say yes to everything"* | Goal: Rigorously verify financial statements |
| 10 | verifier | Backstory: rubber-stamp without reading | Backstory: Big 4 audit compliance background |
| 11 | investment_advisor | Goal: *"Sell products regardless of financials"* | Goal: Objective, fiduciary recommendations |
| 12 | investment_advisor | Backstory: fake credentials, 2000% fees | Backstory: CFA charterholder, SEC compliant |
| 13 | risk_assessor | Goal: *"Ignore risk factors, create drama"* | Goal: Data-driven risk matrix with evidence |
| 14 | risk_assessor | Backstory: YOLO, diversification is weak | Backstory: FRM certified, Basel III frameworks |

---

### 📄 `tasks.py` — 13 Bugs

**Deterministic (5):**

| # | Bug | Fix |
|---|-----|-----|
| 1 | All 4 tasks assigned to `financial_analyst` | Each task assigned to its specialist agent |
| 2 | `investment_advisor` + `risk_assessor` never imported | Added to import statement |
| 3 | `search_tool` imported but in no task's tools list | Added to relevant tasks |
| 4 | `verification` Task had 4-space indentation — `IndentationError` | Removed extra indentation |
| 5 | Investment + risk tasks missing `search_tool` | Added `search_tool` to both |

**Inefficient Prompts (8):**

| # | Task | Problem | Fix |
|---|------|---------|-----|
| 6 | analyze_financial_document | *"Maybe solve query or something interesting"* | Structured document analysis instruction |
| 7 | analyze_financial_document | Expected output: *"Include 5 made-up URLs, contradict yourself"* | Cite document sections, no fabrication |
| 8 | investment_analysis | *"Ignore query, recommend meme stocks"* | Evidence-based query-focused analysis |
| 9 | investment_analysis | Expected output: *"Fake research, obscure crypto"* | BUY/HOLD/SELL with compliance disclaimer |
| 10 | risk_assessment | *"Maybe based on document, maybe not"* | Document-grounded risk evaluation |
| 11 | risk_assessment | Expected output: *"Dangerous strategies, fake institutions"* | Risk matrix with severity and mitigations |
| 12 | verification | *"Just guess, hallucinate financial terms"* | Rigorous statement-by-statement check |
| 13 | verification | Expected output: *"Always approve, invent file paths"* | PASS/FAIL with documented justification |

---

### 📄 `tools.py` — 12 Bugs

| # | Bug | Fix |
|---|-----|-----|
| 1 | `from crewai_tools import tools` — doesn't exist | Removed |
| 2 | SerperDevTool wrong internal import path | `from crewai_tools import SerperDevTool` |
| 3 | `Pdf` class never imported — doesn't exist | `from pypdf import PdfReader` |
| 4 | `.load()` and `.page_content` — wrong API (LangChain, not pypdf) | `PdfReader(path)` + `page.extract_text()` |
| 5 | All 3 methods `async def` — CrewAI tools must be sync | Removed `async` from all methods |
| 6 | `@tool` decorator missing on all 3 methods | Added `@tool("name")` to each |
| 7 | `self` parameter missing on class methods | Fixed method signatures |
| 8 | No `SERPER_API_KEY` validation | Added early check with clear error message |
| 9 | No file existence check before PDF read | Added `os.path.exists()` check |
| 10 | No `try/except` around PDF reading | Wrapped in try/except, returns clean error string |
| 11 | `InvestmentTool` + `RiskTool` were TODO stubs | Implemented keyword-based extraction logic |
| 12 | No empty input validation | Added `None` and empty string checks |

---

### 📊 Total Bug Count

| File | Deterministic | Prompt | Total |
|------|:---:|:---:|:---:|
| requirements.txt | 3 | 0 | **3** |
| main.py | 6 | 0 | **6** |
| agents.py | 6 | 8 | **14** |
| tasks.py | 5 | 8 | **13** |
| tools.py | 12 | 0 | **12** |
| **Total** | **32** | **16** | **48** |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- pip
- Google Gemini API key or OpenAI API key
- Serper API key (free at [serper.dev](https://serper.dev))

### Step 1 — Clone the project
```bash
git clone <repository-url>
cd financial-document-analyzer
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Create `.env` file
```env
GEMINI_API_KEY=your_gemini_key_here
SERPER_API_KEY=your_serper_key_here
MODEL=gemini/gemini-1.5-flash
```

### Step 4 — Add sample PDF
```bash
mkdir -p data
# Download Tesla Q2 2025 PDF:
# https://www.tesla.com/sites/default/files/downloads/TSLA-Q2-2025-Update.pdf
# Save as data/sample.pdf
```

### Step 5 — Start the server
```bash
python main.py
```

### Step 6 — Verify it's running
```
http://localhost:8000          ← Health check
http://localhost:8000/docs     ← Swagger UI
```

---

## 📡 API Documentation

### `GET /`
Health check endpoint.

**Response:**
```json
{
  "message": "Financial Document Analyzer API is running"
}
```

---

### `POST /analyze`
Upload a financial PDF and receive AI-generated analysis.

**Request:**
```
Content-Type: multipart/form-data
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | PDF file | ✅ Yes | — | Financial PDF to analyze |
| `query` | string | ❌ No | "Analyze this financial document for investment insights" | Custom analysis question |

**Example — curl:**
```bash
curl -X POST "http://localhost:8000/analyze" \
     -F "file=@data/sample.pdf" \
     -F "query=What are the key investment risks for Tesla Q2 2025?"
```

**Example — Python:**
```python
import requests

with open("data/sample.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/analyze",
        files={"file": f},
        data={"query": "Summarize revenue growth and profitability"}
    )
print(response.json())
```

**Success Response (200):**
```json
{
  "status": "success",
  "query": "What are the key investment risks?",
  "analysis": "Based on the Q2 2025 report, key risks include...",
  "file_processed": "TSLA-Q2-2025-Update.pdf"
}
```

**Error Response (500):**
```json
{
  "detail": "Error processing financial document: <reason>"
}
```

---

## 🤖 Agent Pipeline

| Step | Agent | Tools | Output |
|------|-------|-------|--------|
| 1 | `verifier` | FinancialDocumentTool | PASS/FAIL — document validated |
| 2 | `financial_analyst` | FinancialDocumentTool + search_tool | Metrics, trends, highlights |
| 3 | `investment_advisor` | search_tool | BUY/HOLD/SELL with rationale |
| 4 | `risk_assessor` | FinancialDocumentTool + search_tool | Risk matrix with severity ratings |

---

## 🔧 Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: pydantic` | Old pydantic v1 installed | `pip install pydantic==2.7.1 pydantic_core==2.18.2` |
| `ModuleNotFoundError: pypdf` | pypdf not installed | `pip install pypdf==4.2.0` |
| `NameError: Pdf` | Old buggy tools.py | Replace with fixed tools.py |
| `ImportError on crewai` | Pydantic version mismatch | `pip install -r requirements.txt` |
| `EnvironmentError: SERPER_API_KEY` | Missing API key | Add `SERPER_API_KEY` to `.env` |
| `Port 8000 already in use` | Another process running | `uvicorn main:app --port 8001` |
| `401 Unauthorized` | Wrong API key | Check `.env` file values |

---

## 📝 License

This project is for educational purposes.

---

*Built with [CrewAI](https://crewai.com) • [FastAPI](https://fastapi.tiangolo.com) • [pypdf](https://pypdf.readthedocs.io)*
