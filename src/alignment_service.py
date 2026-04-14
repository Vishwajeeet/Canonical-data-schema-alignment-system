from src.data_intake import extract_column_samples
from src.prompt_builder import build_schema_mapping_prompt
from src.ai_mapper import call_ai, parse_and_validate


def analyze_csv_schema(csv_path: str) -> dict:
    """
    Application Service Layer:
    Orchestrates schema alignment pipeline.

    Returns JSON-serializable dict with:
    - "accepted": List of mapping dicts that passed validation
    - "needs_review": List of {mapping, reason} dicts that need review

    This function is MCP-safe:
    - No CLI logic
    - No prints
    - Returns fully serializable structure
    """

    # Step 1: Extract representative samples
    column_samples = extract_column_samples(csv_path)

    # Step 2: Build bounded prompt
    prompt = build_schema_mapping_prompt(column_samples)

    raw_ai_output = call_ai(prompt)

    # Step 3: Parse and categorize mappings
    validated_result = parse_and_validate(raw_ai_output)

    # Step 4: Convert to JSON-serializable format
    return {
        "accepted": [m.model_dump() for m in validated_result["accepted"]],
        "needs_review": [
            {
                "mapping": item["mapping"].model_dump(),
                "reason": item["reason"]
            }
            for item in validated_result["needs_review"]
        ]
    }

