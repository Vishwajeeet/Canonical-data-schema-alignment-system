def validate_mapping(mapping) -> tuple[bool, str]:
    """
    Validate a schema mapping.
    
    Returns:
        Tuple of (is_valid, reason).
        is_valid: True if mapping passes all checks.
        reason: Explanation of why validation failed (empty string if valid).
    """
    allowed_fields = {
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "country",
    }

    if mapping.confidence < 0.85:
        return False, f"Low confidence ({mapping.confidence})"

    if mapping.target_field not in allowed_fields:
        return False, f"Invalid target field: {mapping.target_field}"

    return True, ""
