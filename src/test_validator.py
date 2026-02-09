from mapping_contract import SchemaMapping
from validator import validate_mapping

def run_test():
    good_mapping = SchemaMapping(
        source_column = "Email Address",
        target_field = "email",
        confidence = 0.92,
        reasoning = "Column values look like valid email addresses",
    )

    low_confidence_mapping = SchemaMapping(
        source_column="Contact",
        target_field="email",
        confidence=0.60,
        reasoning="Mixed phone numbers and emails",
    )
    
    invalid_field_mapping = SchemaMapping(
        source_column="User Mail",
        target_field="user_email",
        confidence=0.95,
        reasoning="Looks like an email field",
    )

    print("Good mapping accepted:", validate_mapping(good_mapping))
    print("Low confidence accepted:", validate_mapping(low_confidence_mapping))
    print("Invalid field accepted:", validate_mapping(invalid_field_mapping))


if __name__ == "__main__":
    run_test()