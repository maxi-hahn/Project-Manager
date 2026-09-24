from pathlib import Path

DEFAULT_IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
}


def build_tree(root: Path, ignore_names: set[str] | None = None) -> dict:
    """
    Walk `root` recursively and return a tree node structure.
    Directories become {"type": "dir", "name": str, "children": dict}.
    Files become {"type": "file", "name": str}.
    Skip names present in `ignore_names`.
    Skip hidden-heavy dirs: .git, __pycache__, node_modules, .venv,
    venv, env, dist, build.
    Skip .gitkeep files.
    """
    if ignore_names is None:
        ignore_names = set()

    all_ignore = DEFAULT_IGNORE_DIRS | ignore_names

    if not root.exists() or not root.is_dir():
        return {"type": "dir", "name": root.name if root else "", "children": {}}

    children = {}
    try:
        entries = list(root.iterdir())
    except OSError:
        entries = []

    for entry in entries:
        name = entry.name
        if name in all_ignore:
            continue
        if name == ".gitkeep":
            continue

        if entry.is_dir():
            children[name] = build_tree(entry, ignore_names=ignore_names)
        elif entry.is_file():
            children[name] = {"type": "file", "name": name}

    return {"type": "dir", "name": root.name, "children": children}


def _copy_node(node: dict) -> dict:
    """Creates a deep copy of a tree node dictionary."""
    if node.get("type") == "file":
        return {"type": "file", "name": node["name"]}
    elif node.get("type") == "dir":
        new_children = {
            k: _copy_node(v) for k, v in node.get("children", {}).items()
        }
        return {
            "type": "dir",
            "name": node.get("name", ""),
            "children": new_children,
        }
    return {}


def merge_trees(base: dict, other: dict) -> dict:
    """
    Recursively merge two tree nodes.
    Directories with the same name are merged.
    Files with the same name keep the one from `base`.
    Return a NEW dict; do not modify the inputs.
    """
    if not base and not other:
        return {"type": "dir", "name": "", "children": {}}
    if not base:
        return _copy_node(other)
    if not other:
        return _copy_node(base)

    base_type = base.get("type")
    other_type = other.get("type")

    # If base is file, base wins
    if base_type == "file":
        return _copy_node(base)

    # If base is dir and other is file, base wins
    if base_type == "dir" and other_type == "file":
        return _copy_node(base)

    # Both are dirs
    merged_children = {}
    base_children = base.get("children", {})
    other_children = other.get("children", {})

    all_keys = set(base_children.keys()) | set(other_children.keys())

    for key in all_keys:
        if key in base_children and key in other_children:
            merged_children[key] = merge_trees(
                base_children[key], other_children[key]
            )
        elif key in base_children:
            merged_children[key] = _copy_node(base_children[key])
        else:
            merged_children[key] = _copy_node(other_children[key])

    return {
        "type": "dir",
        "name": base.get("name") or other.get("name", ""),
        "children": merged_children,
    }


def render_tree(tree: dict, root_name: str) -> str:
    """
    Render the tree as a string using Unicode box-drawing:
        ├──
        └──
        │
    Directories get a trailing "/".
    Order children: directories first (alphabetical), then files
    (alphabetical).
    Return a multi-line string.
    """
    lines = [f"{root_name}/"]

    def _render_children(node: dict, prefix: str):
        children_dict = node.get("children", {})
        dir_children = sorted(
            [c for c in children_dict.values() if c.get("type") == "dir"],
            key=lambda x: x["name"].lower(),
        )
        file_children = sorted(
            [c for c in children_dict.values() if c.get("type") == "file"],
            key=lambda x: x["name"].lower(),
        )
        ordered = dir_children + file_children

        total = len(ordered)
        for idx, child in enumerate(ordered):
            is_last = idx == total - 1
            connector = "└── " if is_last else "├── "
            child_name = child.get("name", "")

            if child.get("type") == "dir":
                lines.append(f"{prefix}{connector}{child_name}/")
                extension = "    " if is_last else "│   "
                _render_children(child, prefix + extension)
            else:
                lines.append(f"{prefix}{connector}{child_name}")

    if tree and tree.get("type") == "dir":
        _render_children(tree, "")

    return "\n".join(lines)
