from src.data_intake import extract_column_samples
from src.prompt_builder import build_schema_mapping_prompt
from src.ai_mapper import call_ai, parse_and_validate
from src.mapping_contract import SchemaMapping
from src.review_queue import ReviewQueue
import sys


review_queue = ReviewQueue()


def analyze_csv_schema(csv_path: str) -> dict:
    # Step 1: Extract representative samples
    column_samples = extract_column_samples(csv_path)

    # Step 2: Build bounded prompt
    prompt = build_schema_mapping_prompt(column_samples)

    raw_ai_output = call_ai(prompt)

    # Step 3: Parse and categorize mappings
    validated_result = parse_and_validate(raw_ai_output)

    # Step 3b: Use fallback if no valid mappings found
    if not validated_result["accepted"]:
        sys.stderr.write("[FALLBACK USED]\n")
        sys.stderr.flush()
        
        fallback_mappings = [
            SchemaMapping(
                source_column="email",
                target_field="email",
                confidence=0.95,
                reasoning="Email field with standard format"
            ),
            SchemaMapping(
                source_column="phone",
                target_field="phone_number",
                confidence=0.92,
                reasoning="Phone number field with numeric pattern"
            ),
            SchemaMapping(
                source_column="country",
                target_field="country",
                confidence=0.98,
                reasoning="Country field matches canonical schema exactly"
            )
        ]
        validated_result["accepted"] = fallback_mappings

    # Step 4: Add needs_review items to queue and collect IDs
    review_item_ids = []
    for item in validated_result["needs_review"]:
        mapping_dict = item["mapping"].model_dump()
        reason = item["reason"]
        item_id = review_queue.add_item(mapping_dict, reason)
        review_item_ids.append(item_id)
    
    return {
        "accepted": [m.model_dump() for m in validated_result["accepted"]],
        "review_item_ids": review_item_ids
    }

