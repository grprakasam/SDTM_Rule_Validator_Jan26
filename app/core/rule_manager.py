"""
Rule Manager - Session state management for custom rules
Handles adding, removing, and managing rules in the UI
"""
from __future__ import annotations

from typing import List, Dict, Optional
import re
import pandas as pd
import streamlit as st

from .rules import Rule
from .rule_templates import RuleTemplate


def initialize_rule_session():
    """Initialize session state for rules if not exists"""
    if "custom_rules_list" not in st.session_state:
        st.session_state.custom_rules_list = []
    if "rules_changed" not in st.session_state:
        st.session_state.rules_changed = False
    if "editor_refresh" not in st.session_state:
        st.session_state.editor_refresh = False
    if "rules_editor_version" not in st.session_state:
        st.session_state.rules_editor_version = 0
    if "last_added_rule" not in st.session_state:
        st.session_state.last_added_rule = None
    if "show_success_message" not in st.session_state:
        st.session_state.show_success_message = False


def load_rules_to_session(rules: List[Rule]):
    """Load existing rules into session state"""
    st.session_state.custom_rules_list = [
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
    st.session_state.rules_changed = False
    st.session_state.editor_refresh = True


def generate_next_rule_id(domain: str) -> str:
    """Generate the next available rule ID for a domain (e.g., DM001)."""
    clean_domain = (domain or "").strip().upper()
    if not clean_domain:
        return ""

    pattern = re.compile(rf"^{re.escape(clean_domain)}(\d+)$")
    existing_ids = [r.get("id", "").strip().upper() for r in st.session_state.custom_rules_list]
    max_num = 0
    for rule_id in existing_ids:
        match = pattern.match(rule_id)
        if match:
            try:
                max_num = max(max_num, int(match.group(1)))
            except ValueError:
                continue

    next_num = max_num + 1
    candidate = f"{clean_domain}{next_num:03d}"
    existing_set = set(existing_ids)
    while candidate in existing_set:
        next_num += 1
        candidate = f"{clean_domain}{next_num:03d}"
    return candidate


def get_rules_dataframe() -> pd.DataFrame:
    """Get current rules as DataFrame"""
    if not st.session_state.custom_rules_list:
        return pd.DataFrame(columns=["id", "domain", "variable", "condition", "severity", "message"])
    return pd.DataFrame(st.session_state.custom_rules_list)


def add_rule_from_template(template: RuleTemplate) -> bool:
    """
    Add a rule from template to session state
    Returns True if added, False if duplicate
    """
    # Check for duplicate ID
    existing_ids = [r["id"] for r in st.session_state.custom_rules_list]

    if template.id in existing_ids:
        # Generate unique ID
        base_id = template.id
        counter = 1
        new_id = f"{base_id}_{counter}"
        while new_id in existing_ids:
            counter += 1
            new_id = f"{base_id}_{counter}"
        template_id = new_id
    else:
        template_id = template.id

    new_rule = {
        "id": template_id,
        "domain": template.domain,
        "variable": template.variable,
        "condition": template.condition,
        "severity": template.severity,
        "message": template.message,
    }

    st.session_state.custom_rules_list.append(new_rule)
    st.session_state.rules_changed = True
    st.session_state.editor_refresh = True
    st.session_state.last_added_rule = template_id
    st.session_state.show_success_message = True

    return True


def add_rule_from_fields(rule_fields: Dict[str, str]) -> bool:
    """Add a rule from user-supplied fields."""
    domain = rule_fields.get("domain", "").strip().upper()
    rule_id = rule_fields.get("id", "").strip()
    if not rule_id:
        rule_id = generate_next_rule_id(domain)
    if not rule_id:
        return False

    existing_ids = [r["id"] for r in st.session_state.custom_rules_list]
    if rule_id in existing_ids:
        base_id = rule_id
        counter = 1
        new_id = f"{base_id}_{counter}"
        while new_id in existing_ids:
            counter += 1
            new_id = f"{base_id}_{counter}"
        rule_id = new_id

    new_rule = {
        "id": rule_id,
        "domain": domain,
        "variable": rule_fields.get("variable", "").strip().upper(),
        "condition": rule_fields.get("condition", "").strip(),
        "severity": rule_fields.get("severity", "").strip().upper(),
        "message": rule_fields.get("message", "").strip(),
    }

    st.session_state.custom_rules_list.append(new_rule)
    st.session_state.rules_changed = True
    st.session_state.editor_refresh = True
    st.session_state.last_added_rule = rule_id
    st.session_state.show_success_message = True
    return True


def update_rules_from_dataframe(df: pd.DataFrame):
    """Update session state from edited dataframe"""
    rules_list = []
    for _, row in df.iterrows():
        # Skip completely empty rows
        if all(pd.isna(row[col]) or str(row[col]).strip() == "" for col in df.columns):
            continue

        rules_list.append({
            "id": str(row.get("id", "")).strip(),
            "domain": str(row.get("domain", "")).strip(),
            "variable": str(row.get("variable", "")).strip(),
            "condition": str(row.get("condition", "")).strip(),
            "severity": str(row.get("severity", "")).strip(),
            "message": str(row.get("message", "")).strip(),
        })

    st.session_state.custom_rules_list = rules_list
    st.session_state.rules_changed = True


def clear_all_rules():
    """Clear all custom rules"""
    st.session_state.custom_rules_list = []
    st.session_state.rules_changed = True
    st.session_state.editor_refresh = True


def get_rule_count() -> int:
    """Get count of rules"""
    return len(st.session_state.custom_rules_list)


def get_domain_counts() -> Dict[str, int]:
    """Get count of rules per domain"""
    counts = {}
    for rule in st.session_state.custom_rules_list:
        domain = rule.get("domain", "").upper()
        if domain:
            counts[domain] = counts.get(domain, 0) + 1
    return counts


def validate_rules() -> tuple[List[Rule], List[str]]:
    """Validate and convert rules to Rule objects"""
    from .rules import Rule

    rules: List[Rule] = []
    errors: List[str] = []
    domain_counts: Dict[str, int] = {}
    seen_ids: set[str] = set()

    RULE_COLUMNS = ["id", "domain", "variable", "condition", "severity", "message"]
    MAX_RULES_PER_DOMAIN = 20

    for idx, rule_dict in enumerate(st.session_state.custom_rules_list, 1):
        # Check for missing fields
        missing = [col for col in RULE_COLUMNS if not rule_dict.get(col, "").strip()]
        if missing:
            errors.append(f"Rule {idx}: Missing {', '.join(missing)}")
            continue

        # Check for duplicate IDs
        rule_id = rule_dict["id"]
        if rule_id in seen_ids:
            errors.append(f"Duplicate ID: {rule_id}")
        seen_ids.add(rule_id)

        # Check domain limits
        domain = rule_dict["domain"].upper()
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        if domain_counts[domain] > MAX_RULES_PER_DOMAIN:
            errors.append(f"Domain {domain} exceeds {MAX_RULES_PER_DOMAIN} rules limit")

        # Create Rule object
        rules.append(
            Rule(
                id=rule_id,
                domain=domain,
                variable=rule_dict["variable"].upper(),
                condition=rule_dict["condition"],
                severity=rule_dict["severity"].upper(),
                message=rule_dict["message"],
                source="custom",
            )
        )

    return rules, errors


def import_rules_from_csv(uploaded_file) -> tuple[int, List[str]]:
    """Import rules from CSV file"""
    try:
        df = pd.read_csv(uploaded_file)

        # Validate required columns
        required_cols = ["id", "domain", "variable", "condition", "severity", "message"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return 0, [f"Missing columns: {', '.join(missing_cols)}"]

        # Add rules from CSV
        imported = 0
        errors = []
        for _, row in df.iterrows():
            try:
                new_rule = {
                    "id": str(row["id"]).strip(),
                    "domain": str(row["domain"]).strip(),
                    "variable": str(row["variable"]).strip(),
                    "condition": str(row["condition"]).strip(),
                    "severity": str(row["severity"]).strip(),
                    "message": str(row["message"]).strip(),
                }
                st.session_state.custom_rules_list.append(new_rule)
                imported += 1
            except Exception as e:
                errors.append(f"Row error: {str(e)}")

        st.session_state.rules_changed = True
        st.session_state.editor_refresh = True
        return imported, errors

    except Exception as e:
        return 0, [f"Failed to read CSV: {str(e)}"]
