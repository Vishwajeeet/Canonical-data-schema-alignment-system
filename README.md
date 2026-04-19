# Canonical Data Schema Alignment System

> AI-powered backend that automatically maps messy, inconsistent CSV column names to a clean standardized schema — using Google Gemini for inference, with confidence scoring, validation rules, and a human review queue for uncertain decisions.

**🔴 Live API →** `https://canonical-data-schema-alignment-system.onrender.com`   
**📖 Interactive Docs →** `https://canonical-data-schema-alignment-system.onrender.com/docs`

---

## The Problem It Solves

Every company that works with data from multiple sources faces this:

| Source A | Source B | Source C | What it actually is |
|----------|----------|----------|---------------------|
| `cust_email` | `Email Address` | `e_mail` | → `email` |
| `mob_no` | `Phone No.` | `contact_number` | → `phone_number` |
| `DOB` | `date_birth` | `Birth Date` | → `date_of_birth` |

Mapping these manually is slow, error-prone, and doesn't scale.  
This system does it automatically — AI infers the mapping, a validation layer enforces rules, and uncertain decisions go to a human review queue instead of being auto-accepted.

**Real-world use cases:** ETL pipelines · data warehouse ingestion · multi-vendor integrations · hospital/bank mergers · CRM data imports

---

## Live Demo

No setup needed. Open the interactive docs and test directly in browser:

**`https://canonical-data-schema-alignment-system.onrender.com/docs`**

1. Click `POST /api/align` → `Try it out`
2. Upload any CSV file
3. Hit `Execute` — see the mappings instantly

**Sample input:**
```
Email Address,Contact,Country,Full Name,DOB
john@gmail.com,9876543210,India,John Doe,1995-04-12
```

**Response:**
```json
{
  "accepted": [
    { "source_column": "Email Address", "target_field": "email",        "confidence": 0.96 },
    { "source_column": "Contact",       "target_field": "phone_number", "confidence": 0.92 },
    { "source_column": "Country",       "target_field": "country",      "confidence": 0.97 }
  ],
  "review_item_ids": [1, 2]
}
```

`Full Name` and `DOB` → routed to review queue. AI was below confidence threshold — system never auto-accepts uncertain mappings.

---

## Architecture

```
POST /api/align  (CSV upload)
        │
        ▼
    api.py                   FastAPI layer — handles upload, temp file, HTTP
        │
        ▼
alignment_service.py         Orchestrator — runs the full pipeline
        │
   ┌────┼──────────────────┐
   ▼    ▼                  ▼
data_intake.py    prompt_builder.py    ai_mapper.py
(parse CSV)       (build prompt)       (call Gemini API → parse JSON)
                                            │
                                      validator.py
                                      (confidence + schema check)
                                            │
                                  ┌─────────┴──────────┐
                                  ▼                    ▼
                               ACCEPT              REJECT
                                                      │
                                              review_queue.py
                                              (in-memory, pending human decision)
```

**Core design principle:** AI is a *recommender*, not an authority. No mapping is auto-applied without passing validation. Low-confidence decisions are explicitly held for human review — never silently accepted.

**What this system does NOT do:** It does not modify CSV files or write to any database. It produces validated mapping decisions. Downstream pipelines consume these decisions to execute the actual transformation. This separation is intentional — it makes the system safe, testable, and DB-agnostic.

---

## API Reference

### `GET /`
Health check.
```json
{ "status": "ok", "service": "canonical-alignment-api" }
```

### `POST /api/align`
Analyze a CSV file and return schema mappings.

**Request:** `multipart/form-data`, field name: `file`

**cURL:**
```bash
curl -X POST https://canonical-data-schema-alignment-system.onrender.com/api/align \
  -F "file=@your_file.csv"
```

**Success response `200`:**
```json
{
  "accepted": [
    {
      "source_column": "Email Address",
      "target_field": "email",
      "confidence": 0.96,
      "reasoning": "Contains @ symbol, matches email pattern"
    }
  ],
  "review_item_ids": [1, 2]
}
```

