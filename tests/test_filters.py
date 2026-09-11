import pytest
from src.logic.filters import (
    filter_features_by_template,
    filter_environments_by_template,
    filter_tools_by_language,
)


def test_filter_features_by_template():
    template = {"name": "Python Basic"}
    features = [
        {"name": "f1", "compatible_with": ["python_basic", "fastapi"]},
        {"name": "f2", "compatible_with": ["express"]},
        {"name": "f3"},
    ]
    result = filter_features_by_template(features, template)
    assert len(result) == 1
    assert result[0]["name"] == "f1"


def test_filter_environments_by_template():
    template = {"name": "Node Express"}
    environments = [
        {"name": "env1", "compatible_with": ["node_express"]},
        {"name": "env2", "compatible_with": ["python_basic"]},
    ]
    result = filter_environments_by_template(environments, template)
    assert len(result) == 1
    assert result[0]["name"] == "env1"


def test_filter_tools_by_language():
    tools = [
        {"name": "pytest", "language": "Python"},
        {"name": "jest", "language": "JavaScript"},
        {"name": "ruff", "language": "python"},
        {"name": "no_lang"},
    ]
    result = filter_tools_by_language(tools, "python")
    assert len(result) == 2
    assert [t["name"] for t in result] == ["pytest", "ruff"]
