import pytest
from src.logic.validators import validate_project_name, validate_required_field


def test_validate_project_name_valid():
    is_valid, msg = validate_project_name("my_cool_project")
    assert is_valid is True
    assert msg == ""


def test_validate_project_name_empty():
    is_valid, msg = validate_project_name("")
    assert is_valid is False
    assert msg == "El nombre del proyecto no puede estar vacío."

    is_valid_space, msg_space = validate_project_name("   ")
    assert is_valid_space is False
    assert msg_space == "El nombre del proyecto no puede estar vacío."


def test_validate_project_name_invalid_characters():
    invalid_names = ["my:project", "proj<ect>", 'proj"ect', "proj/ect", "proj\\ect", "proj|ect", "proj?ect", "proj*ect"]
    for name in invalid_names:
        is_valid, msg = validate_project_name(name)
        assert is_valid is False
        assert msg == "El nombre contiene caracteres no válidos."


def test_validate_required_field_valid():
    is_valid, msg = validate_required_field("Some description")
    assert is_valid is True
    assert msg == ""


def test_validate_required_field_empty():
    is_valid, msg = validate_required_field("")
    assert is_valid is False
    assert msg == "Este campo no puede estar vacío."

    is_valid_spaces, msg_spaces = validate_required_field("   ")
    assert is_valid_spaces is False
    assert msg_spaces == "Este campo no puede estar vacío."


def test_validate_required_field_custom_error_message():
    custom_msg = "La descripción no puede estar vacía."
    is_valid, msg = validate_required_field("", error_message=custom_msg)
    assert is_valid is False
    assert msg == custom_msg