**Error response `500`:**
```json
{ "detail": { "error": "description of what failed" } }
```

### `GET /docs`
Swagger UI — test all endpoints in browser, no Postman needed.

---

## Project Structure

```
canonical-data-schema-alignment-system/
├── api.py                     ← FastAPI REST layer (entry point for HTTP)
├── mcp_server.py              ← MCP protocol server (AI agent integration)
├── requirements.txt
├── .gitignore
├── data/
│   └── sample_contacts.csv   ← Demo dataset
└── src/
    ├── alignment_service.py   ← Main orchestrator
    ├── canonical_schema.py    ← Hardcoded standard target fields
    ├── data_intake.py         ← CSV parsing + column sampling
    ├── prompt_builder.py      ← Constructs bounded prompts for Gemini
    ├── ai_mapper.py           ← Gemini API call + JSON extraction
    ├── validator.py           ← Confidence + schema validation rules
    ├── review_queue.py        ← In-memory human review queue
    └── mapping_contract.py    ← Pydantic models for type safety
```

---

## Canonical Schema

Standard target fields (defined in `src/canonical_schema.py`):

```
email · phone_number · country · full_name · company_name
street_address · city · state · postal_code · date_of_birth
```

Edit this file to extend — validator auto-updates, no other changes needed.

---

## Quickstart (Local)

```bash
git clone https://github.com/Vishwajeeet/Canonical-data-schema-alignment-system
cd canonical-data-schema-alignment-system

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Set your Gemini API key
export GEMINI_API_KEY=your_key_here   # Windows: set GEMINI_API_KEY=your_key_here

# Start the API server
python api.py
# → Running on http://localhost:8001
# → Swagger UI: http://localhost:8001/docs
```

**Test with cURL:**
```bash
curl -X POST http://localhost:8001/api/align \
  -F "file=@data/sample_contacts.csv"
```

**MCP server (for AI agent integration):**
```bash
python mcp_server.py
```

---

## Key Design Decisions

**Separation of decision from execution** — The system produces mapping recommendations, not database writes. This is intentional: AI decisions go through human review before any downstream system acts on them.

**Human-in-the-loop by default** — Below-threshold confidence = review queue, not auto-accept. This is a safer architecture than trusting AI outputs blindly.

**Graceful degradation** — If Gemini API fails or times out, fallback mappings are returned. The pipeline never crashes.

**Pydantic throughout** — Every input/output has a strict type contract via Pydantic models. No free-form dicts in the pipeline.

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| CSV not found | HTTP 500 with error message |
| Gemini API timeout | Fallback mappings, logs `[FALLBACK USED]` |
| Malformed AI output | Extracts valid JSON, skips corrupt items |
| Validation failure | Routes to review queue with reason |
| Temp file cleanup failure | Silently ignored — does not affect response |

---

## MCP Integration

This system also exposes an MCP (Model Context Protocol) server, allowing AI agents like Claude to call the alignment function as a tool — without any HTTP calls.

```bash
python mcp_server.py
```

**Tool exposed:** `analyze_csv_schema(csv_path: str)`  
**Protocol:** MCP 2024-11-05 via FastMCP 3.2.4

---

## Roadmap

- [ ] Persistent ReviewQueue with SQLite/PostgreSQL backend
- [ ] `POST /api/review/{id}/approve` and `/reject` endpoints
- [ ] Batch mode — process multiple CSVs in one request
- [ ] JSON and Excel (.xlsx) input support
- [ ] Configurable confidence threshold via environment variable

---

## Tech Stack

`Python 3.9+` · `FastAPI` · `Uvicorn` · `Google Gemini API` · `FastMCP 3.2.4` · `Pydantic` · `MCP Protocol 2024-11-05`

---

## Author

**Vishwajeet Mishra**  
[GitHub](https://github.com/Vishwajeeet)