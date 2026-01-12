from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Rule:
    id: str
    domain: str
    variable: str
    condition: str
    severity: str
    message: str
    source: str = "core"


@dataclass(frozen=True)
class Violation:
    rule_id: str
    source: str
    domain: str
    variable: str
    severity: str
    message: str
    row_index: Optional[int]
    record_key: Optional[str]
    value: Optional[str]
    condition: str
