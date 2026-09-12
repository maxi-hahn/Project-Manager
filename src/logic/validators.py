# ============================================================
# VALIDATION LOGIC
# ============================================================
# Pure functions for validating user inputs such as project
# names and required text fields.
# ============================================================


def validate_project_name(name: str) -> tuple[bool, str]:
    """Validate a project name to ensure it is non-empty and contains valid characters."""
    stripped_name = name.strip() if name else ""

    if not stripped_name:
        return False, "El nombre del proyecto no puede estar vacío."

    invalid_chars = '<>:"/\\|?*'
    if any(character in stripped_name for character in invalid_chars):
        return False, "El nombre contiene caracteres no válidos."

    return True, ""


def validate_required_field(
    value: str, error_message: str = "Este campo no puede estar vacío."
) -> tuple[bool, str]:
    """Validate that a required text field is not empty after stripping whitespace."""
    stripped_value = value.strip() if value else ""

    if not stripped_value:
        return False, error_message

    return True, ""
