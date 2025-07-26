from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback
    yaml = None


def load_config(path: str | Path) -> Dict[str, Any]:
    """Load a YAML configuration file.

    If PyYAML is not available, a very naive parser is used which supports a
    subset of YAML used in this project.
    """
    text = Path(path).read_text(encoding="utf-8")
    if yaml:
        return yaml.safe_load(text)
    return _minimal_yaml_parse(text)


def _minimal_yaml_parse(text: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    current_dict = data
    stack = []
    prev_indent = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        key, value = [s.strip() for s in line.split(':', 1)]
        if value == "":
            new_dict: Dict[str, Any] = {}
            if indent > prev_indent:
                stack.append(current_dict)
                current_dict[key] = new_dict
                current_dict = new_dict
            else:
                while stack and indent < prev_indent:
                    current_dict = stack.pop()
                    prev_indent -= 2
                current_dict[key] = new_dict
                current_dict = new_dict
        else:
            if indent > prev_indent:
                stack.append(current_dict)
                prev_indent = indent
            elif indent < prev_indent:
                while stack and indent < prev_indent:
                    current_dict = stack.pop()
                    prev_indent -= 2
            current_dict[key] = _parse_value(value)
    return data


def _parse_value(value: str) -> Any:
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        return value
