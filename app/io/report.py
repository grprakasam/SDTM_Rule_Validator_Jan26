from pathlib import Path
from typing import Iterable, List

import pandas as pd

from app.core.rules import Violation


def _violations_to_frame(violations: Iterable[Violation]) -> pd.DataFrame:
    rows = [
        {
            "source": v.source,
            "rule_id": v.rule_id,
            "domain": v.domain,
            "variable": v.variable,
            "severity": v.severity,
            "message": v.message,
            "condition": v.condition,
            "row_index": v.row_index,
            "record_key": v.record_key,
            "value": v.value,
        }
        for v in violations
    ]
    if not rows:
        return pd.DataFrame(
            columns=[
                "source",
                "rule_id",
                "domain",
                "variable",
                "severity",
                "message",
                "condition",
                "row_index",
                "record_key",
                "value",
            ]
        )
    return pd.DataFrame(rows)


def write_report(output_path: Path, violations: List[Violation], rule_order: List[str]) -> None:
    df = _violations_to_frame(violations)

    order_map = {rule_id: idx for idx, rule_id in enumerate(rule_order)}
    if not df.empty:
        df["source_order"] = df["source"].map({"core": 0, "custom": 1}).fillna(2)
        df["rule_order"] = df["rule_id"].map(order_map).fillna(len(order_map) + 1)
        df = df.sort_values(
            ["source_order", "rule_order", "domain", "row_index"],
            na_position="last",
        )
        df = df.drop(columns=["source_order", "rule_order"])

    summary = (
        df.groupby(["source", "rule_id", "severity"], dropna=False)
        .size()
        .reset_index(name="count")
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="violations")
        summary.to_excel(writer, index=False, sheet_name="summary")
