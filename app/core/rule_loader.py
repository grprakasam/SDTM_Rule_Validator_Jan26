import json
from pathlib import Path
from typing import List

from .rules import Rule


REQUIRED_FIELDS = {"id", "domain", "variable", "condition", "severity", "message"}


def load_rules(path: Path, source: str) -> List[Rule]:
    if not path.exists():
        return []

    data = json.loads(path.read_text(encoding="utf-8"))
    rules: List[Rule] = []
    for idx, item in enumerate(data):
        missing = REQUIRED_FIELDS - set(item.keys())
        if missing:
            raise ValueError(f"Rule at index {idx} missing fields: {sorted(missing)}")
        rules.append(
            Rule(
                id=str(item["id"]).strip(),
                domain=str(item["domain"]).strip().upper(),
                variable=str(item["variable"]).strip().upper(),
                condition=str(item["condition"]).strip(),
                severity=str(item["severity"]).strip().upper(),
                message=str(item["message"]).strip(),
                source=source,
            )
        )
    return rules


def save_rules(path: Path, rules: List[Rule]) -> None:
    payload = [
        {
            "id": rule.id,
            "domain": rule.domain,
            "variable": rule.variable,
            "condition": rule.condition,
            "severity": rule.severity,
            "message": rule.message,
        }
        for rule in rules
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
