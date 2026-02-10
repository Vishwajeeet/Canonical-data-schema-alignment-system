import json
import subprocess
from typing import List

from mapping_contract import SchemaMapping
from validator import validate_mapping


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



def parse_and_validate(ai_output: str) -> List[SchemaMapping]:
    mappings = []

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
            return mappings

        data = json.loads(json_text)

        for item in data:
            mapping = SchemaMapping(**item)
            if validate_mapping(mapping):
                mappings.append(mapping)

    except Exception as e:
        print("Failed to parse AI output:", e)

    return mappings

