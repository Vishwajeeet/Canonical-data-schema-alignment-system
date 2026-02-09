def validate_mapping(mapping) -> bool:
    allowed_fields = {
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "country",
    }

    if mapping.confidence < 0.85:
        return False

    if mapping.target_field not in allowed_fields:
        return False

    return True
