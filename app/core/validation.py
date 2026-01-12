from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from .rule_engine import run_rules
from .rule_loader import load_rules
from .rules import Rule, Violation


def load_all_rules(core_rules_path: Path, custom_rules_path: Path) -> Tuple[List[Rule], List[str]]:
    core_rules = load_rules(core_rules_path, source="core")
    custom_rules = load_rules(custom_rules_path, source="custom")
    all_rules = core_rules + custom_rules
    order = [rule.id for rule in all_rules]
    return all_rules, order


def run_validation(
    domain_tables: Dict[str, pd.DataFrame],
    core_rules_path: Path,
    custom_rules_path: Path,
) -> Tuple[List[Violation], List[str]]:
    rules, order = load_all_rules(core_rules_path, custom_rules_path)
    violations = run_rules(domain_tables, rules)
    return violations, order
