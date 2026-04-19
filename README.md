# Canonical Data Schema Alignment System

> AI-powered system that automatically maps messy, inconsistent CSV column names to a clean standardized schema — with human review for uncertain decisions.

---

## The Problem It Solves

Every company that works with data from multiple sources faces this:

| Source A | Source B | Source C | What it actually is |
|----------|----------|----------|---------------------|
| `cust_email` | `Email Address` | `contact` | → `email` |
| `mob` | `Phone No.` | `contact_number` | → `phone_number` |
| `DOB` | `date_birth` | `Birth Date` | → `date_of_birth` |

Mapping these manually is slow, error-prone, and doesn't scale.  
This system does it automatically — using AI inference, validation rules, and a human review queue for uncertain cases.

**Real-world use cases:** ETL pipelines, data warehouse ingestion, multi-vendor integrations, hospital/bank mergers, CRM data imports.

---

## How It Works

```
CSV File Input
      ↓
[Data Intake]       Extract column names + sample values
      ↓
[Prompt Builder]    Construct a bounded AI prompt
      ↓
[AI Mapper]         LLM infers column → canonical field mapping
      ↓
[Validator]         Check confidence scores + schema rules
      ↓
   ┌──┴──┐
[Accept]       [Review Queue]  ← uncertain mappings held for human decision
```

**Key design principle:** AI acts as a *recommender*, not an authority. Low-confidence or invalid mappings are never auto-accepted — they go to a human review queue with the reason for rejection.

---

## Demo

**Input CSV columns:**
```
Email Address | Contact | Country | Full Name
```

**System Output:**
```
Email Address  →  email         (confidence: 0.96)  ✅ Accepted
Contact        →  phone_number  (confidence: 0.92)  ✅ Accepted
Country        →  country       (confidence: 0.97)  ✅ Accepted
Full Name      →  first_name    (confidence: 0.65)  ❌ → Review Queue
                                          reason: ambiguous (first vs full name)
```

**API Response:**
```json
{
  "accepted": [
    { "source_column": "Email Address", "target_field": "email", "confidence": 0.96 },
    { "source_column": "Contact", "target_field": "phone_number", "confidence": 0.92 },
    { "source_column": "Country", "target_field": "country", "confidence": 0.97 }
  ],
  "review_item_ids": [1]
}
```

---

## Architecture

```
canonical-data-schema-alignment-system/
├── src/
│   ├── alignment_service.py   # Main orchestration — entry point for all integrations
│   ├── canonical_schema.py    # Defines the standard target fields
│   ├── data_intake.py         # CSV parsing and column sampling
│   ├── prompt_builder.py      # Constructs bounded prompts for the LLM
│   ├── ai_mapper.py           # LLM invocation with robust output parsing
│   ├── validator.py           # Validation rules (confidence, field validity)
│   ├── review_queue.py        # In-memory queue for human review decisions
│   └── mapping_contract.py    # Pydantic data models for type safety
├── mcp_server.py              # MCP protocol server (AI agent integration)
├── test_mcp_client.py         # Protocol compliance tests
└── README.md
```

**Design decisions:**
- **Pydantic models** for strict input/output contracts — no free-form dicts
- **Subprocess stdin=DEVNULL** — prevents I/O deadlocks when running under FastMCP stdio
- **Fallback mappings** — demo always produces meaningful output even when LLM is unavailable
- **In-memory ReviewQueue** — stateless by design; suitable for pipeline invocation

---

## Canonical Schema

Default target fields:

```
email · phone_number · country · full_name · company_name
street_address · city · state · postal_code · date_of_birth
```

Extend in `src/canonical_schema.py` — validator auto-updates.

---

## Quickstart

**Prerequisites:** Python 3.9+, OpenCode CLI

```bash
# Setup
git clone https://github.com/Vishwajeeet/Canonical-data-schema-alignment-system
cd canonical-data-schema-alignment-system
python -m venv venv && source venv/bin/activate
pip install fastmcp pydantic

# Run on a CSV
python -c "
from src.alignment_service import analyze_csv_schema
result = analyze_csv_schema('data/sample_contacts.csv')
for m in result['accepted']:
    print(f\"{m['source_column']} → {m['target_field']} ({m['confidence']:.2f})\")
print(f\"Queued for review: {result['review_item_ids']}\")
"
```

---

## MCP Integration

This system is MCP-compliant — it can be called directly by LLM agents (Claude, GPT with tools, etc.) without any manual API calls.

**Start the server:**
```bash
python mcp_server.py
```

**Tool exposed:** `analyze_csv_schema(csv_path: str)`

**MCP Handshake:**
```
Client  ──initialize──►  Server
        ◄──protocolVersion──
        ──tools/list──►
        ◄──[analyze_csv_schema]──
        ──tools/call──►
        ◄──{accepted, review_item_ids}──
```

**Test protocol compliance:**
```bash
python test_mcp_client.py
```

---

## Core Components

### `alignment_service.py` — Orchestration Layer
Central callable that coordinates all pipeline stages. Designed as a pure function so it can be safely invoked from MCP servers, REST APIs, or batch scripts without side effects.

### `ai_mapper.py` — LLM Integration
Calls the LLM with timeout protection (120s), handles mixed text+JSON output, and gracefully degrades when AI is unavailable. Uses `stdin=DEVNULL` to prevent subprocess deadlocks under FastMCP.

### `validator.py` — Rule Engine
Validates every mapping before acceptance: required fields present, confidence in [0.0, 1.0], target field exists in canonical schema. Returns structured failure reasons.

### `review_queue.py` — Human-in-the-Loop
O(1) in-memory store for uncertain mappings. Tracks status: `pending → approved / rejected`. Designed for demo/pipeline use — swap with a DB-backed store for production.

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| CSV not found | Returns `{"error": "..."}` with message |
| LLM timeout (120s) | Falls back to sample mappings, logs `[FALLBACK USED]` |
| Malformed LLM output | Extracts valid JSON array, skips corrupt items |
| Validation failure | Routes to review queue with failure reason |
| Subprocess I/O error | Gracefully degrades, fallback triggers |

---

## Performance

| Operation | Complexity |
|-----------|------------|
| CSV parsing | O(n) rows |
| LLM inference | ~14–15s (OpenCode dependent) |
| Validation | O(m) mappings |
| Review queue ops | O(1) — dict-backed |

---

## Known Limitations

- ReviewQueue is in-memory — data does not persist across restarts (by design for this version)
- CSV only — JSON/Excel ingestion not yet implemented
- LLM inference speed depends on local OpenCode availability
- Canonical schema requires manual extension

---

## Roadmap

- [ ] FastAPI REST layer (`POST /api/align`) for direct HTTP integration
- [ ] Persistent ReviewQueue with SQLite/PostgreSQL backend
- [ ] Streaming CSV support for large files (> RAM)
- [ ] Batch API — process multiple CSVs in one call
- [ ] Web UI for human review management

---

## Tech Stack

`Python 3.9+` · `FastMCP 3.2.4` · `Pydantic` · `OpenCode LLM` · `MCP Protocol 2024-11-05`

---

## Author

**Vishwajeet Mishra**  
B.Tech CSE (AI & ML) — Brainware University  
[GitHub](https://github.com/Vishwajeeet) · [Email](mailto:vishwajeet@example.com)