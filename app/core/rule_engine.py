from typing import Dict, Iterable, List

import pandas as pd

from .rule_parser import build_mask
from .rules import Rule, Violation


def _get_record_key(row: pd.Series) -> str | None:
    for key in ["USUBJID", "SUBJID", "STUDYID"]:
        if key in row.index and pd.notna(row[key]):
            return str(row[key])
    return None


def _missing_domain_violation(rule: Rule) -> Violation:
    return Violation(
        rule_id=rule.id,
        source=rule.source,
        domain=rule.domain,
        variable=rule.variable,
        severity=rule.severity,
        message=f"Domain {rule.domain} not found",
        row_index=None,
        record_key=None,
        value=None,
        condition=rule.condition,
    )


def _missing_variable_violation(rule: Rule) -> Violation:
    return Violation(
        rule_id=rule.id,
        source=rule.source,
        domain=rule.domain,
        variable=rule.variable,
        severity=rule.severity,
        message=f"Variable {rule.variable} not found in {rule.domain}",
        row_index=None,
        record_key=None,
        value=None,
        condition=rule.condition,
    )


def run_rules(domain_tables: Dict[str, pd.DataFrame], rules: Iterable[Rule]) -> List[Violation]:
    violations: List[Violation] = []
    for rule in rules:
        domain = rule.domain.upper()
        if domain not in domain_tables:
            violations.append(_missing_domain_violation(rule))
            continue

        df = domain_tables[domain]
        if rule.variable.upper() not in df.columns:
            violations.append(_missing_variable_violation(rule))
            continue

        mask = build_mask(df, rule.condition)
        if not mask.any():
            continue

        for idx, row in df[mask].iterrows():
            value = row.get(rule.variable.upper())
            violations.append(
                Violation(
                    rule_id=rule.id,
                    source=rule.source,
                    domain=rule.domain,
                    variable=rule.variable,
                    severity=rule.severity,
                    message=rule.message,
                    row_index=int(idx) + 1,
                    record_key=_get_record_key(row),
                    value=None if pd.isna(value) else str(value),
                    condition=rule.condition,
                )
            )

    return violations
