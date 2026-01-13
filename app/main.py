from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.rules import Rule, Violation
from app.core.validation import run_validation
from app.core.rule_templates import (
    get_all_templates,
    get_templates_by_category,
    get_template_categories,
    get_templates_by_domain,
)
from app.core.violation_manager import ViolationManager
from app.io.report import write_report
from app.io.xpt import load_xpt_bytes, load_xpt_path
from app.storage.project import (
    custom_rules_path,
    load_custom_rules,
    new_run_folder,
    save_custom_rules,
)


RULE_COLUMNS = ["id", "domain", "variable", "condition", "severity", "message"]
MAX_RULES_PER_DOMAIN = 20  # Increased for practical use
SAMPLE_LIST_URL = "https://api.github.com/repos/lexjansen/cdisc-core-sas/contents/testdata/sdtm"
SAMPLE_RAW_BASE = "https://raw.githubusercontent.com/lexjansen/cdisc-core-sas/main/testdata/sdtm"
SAMPLE_CACHE_DIR = Path("samples") / "sdtm"


def apply_theme() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --primary: #1565c0;
  --primary-dark: #0d47a1;
  --primary-light: #1976d2;
  --success: #2e7d32;
  --warning: #f57c00;
  --error: #c62828;
  --info: #0277bd;
  --bg-main: #fafafa;
  --bg-card: #ffffff;
  --bg-secondary: #f5f5f5;
  --text-primary: #212121;
  --text-secondary: #616161;
  --text-muted: #9e9e9e;
  --border: #e0e0e0;
  --border-light: #eeeeee;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
  --shadow-md: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
  --shadow-lg: 0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23);
}

.stApp {
  background: var(--bg-main);
  color: var(--text-primary);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

#MainMenu, header, footer { visibility: hidden; }

/* Header */
.app-header {
  background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
  border-radius: 8px;
  padding: 40px;
  margin-bottom: 24px;
  box-shadow: var(--shadow-md);
  color: white;
}

.app-header-badge {
  display: inline-block;
  background: rgba(255,255,255,0.25);
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  margin-bottom: 12px;
}

.app-header-title {
  font-size: 32px;
  font-weight: 700;
  margin: 8px 0;
}

.app-header-subtitle {
  color: rgba(255,255,255,0.9);
  font-size: 15px;
  line-height: 1.6;
}

/* Section Cards */
.section-card {
  background: var(--bg-card);
  border-radius: 8px;
  padding: 24px;
  margin: 20px 0;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--border-light);
}

.section-number {
  background: var(--primary);
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  margin-right: 12px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
}

/* Alert Boxes */
.alert-info {
  background: #e3f2fd;
  border-left: 4px solid var(--info);
  border-radius: 4px;
  padding: 12px 16px;
  margin: 12px 0;
  font-size: 14px;
  color: var(--text-primary);
}

.alert-warning {
  background: #fff3e0;
  border-left: 4px solid var(--warning);
  border-radius: 4px;
  padding: 12px 16px;
  margin: 12px 0;
  font-size: 14px;
  color: var(--text-primary);
}

.alert-success {
  background: #e8f5e9;
  border-left: 4px solid var(--success);
  border-radius: 4px;
  padding: 12px 16px;
  margin: 12px 0;
  font-size: 14px;
  color: var(--text-primary);
}

.alert-error {
  background: #ffebee;
  border-left: 4px solid var(--error);
  border-radius: 4px;
  padding: 12px 16px;
  margin: 12px 0;
  font-size: 14px;
  color: var(--text-primary);
}

/* Metrics */
.metric-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin: 20px 0;
}

.metric-box {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 16px;
  text-align: center;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary);
}

.metric-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-top: 4px;
}

/* Buttons */
.stButton > button {
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 24px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
  box-shadow: var(--shadow-sm);
}

.stButton > button:hover {
  background: var(--primary-dark);
  box-shadow: var(--shadow-md);
}

/* Template Browser */
.template-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px;
  margin: 8px 0;
  cursor: pointer;
  transition: all 0.2s;
}

