from data_intake import extract_column_samples
from prompt_builder import build_schema_mapping_prompt
from ai_mapper import call_ai, parse_and_validate


def main():
    csv_path = "data/sample_contacts.csv"

    # 1) Read data & extract samples
    column_samples = extract_column_samples(csv_path)

    # 2) Build bounded prompt
    prompt = build_schema_mapping_prompt(column_samples)

    # 3) Call AI (headless)
    ai_output = call_ai(prompt)
    print("\n=== RAW AI OUTPUT ===")
    print(ai_output)

    # 4) Parse, contract-enforce, validate
    safe_mappings = parse_and_validate(ai_output)

    # 5) Final result
    print("\n=== ACCEPTED MAPPINGS ===")
    for m in safe_mappings:
        print(m.model_dump())


if __name__ == "__main__":
    main()
