import re
from typing import Iterable, List, Tuple, Union

import pandas as pd


_OP_PATTERN = re.compile(r"^(?P<col>[A-Za-z0-9_]+)\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<val>.+)$")
_IN_PATTERN = re.compile(r"^(?P<col>[A-Za-z0-9_]+)\s+in\s+\{(?P<vals>.+)\}$", re.IGNORECASE)
_NOT_IN_PATTERN = re.compile(r"^(?P<col>[A-Za-z0-9_]+)\s+not\s+in\s+\{(?P<vals>.+)\}$", re.IGNORECASE)
_MISSING_PATTERN = re.compile(r"^(?P<col>[A-Za-z0-9_]+)\s+is\s+missing$", re.IGNORECASE)
_NOT_MISSING_PATTERN = re.compile(r"^(?P<col>[A-Za-z0-9_]+)\s+not\s+missing$", re.IGNORECASE)
_BETWEEN_PATTERN = re.compile(
    r"^(?P<col>[A-Za-z0-9_]+)\s+between\s+(?P<low>.+)\s+and\s+(?P<high>.+)$",
    re.IGNORECASE,
)


Numeric = Union[int, float]


def _parse_value(token: str) -> Union[str, Numeric]:
    text = token.strip()
    if text.startswith(("'", '"')) and text.endswith(("'", '"')) and len(text) >= 2:
        return text[1:-1]
    if re.fullmatch(r"[+-]?\d+(\.\d+)?", text):
        if "." in text:
            return float(text)
        return int(text)
    return text


def _parse_list(values: str) -> List[Union[str, Numeric]]:
    parts = [part.strip() for part in values.split(",") if part.strip()]
    return [_parse_value(part) for part in parts]


def _is_missing(series: pd.Series) -> pd.Series:
    if series.dtype == object or str(series.dtype).startswith("string"):
        return series.isna() | (series.astype(str).str.strip() == "")
    return series.isna()


def _coerce_series(series: pd.Series, target: Union[str, Numeric, Iterable[Union[str, Numeric]]]) -> pd.Series:
    if isinstance(target, (int, float)):
        return pd.to_numeric(series, errors="coerce")
    if isinstance(target, Iterable) and not isinstance(target, (str, bytes)):
        if all(isinstance(item, (int, float)) for item in target):
            return pd.to_numeric(series, errors="coerce")
    return series.astype(str)


def build_mask(df: pd.DataFrame, condition: str) -> pd.Series:
    text = condition.strip()

    match = _MISSING_PATTERN.match(text)
    if match:
        col = match.group("col").upper()
        return _is_missing(df[col])

    match = _NOT_MISSING_PATTERN.match(text)
    if match:
        col = match.group("col").upper()
        return ~_is_missing(df[col])

    match = _IN_PATTERN.match(text)
    if match:
        col = match.group("col").upper()
        values = _parse_list(match.group("vals"))
        series = _coerce_series(df[col], values)
        return series.isin(values)

    match = _NOT_IN_PATTERN.match(text)
    if match:
        col = match.group("col").upper()
        values = _parse_list(match.group("vals"))
        series = _coerce_series(df[col], values)
        return ~series.isin(values)

    match = _BETWEEN_PATTERN.match(text)
    if match:
        col = match.group("col").upper()
        low = _parse_value(match.group("low"))
        high = _parse_value(match.group("high"))
        series = _coerce_series(df[col], [low, high])
        return (series >= low) & (series <= high)

    match = _OP_PATTERN.match(text)
    if match:
        col = match.group("col").upper()
        op = match.group("op")
        value = _parse_value(match.group("val"))
        series = _coerce_series(df[col], value)
        if op == "==":
            return series == value
        if op == "!=":
            return series != value
        if op == ">":
            return series > value
        if op == ">=":
            return series >= value
        if op == "<":
            return series < value
        if op == "<=":
            return series <= value

    raise ValueError(f"Unsupported condition: {condition}")
