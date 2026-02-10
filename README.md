# Canonical Data Schema Alignment System

An AI-assisted, production-oriented schema alignment engine that analyzes
heterogeneous CSV datasets and produces validated, confidence-scored mappings
against a predefined canonical schema.

The system is designed to assist safe downstream data ingestion by treating
LLM outputs as *suggestions*, not authority, and enforcing deterministic
validation rules before any automation is allowed.

---

## Problem Context

In real-world data pipelines, incoming datasets from vendors, partners, or
legacy systems rarely follow consistent naming conventions or structures.

Examples:
- `Email`, `Email Address`, `User Mail`
- `Phone`, `Contact`, `Mobile No`
- `Country`, `Nation`, `Location`

Manual schema mapping is slow, error-prone, and does not scale.  
Blindly trusting LLM-based mappings introduces a high risk of silent data
corruption.

---

## Solution Overview

This system implements a **schema alignment decision engine** that:

- Extracts representative samples from raw CSV data
- Uses constrained LLM reasoning to suggest semantic mappings
- Enforces strict schema contracts on AI outputs
- Applies confidence-based deterministic validation
- Accepts only high-confidence, schema-safe mappings
- Flags ambiguous cases for manual review

The system **does not write to databases**.  
It produces *validated alignment decisions* to enable safe downstream actions.

---

## System Architecture

The schema alignment pipeline follows a deterministic, staged flow:

1. **CSV Input**
2. **Column Sample Extraction**
3. **Bounded Prompt Construction**
4. **LLM Mapping Suggestions**
5. **Contract Enforcement (Pydantic)**
6. **Confidence-Based Validation**
7. **Accepted / Rejected Mappings**



---

## Key Design Principles

- **AI as a recommender, not an authority**
- **Strict contracts over free-form outputs**
- **Deterministic validation over probabilistic trust**
- **Separation of decision logic from execution**
- **Explainability and auditability by design**


---

## End-to-End Demo

## End-to-End Demo

### Input CSV
Email Address, Contact, Country, Full Name

### System Output
Email Address → email        (confidence: 0.96)  ✓
Contact       → phone_number (confidence: 0.92)  ✓
Country       → country      (confidence: 0.97)  ✓
Full Name     → first_name   (confidence: 0.65)  ✗  (rejected: ambiguous)

Only high-confidence, schema-safe mappings are accepted.
Ambiguous mappings are explicitly rejected for manual review.


---

## Project Scope

### What this system does
- Produces validated schema alignment decisions
- Prevents low-confidence or invalid mappings
- Handles real-world LLM integration issues (streaming output, model failures)

### What this system does NOT do
- Modify CSV files
- Write to production databases
- Execute data transformations

Downstream systems are expected to apply accepted mappings with appropriate
human or automated approval workflows.

---

## Project Status

Core schema alignment engine completed.

Planned next phase:
- MCP server layer to expose the engine as callable tools
- Human review workflows for rejected mappings
- Extended field decomposition (e.g., full name splitting)