.template-card:hover {
  background: #e8eaf6;
  border-color: var(--primary);
  box-shadow: var(--shadow-sm);
}

.template-id {
  font-weight: 700;
  color: var(--primary);
  font-size: 12px;
}

.template-name {
  font-weight: 600;
  margin: 4px 0;
  font-size: 14px;
}

.template-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.template-tags {
  margin-top: 8px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  background: var(--primary);
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 600;
}

/* Status Badges */
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-new { background: #e0e0e0; color: #424242; }
.status-review { background: #fff3e0; color: #e65100; }
.status-accepted { background: #e8f5e9; color: #2e7d32; }
.status-fixed { background: #bbdefb; color: #01579b; }
.status-false { background: #f3e5f5; color: #4a148c; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 8px;
}

.stTabs [data-baseweb="tab"] {
  border-radius: 6px 6px 0 0;
  padding: 12px 24px;
  font-weight: 600;
}

/* Data Editor */
.stDataFrame, .stDataEditor {
  border-radius: 6px;
  border: 1px solid var(--border);
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--bg-card);
  border-right: 1px solid var(--border);
}

/* Code */
code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  background: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 4px;
}

pre {
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: 6px;
  border: 1px solid var(--border);
}
</style>
""",
        unsafe_allow_html=True,
    )


def _rules_from_editor(df: pd.DataFrame) -> Tuple[List[Rule], List[str]]:
    rules: List[Rule] = []
    errors: List[str] = []
    domain_counts: Dict[str, int] = {}
    seen_ids: set[str] = set()

    for idx, row in df.iterrows():
        values = {col: str(row.get(col, "")).strip() for col in RULE_COLUMNS}
        if all(not value for value in values.values()):
            continue
        missing = [col for col, value in values.items() if not value]
        if missing:
            errors.append(f"Row {idx + 1}: Missing {', '.join(missing)}")
            continue

        rule_id = values["id"]
        if rule_id in seen_ids:
            errors.append(f"Duplicate ID: {rule_id}")
        seen_ids.add(rule_id)

        domain = values["domain"].upper()
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        if domain_counts[domain] > MAX_RULES_PER_DOMAIN:
            errors.append(f"Domain {domain} exceeds {MAX_RULES_PER_DOMAIN} rules limit")

        rules.append(
            Rule(
                id=rule_id,
                domain=domain,
                variable=values["variable"].upper(),
                condition=values["condition"],
                severity=values["severity"].upper(),
                message=values["message"],
                source="custom",
            )
        )

    return rules, errors


def _build_domain_table(domain_tables: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = [
        {
            "Domain": domain,
            "Records": f"{len(table):,}",
            "Variables": len(table.columns),
            "Variables List": ", ".join(sorted(table.columns[:10])) + ("..." if len(table.columns) > 10 else ""),
        }
        for domain, table in sorted(domain_tables.items())
    ]
    return pd.DataFrame(rows)


def _fetch_sample_files() -> List[str]:
    try:
        response = requests.get(SAMPLE_LIST_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        files = [
            item["name"]
            for item in data
            if item.get("type") == "file" and str(item.get("name", "")).lower().endswith(".xpt")
        ]
        if files:
            return sorted(files)
    except requests.RequestException:
        pass
    return []


def _download_sample_files(progress_container) -> List[Path]:
    files = _fetch_sample_files()
    if not files:
        st.error("Unable to fetch sample files")
        return []

    SAMPLE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    total = len(files)
    progress_bar = progress_container.progress(0.0)
    status_text = progress_container.empty()

    for idx, name in enumerate(files, start=1):
        target = SAMPLE_CACHE_DIR / name
        if not target.exists():
            status_text.text(f"Downloading {name}...")
            url = f"{SAMPLE_RAW_BASE}/{name}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            target.write_bytes(response.content)
        progress_bar.progress(idx / total)

    progress_bar.empty()
    status_text.empty()
    return [SAMPLE_CACHE_DIR / name for name in files]


# Page Configuration
st.set_page_config(
    page_title="SDTM Validation Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_theme()

# Initialize Session State
if "domain_tables" not in st.session_state:
    st.session_state.domain_tables = {}
if "data_source" not in st.session_state:
    st.session_state.data_source = "none"
if "violations" not in st.session_state:
    st.session_state.violations = []
if "rule_order" not in st.session_state:
    st.session_state.rule_order = []
if "validation_complete" not in st.session_state:
    st.session_state.validation_complete = False
if "last_run_time" not in st.session_state:
    st.session_state.last_run_time = None

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Project Settings")
    project_name = st.text_input(
        "Project ID",
        value="STUDY-001",
        help="Unique study identifier"
    )

    protocol_number = st.text_input(
        "Protocol Number",
        value="PRO-2024-001",
        help="Clinical trial protocol number"
    )

    st.markdown("### 📋 Validation Configuration")
    core_rules_path = st.text_input(
        "Core Rules",
        value="rules/core_rules.json",
        help="CDISC core validation rules"
    )

    include_custom = st.toggle(
        "Custom Rules",
        value=True,
        help="Enable project-specific rules"
    )

    st.divider()

    st.markdown("### 📊 Quick Stats")
    if st.session_state.domain_tables:
        st.metric("Domains Loaded", len(st.session_state.domain_tables))

    if st.session_state.validation_complete:
        st.metric("Violations Found", len(st.session_state.violations))
        if st.session_state.last_run_time:
            st.caption(f"Last run: {st.session_state.last_run_time}")

    st.divider()

    st.markdown("### 📚 Help & Documentation")
    with st.expander("Common Issues"):
        st.markdown("""
        **Error: Domain not found**
        - Ensure XPT files are named correctly (DM.xpt, AE.xpt)

        **Error: Variable not found**
        - Check variable name spelling and case

        **Slow validation**
        - Large datasets may take time
        - Consider filtering by domain
        """)

# Main Header
st.markdown(
    f"""
<div class="app-header">
  <div class="app-header-badge">CDISC SDTM Compliance Engine</div>
  <div class="app-header-title">Clinical Data Validation Platform</div>
  <div class="app-header-subtitle">
    Project: <strong>{project_name}</strong> | Protocol: <strong>{protocol_number}</strong>
    <br>Automated validation of SDTM datasets with CDISC core rules and study-specific checks
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Data Loading",
    "⚙️ Rule Configuration",
    "🔍 Run Validation",
    "📈 Results Analysis"
])

