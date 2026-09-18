# ============================================================
# FILTERING LOGIC
# ============================================================
# Pure logic functions for filtering resources (features,
# environments, tools) based on templates or attributes.
# ============================================================


def filter_features_by_template(features: list[dict], template: dict) -> list[dict]:
    # Normalize template name: lowercase, spaces and hyphens to underscores
    template_id = (
        template["name"]
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )
    return [
        f for f in features
        if template_id in f.get("compatible_with", [])
    ]

def filter_environments_by_template(
    environments: list[dict], template: dict
) -> list[dict]:
    """Filter environments whose compatible_with list includes the template identifier."""
    template_id = template["name"].lower().replace(" ", "_")
    return [
        env
        for env in environments
        if template_id in env.get("compatible_with", [])
    ]


def filter_tools_by_language(tools: list[dict], language: str) -> list[dict]:
    """Filter tools whose language field matches the given language (case-insensitive)."""
    target_lang = language.lower()
    return [
        tool
        for tool in tools
        if tool.get("language", "").lower() == target_lang
    ]
