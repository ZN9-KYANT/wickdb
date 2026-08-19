"""
Pattern loader — discovers and loads YAML pattern files from the patterns/ directory.
"""

from pathlib import Path
from typing import Optional

import yaml


def load_patterns(patterns_dir: Optional[str] = None) -> list[dict]:
    """
    Load all pattern YAML files from the patterns directory.

    Args:
        patterns_dir: Path to patterns directory. Defaults to the bundled patterns/.

    Returns:
        List of pattern dictionaries.
    """
    if patterns_dir is None:
        # Default to the patterns directory bundled with the package
        root = Path(__file__).resolve().parent.parent.parent
        patterns_dir = root / "patterns"

    patterns_path = Path(patterns_dir)
    if not patterns_path.exists():
        raise FileNotFoundError(f"Patterns directory not found: {patterns_path}")

    patterns = []
    for yaml_file in sorted(patterns_path.rglob("*.yaml")):
        with open(yaml_file, "r", encoding="utf-8") as f:
            pattern = yaml.safe_load(f)
            if pattern and "id" in pattern:
                pattern["_file"] = str(yaml_file.relative_to(patterns_path))
                patterns.append(pattern)

    return patterns


def load_pattern(pattern_id: str, patterns_dir: Optional[str] = None) -> Optional[dict]:
    """
    Load a single pattern by ID.

    Args:
        pattern_id: The pattern ID (e.g. "morning_star").
        patterns_dir: Path to patterns directory.

    Returns:
        Pattern dictionary or None if not found.
    """
    patterns = load_patterns(patterns_dir)
    for p in patterns:
        if p.get("id") == pattern_id:
            return p
    return None