# TAB 1: Data Loading
with tab1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        """
    <div class="section-header">
      <div class="section-number">1</div>
      <div class="section-title">SDTM Dataset Loading</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="alert-info">💡 Upload XPT files from your SDTM submission package or use sample data for testing. '
        'File names should match domain codes (e.g., dm.xpt, ae.xpt, lb.xpt).</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        load_sample = st.button("📥 Load Sample Data", use_container_width=True)
    with col2:
        clear_data = st.button("🗑️ Clear All Data", use_container_width=True)
    with col3:
        st.markdown("[📖 Sample Source](https://github.com/lexjansen/cdisc-core-sas)")

    uploaded_files = st.file_uploader(
        "Upload SDTM XPT Files",
        type=["xpt"],
        accept_multiple_files=True,
        help="Select multiple XPT files (Ctrl+Click or Cmd+Click)"
    )

    domain_tables: Dict[str, pd.DataFrame] = dict(st.session_state.domain_tables)

    if clear_data:
        st.session_state.domain_tables = {}
        st.session_state.data_source = "none"
        st.session_state.violations = []
        st.session_state.validation_complete = False
        domain_tables = {}
        st.rerun()

    if load_sample:
        progress_container = st.empty()
        with st.spinner("Downloading CDISC sample datasets..."):
            try:
                paths = _download_sample_files(progress_container)
                if paths:
                    domain_tables = {}
                    for path in paths:
                        domain, df = load_xpt_path(path)
                        domain_tables[domain] = df
                    st.session_state.domain_tables = domain_tables
                    st.session_state.data_source = "sample"
                    st.success(f"✅ Loaded {len(domain_tables)} sample domains")
                    st.rerun()
            except Exception as exc:
                st.error(f"❌ Failed to load sample data: {str(exc)}")

    if uploaded_files:
        domain_tables = {}
        with st.spinner("Processing XPT files..."):
            for upload in uploaded_files:
                try:
                    domain, df = load_xpt_bytes(upload.getvalue(), upload.name)
                    domain_tables[domain] = df
                except Exception as exc:
                    st.error(f"❌ Error loading {upload.name}: {str(exc)}")
            st.session_state.domain_tables = domain_tables
            st.session_state.data_source = "upload"
            if domain_tables:
                st.success(f"✅ Loaded {len(domain_tables)} domains")

    if domain_tables:
        # Metrics
        st.markdown('<div class="metric-row">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f'<div class="metric-box"><div class="metric-value">{len(domain_tables)}</div>'
                f'<div class="metric-label">Domains</div></div>',
                unsafe_allow_html=True
            )
        with col2:
            total_records = sum(len(t) for t in domain_tables.values())
            st.markdown(
                f'<div class="metric-box"><div class="metric-value">{total_records:,}</div>'
                f'<div class="metric-label">Total Records</div></div>',
                unsafe_allow_html=True
            )
        with col3:
            total_vars = sum(len(t.columns) for t in domain_tables.values())
            st.markdown(
                f'<div class="metric-box"><div class="metric-value">{total_vars}</div>'
                f'<div class="metric-label">Total Variables</div></div>',
                unsafe_allow_html=True
            )
        with col4:
            source = "Sample Data" if st.session_state.data_source == "sample" else "Uploaded"
            st.markdown(
                f'<div class="metric-box"><div class="metric-value">✓</div>'
                f'<div class="metric-label">{source}</div></div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # Domain Details
        with st.expander("📊 View Domain Details", expanded=False):
            summary_df = _build_domain_table(domain_tables)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)

            # Domain selector for data preview
            selected_domain = st.selectbox(
                "Preview Domain Data",
                options=sorted(domain_tables.keys()),
                help="Select a domain to view sample records"
            )

            if selected_domain:
                st.markdown(f"**{selected_domain} Domain - First 10 Records:**")
                st.dataframe(
                    domain_tables[selected_domain].head(10),
                    use_container_width=True,
                    hide_index=False
                )
    else:
        st.markdown(
            '<div class="alert-warning">⚠️ No datasets loaded. Upload XPT files or load sample data to begin.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

# TAB 2: Rule Configuration
with tab2:
    col_rules, col_templates = st.columns([3, 2])

    with col_rules:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(
            """
        <div class="section-header">
          <div class="section-number">2</div>
          <div class="section-title">Custom Validation Rules</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if include_custom:
            st.markdown(
                f'<div class="alert-info">💡 Define custom rules tailored to your protocol. '
                f'Maximum {MAX_RULES_PER_DOMAIN} rules per domain. Use the template browser on the right for quick insertion.</div>',
                unsafe_allow_html=True,
            )

            existing_rules = load_custom_rules(project_name)
            if existing_rules:
                rules_df = pd.DataFrame(
                    [
                        {
                            "id": rule.id,
                            "domain": rule.domain,
                            "variable": rule.variable,
                            "condition": rule.condition,
                            "severity": rule.severity,
                            "message": rule.message,
                        }
                        for rule in existing_rules
                    ]
                )
            else:
                rules_df = pd.DataFrame(columns=RULE_COLUMNS)

            edited_df = st.data_editor(
                rules_df,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": st.column_config.TextColumn("Rule ID", width="small", required=True),
                    "domain": st.column_config.TextColumn("Domain", width="small", required=True),
                    "variable": st.column_config.TextColumn("Variable", width="medium", required=True),
                    "condition": st.column_config.TextColumn("Condition", width="large", required=True),
                    "severity": st.column_config.SelectboxColumn(
                        "Severity",
                        width="small",
                        options=["ERROR", "WARNING", "INFO"],
                        required=True
                    ),
                    "message": st.column_config.TextColumn("Message", width="large", required=True),
                },
            )

            # Rule Summary
            cleaned = edited_df.replace({"": None}).dropna(how="all")
            total_rules = len(cleaned) if not cleaned.empty else 0
            domains_covered = cleaned["domain"].nunique() if not cleaned.empty else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("Custom Rules", total_rules)
            col2.metric("Domains Covered", domains_covered)
            col3.metric("Max Per Domain", MAX_RULES_PER_DOMAIN)

            with st.expander("📖 Rule Syntax Examples"):
                st.code(
                    """# Comparison
AGE > 120          # Age exceeds maximum
WEIGHT < 30        # Underweight check

# Missing Values
USUBJID is missing    # Required field check
RFSTDTC not missing   # Field should be populated

# Set Membership
AESEV in {'SEVERE','LIFE THREATENING'}
SEX in {'M','F'}

# Range Checks
AGE between 18 and 65
VISITNUM between 1 and 12

# Equality
ARMCD == 'PLACEBO'
COUNTRY != 'USA'""",
                    language="text"
                )

            col_save, col_export = st.columns(2)
            with col_save:
                save_clicked = st.button("💾 Save Rules", type="primary", use_container_width=True)
            with col_export:
                if not edited_df.empty:
                    csv = edited_df.to_csv(index=False)
                    st.download_button(
                        "📥 Export Rules (CSV)",
                        csv,
                        f"custom_rules_{project_name}.csv",
                        "text/csv",
                        use_container_width=True
                    )

            if save_clicked:
                rules, errors = _rules_from_editor(edited_df)
                if errors:
                    st.markdown(
                        f'<div class="alert-error">❌ <strong>Validation Errors:</strong><br>{"<br>".join(errors)}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    save_custom_rules(project_name, rules)
                    st.markdown(
                        f'<div class="alert-success">✅ Successfully saved {len(rules)} custom rule(s) for {project_name}</div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown(
                '<div class="alert-warning">⚠️ Custom rules disabled. Enable in sidebar to add project-specific rules.</div>',
                unsafe_allow_html=True,
            )

        st.markdown('</div>', unsafe_allow_html=True)

    # Rule Template Browser
    with col_templates:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 📚 Rule Template Library")
        st.caption("Click a template to copy rule syntax")

        categories = get_template_categories()
        selected_category = st.selectbox(
            "Filter by Category",
            options=["All Categories"] + categories,
            help="Browse pre-built rules by domain"
        )

        if domain_tables:
            loaded_domains = sorted(domain_tables.keys())
            domain_filter = st.multiselect(
                "Filter by Loaded Domains",
                options=loaded_domains,
                help="Show only templates for loaded domains"
            )
        else:
            domain_filter = []

        # Get templates
        if selected_category == "All Categories":
            templates = get_all_templates()
        else:
            templates = get_templates_by_category(selected_category)

        # Apply domain filter
        if domain_filter:
            templates = [t for t in templates if t.domain in domain_filter]

        st.caption(f"Showing {len(templates)} templates")

        # Display templates
        for template in templates[:10]:  # Limit to 10 for performance
            with st.container():
                st.markdown(f"""
                <div class="template-card">
                  <div class="template-id">{template.id}</div>
                  <div class="template-name">{template.name}</div>
                  <div class="template-desc">{template.description}</div>
                  <div class="template-tags">
                    {"".join(f'<span class="tag">{tag}</span>' for tag in template.tags[:3])}
                  </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"➕ Add {template.id}", key=f"add_{template.id}", use_container_width=True):
                    st.code(
                        f"ID: {template.id}\n"
                        f"Domain: {template.domain}\n"
                        f"Variable: {template.variable}\n"
                        f"Condition: {template.condition}\n"
                        f"Severity: {template.severity}\n"
                        f"Message: {template.message}",
                        language="text"
                    )
                    st.info(f"👆 Copy the above values into the rule editor on the left")

        st.markdown('</div>', unsafe_allow_html=True)

# TAB 3: Run Validation
with tab3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        """
    <div class="section-header">
      <div class="section-number">3</div>
      <div class="section-title">Execute Validation</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    core_path = Path(core_rules_path)
    if not core_path.exists():
        st.markdown(
            f'<div class="alert-warning">⚠️ Core rules not found at {core_rules_path}. Only custom rules will run.</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="alert-info">💡 Validation will check all loaded domains against CDISC core rules and your custom rules. '
        'Results will include detailed violation records with row-level information.</div>',
        unsafe_allow_html=True,
    )

    col_run, col_status = st.columns([2, 3])
    with col_run:
        run_clicked = st.button("▶️ Run Validation", type="primary", use_container_width=True, key="run_validation")

    with col_status:
        if st.session_state.validation_complete and st.session_state.last_run_time:
            st.info(f"Last validation: {st.session_state.last_run_time}")

    if run_clicked:
        if not domain_tables:
            st.markdown(
                '<div class="alert-error">❌ No datasets loaded. Load data in Tab 1 first.</div>',
                unsafe_allow_html=True,
            )
        else:
            # Save custom rules if enabled
            if include_custom:
                rules, errors = _rules_from_editor(edited_df)
                if errors:
                    st.markdown(
                        f'<div class="alert-error">❌ <strong>Rule Errors:</strong><br>{"<br>".join(errors)}</div>',
                        unsafe_allow_html=True,
                    )
                    st.stop()
                save_custom_rules(project_name, rules)
            else:
                save_custom_rules(project_name, [])

            custom_path = custom_rules_path(project_name)

            # Run validation
            with st.spinner("🔍 Running validation checks..."):
                try:
                    start_time = datetime.now()
                    violations, rule_order = run_validation(domain_tables, core_path, custom_path)
                    run_folder = new_run_folder(project_name)
                    report_path = run_folder / "validation_report.xlsx"
                    write_report(report_path, violations, rule_order)

                    st.session_state.violations = violations
                    st.session_state.rule_order = rule_order
                    st.session_state.validation_complete = True
                    st.session_state.last_run_time = start_time.strftime("%Y-%m-%d %H:%M:%S")

                except Exception as exc:
                    st.markdown(
                        f'<div class="alert-error">❌ <strong>Validation Failed:</strong><br>{str(exc)}</div>',
                        unsafe_allow_html=True,
                    )
                    st.stop()

            st.markdown(
                f'<div class="alert-success">✅ <strong>Validation Complete!</strong><br>Report: {report_path}</div>',
                unsafe_allow_html=True,
            )

            # Summary metrics
            if violations:
                error_count = sum(1 for v in violations if v.severity == "ERROR")
                warning_count = sum(1 for v in violations if v.severity == "WARNING")
                info_count = sum(1 for v in violations if v.severity == "INFO")

                st.markdown('<div class="metric-row">', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(
                        f'<div class="metric-box"><div class="metric-value" style="color: var(--error);">{error_count}</div>'
                        f'<div class="metric-label">Errors</div></div>',
                        unsafe_allow_html=True
                    )
                with col2:
                    st.markdown(
                        f'<div class="metric-box"><div class="metric-value" style="color: var(--warning);">{warning_count}</div>'
                        f'<div class="metric-label">Warnings</div></div>',
                        unsafe_allow_html=True
                    )
                with col3:
                    st.markdown(
                        f'<div class="metric-box"><div class="metric-value" style="color: var(--info);">{info_count}</div>'
                        f'<div class="metric-label">Info</div></div>',
                        unsafe_allow_html=True
                    )
                with col4:
                    st.markdown(
                        f'<div class="metric-box"><div class="metric-value">{len(violations)}</div>'
                        f'<div class="metric-label">Total</div></div>',
                        unsafe_allow_html=True
                    )
                st.markdown('</div>', unsafe_allow_html=True)

                with st.expander("👁️ Preview Results (First 20)", expanded=True):
                    preview_df = pd.DataFrame([v.__dict__ for v in violations[:20]])
                    st.dataframe(preview_df, use_container_width=True, hide_index=True)
            else:
                st.markdown(
                    '<div class="alert-success">🎉 <strong>No violations found!</strong> All datasets passed validation.</div>',
                    unsafe_allow_html=True,
                )

            # Download button
            with report_path.open("rb") as f:
                st.download_button(
                    "📥 Download Full Validation Report (Excel)",
                    f,
                    file_name=report_path.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )

    st.markdown('</div>', unsafe_allow_html=True)

# TAB 4: Results Analysis
with tab4:
    if not st.session_state.validation_complete:
        st.info("⏳ Run validation in Tab 3 to see results analysis here.")
    else:
        violations = st.session_state.violations

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(
            """
        <div class="section-header">
          <div class="section-number">4</div>
          <div class="section-title">Results Analysis & Tracking</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if not violations:
            st.markdown(
                '<div class="alert-success">🎉 No violations found. All validation checks passed!</div>',
                unsafe_allow_html=True,
            )
        else:
            # Filters
            col1, col2, col3 = st.columns(3)

            with col1:
                severity_filter = st.multiselect(
                    "Filter by Severity",
                    options=["ERROR", "WARNING", "INFO"],
                    default=["ERROR", "WARNING", "INFO"]
                )

            with col2:
                domains_in_violations = sorted(set(v.domain for v in violations))
                domain_filter = st.multiselect(
                    "Filter by Domain",
                    options=domains_in_violations,
                    default=domains_in_violations
                )

            with col3:
                sources = sorted(set(v.source for v in violations))
                source_filter = st.multiselect(
                    "Filter by Source",
                    options=sources,
                    default=sources
                )

            # Apply filters
            filtered_violations = [
                v for v in violations
                if v.severity in severity_filter
                and v.domain in domain_filter
                and v.source in source_filter
            ]

            st.metric("Filtered Violations", len(filtered_violations))

            # Violations table
            if filtered_violations:
                violations_df = pd.DataFrame([v.__dict__ for v in filtered_violations])

                # Add drill-down capability
                st.markdown("### 📋 Violation Details")
                st.dataframe(
                    violations_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "severity": st.column_config.TextColumn("Severity", width="small"),
                        "domain": st.column_config.TextColumn("Domain", width="small"),
                        "rule_id": st.column_config.TextColumn("Rule ID", width="small"),
                        "variable": st.column_config.TextColumn("Variable", width="medium"),
                        "message": st.column_config.TextColumn("Message", width="large"),
                        "row_index": st.column_config.NumberColumn("Row", width="small"),
                        "value": st.column_config.TextColumn("Value", width="medium"),
                    }
                )

                # Export filtered results
                csv = violations_df.to_csv(index=False)
                st.download_button(
                    "📥 Export Filtered Results (CSV)",
                    csv,
                    f"violations_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv",
                    use_container_width=True
                )

                # Domain-specific drill-down
                with st.expander("🔍 Drill-Down by Domain"):
                    selected_drill_domain = st.selectbox(
                        "Select Domain",
                        options=sorted(set(v.domain for v in filtered_violations))
                    )

                    domain_violations = [v for v in filtered_violations if v.domain == selected_drill_domain]

                    st.markdown(f"**{len(domain_violations)} violations in {selected_drill_domain} domain**")

                    # Show actual data if available
                    if selected_drill_domain in domain_tables:
                        show_data = st.checkbox("Show violating records from dataset")

                        if show_data and domain_violations:
                            row_indices = [v.row_index - 1 for v in domain_violations if v.row_index]
                            if row_indices:
                                df = domain_tables[selected_drill_domain]
                                violating_records = df.iloc[row_indices]
                                st.markdown("**Violating Records:**")
                                st.dataframe(violating_records, use_container_width=True)

            else:
                st.info("No violations match the selected filters.")

        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.divider()
st.markdown(
    f"""
<div style="text-align: center; color: var(--text-muted); font-size: 12px; padding: 16px;">
    <strong>SDTM Validation Platform v2.0</strong> | CDISC Compliant | FDA Submission Ready
    <br>Project: {project_name} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
</div>
""",
    unsafe_allow_html=True,
)
