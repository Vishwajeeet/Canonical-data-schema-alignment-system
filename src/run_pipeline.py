from data_intake import extract_column_samples
from prompt_builder import build_schema_mapping_prompt


def main():
    csv_path = "data/sample_contacts.csv"

    column_samples = extract_column_samples(csv_path)
    print("=== COLUMN SAMPLES ===")
    print(column_samples)

    prompt = build_schema_mapping_prompt(column_samples)
    print("\n=== GENERATED PROMPT ===")
    print(prompt)


if __name__ == "__main__":
    main()
