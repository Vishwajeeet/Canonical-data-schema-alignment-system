from typing import Dict, List
from canonical_schema import CanonicalSchema


def build_schema_mapping_prompt(
    column_samples: Dict[str, List[str]]
) -> str:
    canonical_fields = list(CanonicalSchema.__annotations__.keys())

    prompt = f"""
You are an AI assistant helping map input dataset columns to a canonical schema.

Canonical schema fields (choose ONLY from these):
{canonical_fields}

For EACH input column below:
- Suggest exactly ONE target_field from the canonical schema
- Provide a confidence score between 0 and 1
- Give a short reasoning

Return ONLY valid JSON in the following format (no extra text):

{{
  "source_column": "<column name>",
  "target_field": "<one canonical field>",
  "confidence": <number between 0 and 1>,
  "reasoning": "<short explanation>"
}}

Input columns and sample values:
"""

    for column, samples in column_samples.items():
        prompt += f"\nColumn: {column}\nSamples: {samples}\n"

    return prompt
