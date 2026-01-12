from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

from app.core.rule_loader import load_rules, save_rules
from app.core.rules import Rule


PROJECTS_ROOT = Path("projects")


def sanitize_project_name(name: str) -> str:
    cleaned = "".join(ch for ch in name.strip() if ch.isalnum() or ch in ("-", "_"))
    return cleaned or "default"


def project_path(project_name: str) -> Path:
    return PROJECTS_ROOT / sanitize_project_name(project_name)


def custom_rules_path(project_name: str) -> Path:
    return project_path(project_name) / "custom_rules.json"


def load_custom_rules(project_name: str) -> List[Rule]:
    path = custom_rules_path(project_name)
    return load_rules(path, source="custom")


def save_custom_rules(project_name: str, rules: List[Rule]) -> None:
    path = custom_rules_path(project_name)
    save_rules(path, rules)


def new_run_folder(project_name: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = project_path(project_name) / "runs" / timestamp
    path.mkdir(parents=True, exist_ok=True)
    return path
