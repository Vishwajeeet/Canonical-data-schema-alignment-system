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
    try:
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
            stdin=subprocess.DEVNULL,  # Explicitly close stdin
        )
        return result.stdout
    except FileNotFoundError:
        return "[]"
    except subprocess.TimeoutExpired:
        return "[]"
    except Exception:
        return "[]"



def parse_and_validate(ai_output: str) -> ValidationResult:
    result = {
        "accepted": [],
        "needs_review": []
    }

    try:
        # Extract first JSON array from output
        start_idx = ai_output.find('[')
        if start_idx == -1:
            return result
        
        end_idx = ai_output.rfind(']')
        if end_idx == -1 or end_idx <= start_idx:
            return result
        
        json_str = ai_output[start_idx:end_idx + 1]
        data = json.loads(json_str)
        
        if not isinstance(data, list):
            return result

        for item in data:
            try:
                mapping = SchemaMapping(**item)
                is_valid, reason = validate_mapping(mapping)
                
                if is_valid:
                    result["accepted"].append(mapping)
                else:
                    result["needs_review"].append({
                        "mapping": mapping,
                        "reason": reason
                    })
            except Exception:
                continue

    except Exception:
        pass

    return result

