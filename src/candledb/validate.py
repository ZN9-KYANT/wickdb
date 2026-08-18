"""
Schema validation — validates pattern YAML files against the JSON Schema.
"""

import json
from pathlib import Path
from typing import Optional

try:
    import jsonschema
except ImportError:
    jsonschema = None


def _load_schema() -> dict:
    """Load the pattern JSON Schema."""
    root = Path(__file__).resolve().parent.parent.parent
    schema_path = root / "schemas" / "pattern.schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_pattern(pattern: dict, schema: Optional[dict] = None) -> tuple[bool, list[str]]:
    """
    Validate a pattern dictionary against the JSON Schema.

    Args:
        pattern: Pattern dictionary to validate.
        schema: Optional schema dict. Loads from file if not provided.

    Returns:
        Tuple of (is_valid, list_of_errors).
    """
    if jsonschema is None:
        raise ImportError(
            "jsonschema is required for validation. Install with: pip install jsonschema"
        )

    if schema is None:
        schema = _load_schema()

    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(pattern), key=lambda e: e.path)

    if not errors:
        return True, []

    error_messages = []
    for err in errors:
        path = ".".join(str(p) for p in err.absolute_path) or "(root)"
        error_messages.append(f"{path}: {err.message}")

    return False, error_messages


def validate_all(patterns_dir: Optional[str] = None) -> dict:
    """
    Validate all pattern files in a directory.

    Args:
        patterns_dir: Path to patterns directory.

    Returns:
        Dict with "valid" and "invalid" lists.
    """
    from candledb.loader import load_patterns

    patterns = load_patterns(patterns_dir)
    results = {"valid": [], "invalid": []}

    for pattern in patterns:
        # Strip internal fields before validation
        p = {k: v for k, v in pattern.items() if not k.startswith("_")}
        is_valid, errors = validate_pattern(p)
        if is_valid:
            results["valid"].append(pattern["id"])
        else:
            results["invalid"].append({"id": pattern["id"], "errors": errors})

    return results