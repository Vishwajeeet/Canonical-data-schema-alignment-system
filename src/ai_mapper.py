import json
import subprocess
from typing import List, Dict, TypedDict

from src.mapping_contract import SchemaMapping
from src.validator import validate_mapping


class ReviewItem(TypedDict):
    """Represents a mapping that needs human review with its validation reason."""
    mapping: SchemaMapping
    reason: str


class ValidationResult(TypedDict):
    """Result of parsing and validating AI-generated schema mappings."""
    accepted: List[SchemaMapping]
    needs_review: List[ReviewItem]


def call_ai(prompt: str) -> str:
    result = subprocess.run(
        [
            "opencode",
            "run",
            "-m",
            "opencode/gpt-5-nano",
            "--thinking", "false",
            "--format", "json",
            prompt,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.stderr:
        print("\n=== AI STDERR ===")
        print(result.stderr)

    return result.stdout



def parse_and_validate(ai_output: str) -> ValidationResult:
    """
    Parse AI output and categorize mappings by validation status.
    
    Returns:
        ValidationResult dict with keys:
        - "accepted": mappings that pass all validation checks
        - "needs_review": mappings that fail validation with reasons (preserved for audit)
    """
    result = {
        "accepted": [],
        "needs_review": []
    }

    try:
        # Split event-stream lines
        lines = ai_output.splitlines()

        json_text = None
        for line in lines:
            if '"type":"text"' in line and '"text"' in line:
                event = json.loads(line)
                json_text = event["part"]["text"]
                break

        if not json_text:
            print("No JSON payload found in AI output")
            return result

        data = json.loads(json_text)

        for item in data:
            mapping = SchemaMapping(**item)
            is_valid, reason = validate_mapping(mapping)
            
            if is_valid:
                result["accepted"].append(mapping)
            else:
                # Wrap failed mapping with validation reason
                result["needs_review"].append({
                    "mapping": mapping,
                    "reason": reason
                })

    except Exception as e:
        print("Failed to parse AI output:", e)

    return result

