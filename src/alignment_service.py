from src.data_intake import extract_column_samples
from src.prompt_builder import build_schema_mapping_prompt
from src.ai_mapper import call_ai, parse_and_validate


def analyze_csv_schema(csv_path: str):
    """
    Application Service Layer:
    Orchestrates schema alignment pipeline.

    This function is MCP-safe:
    - No CLI logic
    - No prints
    - Returns structured result
    """

    # Step 1: Extract representative samples
    column_samples = extract_column_samples(csv_path)

    # Step 2: Build bounded prompt
    prompt = build_schema_mapping_prompt(column_samples)

    raw_ai_output = call_ai(prompt)

    validated_mappings = parse_and_validate(raw_ai_output)

    return validated_mappings

