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
from app.core.rule_loader import load_rules
from app.core.rule_manager import (
    initialize_rule_session,
    load_rules_to_session,
    get_rules_dataframe,
    add_rule_from_template,
    add_rule_from_fields,
    generate_next_rule_id,
    update_rules_from_dataframe,
    clear_all_rules,
    get_rule_count,
    get_domain_counts,
    validate_rules,
    import_rules_from_csv,
)
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  /* Primary Colors */
  --primary: #2563eb;
  --primary-dark: #1e40af;
  --primary-light: #3b82f6;
  --primary-glow: rgba(37, 99, 235, 0.15);

  /* Vibrant Accent Colors */
  --accent-purple: #8b5cf6;
  --accent-pink: #ec4899;
  --accent-teal: #14b8a6;
  --accent-orange: #f97316;

  /* Status Colors with Depth */
  --success: #10b981;
  --success-light: #34d399;
  --success-dark: #059669;
  --success-bg: #d1fae5;

  --warning: #f59e0b;
  --warning-light: #fbbf24;
  --warning-dark: #d97706;
  --warning-bg: #fef3c7;

  --error: #ef4444;
  --error-light: #f87171;
  --error-dark: #dc2626;
  --error-bg: #fee2e2;

  --info: #06b6d4;
  --info-light: #22d3ee;
  --info-dark: #0891b2;
  --info-bg: #cffafe;

  /* Rich Background Palette */
  --bg-main: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  --bg-card: #ffffff;
  --bg-secondary: #f1f5f9;
  --bg-accent: #f8fafc;
  --bg-gradient-light: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);

  /* Text Colors */
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --text-accent: var(--primary);

  /* Rich Border System */
  --border-primary: #2563eb;
  --border-success: #10b981;
  --border-warning: #f59e0b;
  --border-error: #ef4444;
  --border-accent: #8b5cf6;
  --border-light: #e2e8f0;
  --border-medium: #cbd5e1;
  --border-dark: #94a3b8;

  /* Enhanced Shadows */
  --shadow-xs: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.08), 0 1px 4px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.08);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.15), 0 4px 12px rgba(0,0,0,0.1);
  --shadow-xl: 0 12px 32px rgba(0,0,0,0.18), 0 6px 16px rgba(0,0,0,0.12);
  --shadow-glow: 0 0 20px var(--primary-glow);
  --shadow-color: 0 4px 16px rgba(37, 99, 235, 0.2);

  /* Border Radius */
  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-full: 9999px;

  /* Spacing System */
  --spacing-xs: 8px;
  --spacing-sm: 12px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-2xl: 40px;
}

/* Global Styles */
.stApp {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #dbeafe 100%);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  position: relative;
}

.stApp::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20% 80%, rgba(37, 99, 235, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.05) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

#MainMenu, header[data-testid="stHeader"], footer[data-testid="stFooter"] {
  visibility: hidden;
}

.block-container {
  max-width: 1400px !important;
  padding: var(--spacing-lg) var(--spacing-xl) !important;
  position: relative;
  z-index: 1;
}

[data-testid="stAppViewContainer"] > .main {
  position: relative;
  z-index: 1;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border-right: 3px solid var(--border-primary);
  box-shadow: 4px 0 16px rgba(37, 99, 235, 0.08);
}

[data-testid="stSidebar"] .block-container {
  padding: var(--spacing-md) !important;
}

/* Stunning Header */
.app-header {
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 50%, #7c3aed 100%);
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl) var(--spacing-2xl);
  margin-bottom: var(--spacing-xl);
  box-shadow: var(--shadow-xl), 0 0 40px rgba(37, 99, 235, 0.3);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.app-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at bottom left, rgba(139, 92, 246, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.app-header > * {
  position: relative;
  z-index: 1;
}

.app-header-badge {
  display: inline-block;
  background: linear-gradient(135deg, rgba(255,255,255,0.25), rgba(255,255,255,0.15));
  padding: 8px 18px;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-bottom: var(--spacing-md);
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.app-header-title {
  font-size: 38px;
  font-weight: 900;
  margin: 0;
  letter-spacing: -1px;
  line-height: 1.1;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.app-header-subtitle {
  color: rgba(255,255,255,0.95);
  font-size: 15px;
  margin-top: var(--spacing-sm);
  line-height: 1.6;
  font-weight: 500;
}

/* Stunning Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: var(--spacing-sm);
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  padding: var(--spacing-sm);
  border-radius: var(--radius-lg);
  border: 2px solid var(--border-primary);
  margin-bottom: var(--spacing-xl);
  box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.stTabs [data-baseweb="tab"] {
  height: 52px;
  background: transparent;
  border-radius: var(--radius-md);
  padding: 0 var(--spacing-xl);
  font-weight: 700;
  font-size: 14px;
  color: var(--text-secondary);
  border: 2px solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.stTabs [data-baseweb="tab"]:hover {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  color: var(--text-primary);
  border-color: var(--border-medium);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
  color: white !important;
  border-color: var(--border-primary) !important;
  box-shadow: var(--shadow-color), 0 0 20px rgba(37, 99, 235, 0.3) !important;
  transform: translateY(-2px);
}

.stTabs [aria-selected="true"]::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 40%;
  height: 4px;
  background: linear-gradient(90deg, transparent, white, transparent);
  border-radius: var(--radius-full);
}

.stTabs [data-baseweb="tab-panel"] {
  padding: var(--spacing-xl) 0;
}

/* Stunning Section Cards */
.section-card {
  background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
  box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255, 255, 255, 0.9);
  border: 3px solid var(--border-primary);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.section-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary), var(--accent-purple), var(--accent-teal));
  opacity: 0.8;
}

.section-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl), inset 0 1px 0 rgba(255, 255, 255, 0.9);
  border-color: var(--primary-light);
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-lg);
  border-bottom: 3px solid transparent;
  border-image: linear-gradient(90deg, var(--border-primary), var(--accent-purple), transparent) 1;
  position: relative;
}

.section-number {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 22px;
  margin-right: var(--spacing-lg);
  box-shadow: var(--shadow-color), 0 0 24px rgba(37, 99, 235, 0.4);
  border: 3px solid rgba(255, 255, 255, 0.3);
  position: relative;
}

.section-number::after {
  content: '';
  position: absolute;
  inset: -3px;
  border-radius: var(--radius-md);
  padding: 3px;
  background: linear-gradient(135deg, var(--primary-light), var(--accent-purple));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0.6;
}

.section-title {
  font-size: 24px;
  font-weight: 800;
  color: var(--text-primary);
  flex: 1;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, var(--text-primary), var(--primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Vibrant Alert Boxes */
.alert-info {
  background: linear-gradient(135deg, var(--info-bg) 0%, #e0f7fa 100%);
  border-left: 5px solid var(--info);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg) var(--spacing-lg);
  margin: var(--spacing-lg) 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--info-dark);
  box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255, 255, 255, 0.8);
  border-top: 2px solid var(--info-light);
  border-bottom: 2px solid var(--info-light);
  border-right: 2px solid var(--info-light);
  position: relative;
  overflow: hidden;
}

.alert-info::before {
  content: '💡';
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24px;
  opacity: 0.3;
}

.alert-warning {
  background: linear-gradient(135deg, var(--warning-bg) 0%, #fff8e1 100%);
  border-left: 5px solid var(--warning);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg) var(--spacing-lg);
  margin: var(--spacing-lg) 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--warning-dark);
  box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255, 255, 255, 0.8);
  border-top: 2px solid var(--warning-light);
  border-bottom: 2px solid var(--warning-light);
  border-right: 2px solid var(--warning-light);
  position: relative;
  overflow: hidden;
}

.alert-warning::before {
  content: '⚠️';
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24px;
  opacity: 0.3;
}

.alert-success {
  background: linear-gradient(135deg, var(--success-bg) 0%, #e8f5e9 100%);
  border-left: 5px solid var(--success);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg) var(--spacing-lg);
  margin: var(--spacing-lg) 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--success-dark);
  box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255, 255, 255, 0.8);
  border-top: 2px solid var(--success-light);
  border-bottom: 2px solid var(--success-light);
  border-right: 2px solid var(--success-light);
  position: relative;
  overflow: hidden;
}

.alert-success::before {
  content: '✅';
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24px;
  opacity: 0.3;
}

.alert-error {
  background: linear-gradient(135deg, var(--error-bg) 0%, #ffebee 100%);
  border-left: 5px solid var(--error);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg) var(--spacing-lg);
  margin: var(--spacing-lg) 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--error-dark);
  box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255, 255, 255, 0.8);
  border-top: 2px solid var(--error-light);
  border-bottom: 2px solid var(--error-light);
  border-right: 2px solid var(--error-light);
  position: relative;
  overflow: hidden;
}

.alert-error::before {
  content: '❌';
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24px;
  opacity: 0.3;
}

/* Stunning Metrics */
.metric-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
  margin: var(--spacing-xl) 0;
}

.metric-box {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 3px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  text-align: center;
  box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255, 255, 255, 0.9);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.metric-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary), var(--accent-purple), var(--accent-teal));
}

.metric-box::after {
  content: '';
  position: absolute;
  bottom: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.05) 0%, transparent 70%);
  transition: all 0.3s;
}

.metric-box:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: var(--shadow-xl), inset 0 1px 0 rgba(255, 255, 255, 0.9);
  border-color: var(--primary-light);
}

.metric-box:hover::after {
  bottom: -20%;
  right: -20%;
}

.metric-value {
  font-size: 40px;
  font-weight: 900;
  background: linear-gradient(135deg, var(--primary), var(--accent-purple));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  position: relative;
  z-index: 1;
}

.metric-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 1.2px;
  margin-top: var(--spacing-md);
  position: relative;
  z-index: 1;
}

/* Stunning Buttons */
.stButton > button {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  border: 3px solid rgba(255, 255, 255, 0.3) !important;
  border-radius: var(--radius-md);
  padding: 14px var(--spacing-xl);
  font-weight: 700;
  font-size: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-color), 0 0 20px rgba(37, 99, 235, 0.2);
  position: relative;
  overflow: hidden;
}

.stButton > button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.5s;
}

.stButton > button:hover::before {
  left: 100%;
}

.stButton > button:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: var(--shadow-xl), 0 0 30px rgba(37, 99, 235, 0.4);
  background: linear-gradient(135deg, var(--primary-light), var(--primary));
  border-color: rgba(255, 255, 255, 0.5) !important;
}

.stButton > button:active {
  transform: translateY(-1px) scale(0.98);
}

.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--primary), var(--accent-purple));
  box-shadow: var(--shadow-color), 0 0 25px rgba(139, 92, 246, 0.3);
}

.stDownloadButton > button {
  background: linear-gradient(135deg, var(--success), var(--accent-teal));
  color: white;
  border: 3px solid rgba(255, 255, 255, 0.3) !important;
  border-radius: var(--radius-md);
  padding: 14px var(--spacing-xl);
  font-weight: 700;
  font-size: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3), 0 0 20px rgba(20, 184, 166, 0.2);
}

.stDownloadButton > button:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: var(--shadow-xl), 0 0 30px rgba(16, 185, 129, 0.4);
  background: linear-gradient(135deg, var(--success-light), var(--accent-teal));
  border-color: rgba(255, 255, 255, 0.5) !important;
}

/* Stunning Template Cards */
.template-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 2px solid var(--border-medium);
  border-left: 5px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  margin: var(--spacing-md) 0;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
}

.template-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 60px;
  height: 60px;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.1) 0%, transparent 70%);
  transform: translate(20px, -20px);
  transition: all 0.3s;
}

.template-card:hover::before {
  transform: translate(10px, -10px) scale(1.5);
  background: radial-gradient(circle, rgba(37, 99, 235, 0.15) 0%, transparent 70%);
}

.template-card:hover {
  background: linear-gradient(135deg, #f0f7ff 0%, #e0f2fe 100%);
  border-left-color: var(--accent-purple);
  border-color: var(--border-primary);
  box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255, 255, 255, 0.9);
  transform: translateX(8px) translateY(-2px);
}

.template-id {
  font-weight: 800;
  font-size: 13px;
  color: var(--primary);
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, var(--primary), var(--accent-purple));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: inline-block;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  border: 2px solid var(--border-primary);
  margin-bottom: var(--spacing-xs);
}

.template-name {
  font-weight: 700;
  font-size: 15px;
  margin: var(--spacing-sm) 0;
  color: var(--text-primary);
  line-height: 1.4;
}

.template-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-top: var(--spacing-xs);
  font-weight: 500;
}

.template-tags {
  margin-top: var(--spacing-md);
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  background: linear-gradient(135deg, var(--primary), var(--accent-purple));
  color: white;
  padding: 5px 12px;
  border-radius: var(--radius-full);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.3);
  transition: all 0.2s;
}

.tag:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(37, 99, 235, 0.4);
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

/* Sidebar Navigation */
[data-testid="stSidebar"] {
  background: #f6f8fb;
  border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] .sidebar-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-muted);
  margin: 4px 0 12px 0;
}

[data-testid="stSidebar"] .stRadio > div {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

[data-testid="stSidebar"] .stRadio label {
  background: #ffffff;
  border: 1px solid #d7e0ef;
  border-radius: 12px;
  padding: 10px 14px;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
  cursor: pointer;
}

[data-testid="stSidebar"] .stRadio label:hover {
  background: #f6f8fb;
  border-color: #c9d6ea;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

[data-testid="stSidebar"] .stRadio label input {
  display: none;
}

[data-testid="stSidebar"] .stRadio label div {
  font-weight: 700;
  color: var(--text-secondary);
}

[data-testid="stSidebar"] .stRadio label:has(input:checked) {
  background: linear-gradient(135deg, #1e63d6 0%, #0d47a1 100%);
  border-color: #0d47a1;
  box-shadow: var(--shadow-lg);
}

[data-testid="stSidebar"] .stRadio label:has(input:checked) div {
  color: #ffffff;
}

/* Data Tables & Editor */
.stDataFrame, .stDataEditor {
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}

[data-testid="stDataFrame"] > div, [data-testid="stDataEditor"] > div {
  border-radius: var(--radius-sm);
}

/* Code Blocks */
code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  background: var(--bg-secondary);
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-light);
  color: var(--primary-dark);
}

pre {
  background: #f8f9fa;
  padding: var(--spacing-md);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
}

/* Inputs & Selects */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stMultiSelect > div > div > div {
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border) !important;
  font-size: 14px;
  padding: var(--spacing-sm) !important;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > div:focus,
.stMultiSelect > div > div > div:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 1px var(--primary) !important;
}

/* File Uploader */
.stFileUploader {
  border-radius: var(--radius-sm);
}

[data-testid="stFileUploadDropzone"] {
  border-radius: var(--radius-sm);
  border: 2px dashed var(--border);
  background: var(--bg-secondary);
  transition: all 0.2s;
}

[data-testid="stFileUploadDropzone"]:hover {
  border-color: var(--primary);
  background: #f0f7ff;
}

/* Progress Bars */
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--primary), var(--primary-light));
  border-radius: 10px;
}

/* Expander */
.streamlit-expanderHeader {
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  font-weight: 600;
  border: 1px solid var(--border-light);
}

.streamlit-expanderHeader:hover {
  background: var(--bg-card);
  border-color: var(--border);
}

/* Success/Info/Warning/Error Messages */
.stSuccess, .stInfo, .stWarning, .stError {
  border-radius: var(--radius-sm);
  padding: var(--spacing-md);
  margin: var(--spacing-md) 0;
}

/* Metrics */
[data-testid="stMetricValue"] {
  font-size: 28px;
  font-weight: 800;
  color: var(--primary);
}

[data-testid="stMetricLabel"] {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Columns */
[data-testid="column"] {
  padding: 0 var(--spacing-xs);
}

/* Divider */
hr {
  margin: var(--spacing-lg) 0;
  border: none;
  border-top: 2px solid var(--border-light);
}

/* Tooltips */
[data-baseweb="tooltip"] {
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-lg);
}

/* Responsive Design */
@media (max-width: 768px) {
  .block-container {
    padding: var(--spacing-md) !important;
  }

  .app-header {
    padding: var(--spacing-md);
  }

  .app-header-title {
    font-size: 24px;
  }

  .metric-row {
    grid-template-columns: 1fr;
  }

  .section-card {
    padding: var(--spacing-md);
  }
}

/* Animation Classes */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-in {
  animation: fadeIn 0.3s ease-out;
}

/* Loading State */
.stSpinner > div {
  border-color: var(--primary) !important;
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

# Initialize rule session management
initialize_rule_session()

if "project_name" not in st.session_state:
    st.session_state.project_name = "STUDY-001"
if "protocol_number" not in st.session_state:
    st.session_state.protocol_number = "PRO-2024-001"
if "core_rules_path" not in st.session_state:
    st.session_state.core_rules_path = "rules/core_rules.json"
if "include_custom" not in st.session_state:
    st.session_state.include_custom = True

project_name = st.session_state.project_name
protocol_number = st.session_state.protocol_number
core_rules_path = st.session_state.core_rules_path
include_custom = st.session_state.include_custom

# Main Header
st.markdown(
    f"""
<div class="app-header">
  <div class="app-header-title">SDTM Data Standards Validator</div>
</div>
""",
    unsafe_allow_html=True,
)

# Navigation
nav_items = [
    "Project Settings",
    "Data Loading",
    "Rule Configuration",
    "Run Validation",
    "Results Analysis",
    "Help",
]
st.sidebar.markdown('<div class="sidebar-title">Navigation</div>', unsafe_allow_html=True)
selected_tab = st.sidebar.radio(
    "Navigation",
    nav_items,
    index=0,
    key="nav_tab",
    label_visibility="collapsed",
)

# TAB 0: Project Settings
if selected_tab == "Project Settings":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        """
    <div class="section-header">
      <div class="section-number">0</div>
      <div class="section-title">Project Settings</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="alert-info">Set the study context and validation configuration used across the app.</div>',
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns(2)
    with col_left:
        st.text_input(
            "Project ID",
            key="project_name",
            help="Unique study identifier used for file storage and reporting.",
        )
        st.text_input(
            "Protocol Number",
            key="protocol_number",
            help="Clinical protocol identifier shown in the report header.",
        )
        st.caption("Reports are saved under projects/<project>/runs/<timestamp>.")

    with col_right:
        st.text_input(
            "Core Rules Path",
            key="core_rules_path",
            help="Path to CDISC core rules JSON.",
        )
        st.toggle(
            "Enable Custom Rules",
            key="include_custom",
            help="Turn on project-specific validation rules.",
        )
        st.caption("Custom rules are stored in projects/<project>/custom_rules.json.")

    st.markdown('</div>', unsafe_allow_html=True)

# TAB 1: Data Loading
elif selected_tab == "Data Loading":
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
elif selected_tab == "Rule Configuration":
    domain_tables: Dict[str, pd.DataFrame] = dict(st.session_state.domain_tables)

    # Load existing rules into session on first visit
    if not st.session_state.custom_rules_list:
        existing_rules = load_custom_rules(project_name)
        if existing_rules:
            load_rules_to_session(existing_rules)

    # Display success message if rule was just added
    if st.session_state.get("show_success_message", False):
        last_added = st.session_state.get("last_added_rule", "")
        st.success(f"✅ Rule {last_added} added successfully! You can edit it in the table below.")
        st.session_state.show_success_message = False

    col_rules, col_templates = st.columns([3, 2])

    with col_rules:
        st.markdown('<div class="section-card section-card--rules">', unsafe_allow_html=True)
        st.markdown(
            """
        <div class="section-card-header section-card-header--rules">
          <div class="section-number">2</div>
          <div class="section-title">Custom Validation Rules</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if include_custom:
            st.markdown(
                f'<div class="alert-info">💡 Click templates on the right to add rules instantly! '
                f'Maximum {MAX_RULES_PER_DOMAIN} rules per domain. Edit any rule directly in the table.</div>',
                unsafe_allow_html=True,
            )

            editor_key = f"rules_editor_{st.session_state.rules_editor_version}"
            if editor_key in st.session_state and isinstance(st.session_state[editor_key], pd.DataFrame):
                update_rules_from_dataframe(st.session_state[editor_key])

            st.markdown("#### Quick Add Templates")
            quick_cols = st.columns([2, 1])
            with quick_cols[0]:
                domain_options = ["All Domains"] + sorted({t.domain for t in get_all_templates()})
                quick_domain = st.selectbox(
                    "Template Domain",
                    options=domain_options,
                    help="Narrow templates by domain for faster adding",
                )
            with quick_cols[1]:
                quick_add_all = st.button("Add all shown", use_container_width=True)

            if quick_domain == "All Domains":
                quick_templates = get_all_templates()
            else:
                quick_templates = get_templates_by_domain(quick_domain)

            quick_templates = quick_templates[:6]
            quick_button_cols = st.columns(3)
            for idx, template in enumerate(quick_templates):
                with quick_button_cols[idx % 3]:
                    if st.button(
                        f"+ Add {template.id}",
                        key=f"quick_add_{template.id}",
                        help=template.description,
                        use_container_width=True,
                    ):
                        if include_custom:
                            add_rule_from_template(template)
                            st.rerun()
                        else:
                            st.warning("Enable custom rules in the Project Settings tab.")

            if quick_add_all and quick_templates:
                if include_custom:
                    for template in quick_templates:
                        add_rule_from_template(template)
                    st.rerun()
                else:
                    st.warning("Enable custom rules in the Project Settings tab.")

            with st.expander("Add a custom rule manually"):
                auto_id = st.toggle("Auto-generate Rule ID", value=True, key="builder_auto_id")
                if auto_id and st.session_state.get("builder_domain"):
                    preview_id = generate_next_rule_id(st.session_state.get("builder_domain", ""))
                    if preview_id:
                        st.caption(f"Next Rule ID: {preview_id}")
                    else:
                        st.caption("Enter a domain to generate the Rule ID.")

                with st.form("rule_builder", clear_on_submit=True):
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        builder_domain = st.text_input("Domain", placeholder="DM", key="builder_domain")
                        builder_id = st.text_input(
                            "Rule ID",
                            placeholder="DM001",
                            key="builder_id",
                            disabled=auto_id,
                        )
                    with col_b:
                        builder_variable = st.text_input("Variable", placeholder="AGE", key="builder_variable")
                        builder_severity = st.selectbox(
                            "Severity",
                            options=["ERROR", "WARNING", "INFO"],
                            index=1,
                            key="builder_severity",
                        )
                    with col_c:
                        builder_condition = st.text_input("Condition", placeholder="AGE > 100", key="builder_condition")
                        builder_message = st.text_input("Message", placeholder="Age exceeds 100", key="builder_message")

                    builder_submit = st.form_submit_button("Add rule")

                if builder_submit:
                    if not include_custom:
                        st.warning("Enable custom rules in the Project Settings tab.")
                    else:
                        missing_fields = []
                        if not builder_domain.strip():
                            missing_fields.append("Domain")
                        if not builder_variable.strip():
                            missing_fields.append("Variable")
                        if not builder_condition.strip():
                            missing_fields.append("Condition")
                        if not builder_message.strip():
                            missing_fields.append("Message")
                        if not auto_id and not builder_id.strip():
                            missing_fields.append("Rule ID")

                        if missing_fields:
                            st.error(f"Missing fields: {', '.join(missing_fields)}")
                            st.stop()

                        added = add_rule_from_fields(
                            {
                                "id": "" if auto_id else builder_id,
                                "domain": builder_domain,
                                "variable": builder_variable,
                                "condition": builder_condition,
                                "severity": builder_severity,
                                "message": builder_message,
                            }
                        )
                        if not added:
                            st.error("Domain is required to generate a Rule ID.")
                        else:
                            st.rerun()

            # Get rules from session state
            rules_df = get_rules_dataframe()

            if st.session_state.get("editor_refresh", False):
                st.session_state.rules_editor_version += 1
                st.session_state.editor_refresh = False
                editor_key = f"rules_editor_{st.session_state.rules_editor_version}"

            # Data editor
            edited_df = st.data_editor(
                rules_df,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key=editor_key,
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

            # Update session state from editor
            update_rules_from_dataframe(edited_df)

            # Rule Summary with Progress Bars
            rule_count = get_rule_count()
            domain_counts = get_domain_counts()

            st.markdown("---")
            st.markdown("#### 📊 Rule Summary")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Custom Rules", rule_count)

                # Progress bar for total rules
                total_limit = MAX_RULES_PER_DOMAIN * 10  # Reasonable total limit
                progress_pct = min(rule_count / total_limit, 1.0)
                st.progress(progress_pct, text=f"{rule_count} / {total_limit} rules")

            with col2:
                st.metric("Domains Covered", len(domain_counts))

                # Show domain breakdown
                if domain_counts:
                    st.caption("Rules per domain:")
                    for domain, count in sorted(domain_counts.items()):
                        pct = count / MAX_RULES_PER_DOMAIN
                        color = "🟢" if pct < 0.7 else "🟡" if pct < 0.9 else "🔴"
                        st.caption(f"{color} {domain}: {count}/{MAX_RULES_PER_DOMAIN}")

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

            # Action buttons
            st.markdown("---")
            st.markdown("#### 🛠️ Actions")
            if st.session_state.rules_changed:
                st.markdown(
                    '<div class="alert-warning">⚠️ You have unsaved changes. Click Save to persist them.</div>',
                    unsafe_allow_html=True,
                )

            col_save, col_export, col_import, col_clear = st.columns(4)

            with col_save:
                save_clicked = st.button("💾 Save", type="primary", use_container_width=True, help="Save rules to project")

            with col_export:
                if rule_count > 0:
                    csv = edited_df.to_csv(index=False)
                    st.download_button(
                        "📥 Export",
                        csv,
                        f"custom_rules_{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv",
                        use_container_width=True,
                        help="Export rules as CSV"
                    )
                else:
                    st.button("📥 Export", use_container_width=True, disabled=True, help="No rules to export")

            with col_import:
                uploaded_file = st.file_uploader("📤 Import CSV", type="csv", key="rule_import", label_visibility="collapsed")
                if uploaded_file:
                    imported, errors = import_rules_from_csv(uploaded_file)
                    if errors:
                        st.error(f"Import errors: {', '.join(errors)}")
                    else:
                        st.success(f"✅ Imported {imported} rules!")
                        st.rerun()

            with col_clear:
                if rule_count > 0:
                    if st.button("🗑️ Clear All", use_container_width=True, help="Remove all custom rules"):
                        clear_all_rules()
                        st.success("✅ All rules cleared!")
                        st.rerun()
                else:
                    st.button("🗑️ Clear All", use_container_width=True, disabled=True, help="No rules to clear")

            # Save action
            if save_clicked:
                rules, errors = validate_rules()
                if errors:
                    st.markdown(
                        f'<div class="alert-error">❌ <strong>Validation Errors:</strong><br>{"<br>".join(errors)}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    save_custom_rules(project_name, rules)
                    st.session_state.rules_changed = False
                    st.markdown(
                        f'<div class="alert-success">✅ Successfully saved {len(rules)} custom rule(s) for {project_name}</div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown(
                '<div class="alert-warning">Custom rules disabled. Enable them in Project Settings to add project-specific rules.</div>',
                unsafe_allow_html=True,
            )

        st.markdown('</div>', unsafe_allow_html=True)

    # Rule Template Browser
    with col_templates:
        st.markdown('<div class="section-card section-card--templates">', unsafe_allow_html=True)
        st.markdown(
            """
        <div class="section-card-header section-card-header--templates">
          <div class="section-number">T</div>
          <div class="section-title">Rule Template Library</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.caption("Click '+Add' to instantly add rules")

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

        # Search filter
        search_term = st.text_input("🔍 Search templates", placeholder="Search by ID, name, or tag...", label_visibility="collapsed")
        if search_term:
            search_lower = search_term.lower()
            templates = [
                t for t in templates
                if search_lower in t.id.lower()
                or search_lower in t.name.lower()
                or search_lower in t.description.lower()
                or any(search_lower in tag.lower() for tag in t.tags)
            ]

        st.caption(f"📋 Showing {len(templates)} templates")

        # Display templates
        for template in templates[:15]:  # Show more templates
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

                # ONE-CLICK ADD BUTTON
                if st.button(f"➕ Add {template.id}", key=f"add_{template.id}", use_container_width=True):
                    if include_custom:
                        success = add_rule_from_template(template)
                        if success:
                            st.rerun()
                    else:
                        st.warning("Enable custom rules in Project Settings first.")

        if len(templates) > 15:
            st.caption(f"⬇️ {len(templates) - 15} more templates available. Use filters to narrow down.")

        st.markdown('</div>', unsafe_allow_html=True)

# TAB 3: Run Validation
elif selected_tab == "Run Validation":
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

    domain_tables = dict(st.session_state.domain_tables)

    st.markdown("#### Validation scope")
    validation_mode = st.radio(
        "Choose validation type",
        ["Standard rules only", "Custom rules only", "Standard + Custom"],
        index=2,
        horizontal=True,
        help="Standard rules come from the CDISC core rule set; custom rules are project-specific.",
    )
    apply_core = validation_mode != "Custom rules only"
    apply_custom = validation_mode != "Standard rules only"

    if apply_custom and include_custom and not st.session_state.custom_rules_list:
        existing_rules = load_custom_rules(project_name)
        if existing_rules:
            load_rules_to_session(existing_rules)

    core_path = Path(core_rules_path)
    if apply_core and not core_path.exists():
        st.markdown(
            f'<div class="alert-warning">Core rules not found at {core_rules_path}. Standard validation cannot run.</div>',
            unsafe_allow_html=True,
        )
    if apply_custom and not include_custom:
        st.markdown(
            '<div class="alert-warning">Custom rules are disabled. Enable them in Project Settings to use custom validation.</div>',
            unsafe_allow_html=True,
        )

    scope_label = "standard rules" if apply_core and not apply_custom else "custom rules" if apply_custom and not apply_core else "standard and custom rules"
    st.markdown(
        f'<div class="alert-info">Validation will run {scope_label} and report row-level violations.</div>',
        unsafe_allow_html=True,
    )

    core_rules = load_rules(core_path, source="core") if (apply_core and core_path.exists()) else []
    if core_rules:
        core_rules_df = pd.DataFrame(
            [
                {
                    "id": rule.id,
                    "domain": rule.domain,
                    "variable": rule.variable,
                    "condition": rule.condition,
                    "severity": rule.severity,
                    "message": rule.message,
                }
                for rule in core_rules
            ]
        )
    else:
        core_rules_df = pd.DataFrame(columns=RULE_COLUMNS)

    all_custom_rules_df = get_rules_dataframe() if include_custom else pd.DataFrame(columns=RULE_COLUMNS)
    custom_rules_df = all_custom_rules_df if (apply_custom and include_custom) else pd.DataFrame(columns=RULE_COLUMNS)
    custom_rule_count = len(custom_rules_df)

    loaded_domains = sorted(domain_tables.keys())
    core_domains = {rule.domain for rule in core_rules}
    custom_domains = set()
    if not custom_rules_df.empty:
        custom_domains = set(custom_rules_df["domain"].astype(str).str.upper())
    applicable_domains = sorted(core_domains | custom_domains)
    missing_domains = sorted(set(applicable_domains) - set(loaded_domains))
    applicable_present = [d for d in applicable_domains if d in domain_tables]

    st.markdown("#### Applicable datasets")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Loaded domains", len(loaded_domains))
    with col_b:
        st.metric("Applicable domains", len(applicable_present))
    with col_c:
        st.metric("Missing domains", len(missing_domains))

    if missing_domains:
        st.markdown(
            f'<div class="alert-warning">Rules reference domains not loaded: {", ".join(missing_domains)}</div>',
            unsafe_allow_html=True,
        )

    if not applicable_present and loaded_domains:
        st.info("No rule domains detected yet. Showing all loaded datasets for preview.")
        applicable_present = loaded_domains

    if applicable_present:
        applicable_tables = {d: domain_tables[d] for d in applicable_present}
        st.dataframe(_build_domain_table(applicable_tables), use_container_width=True, hide_index=True)
        preview_domain = st.selectbox(
            "Preview applicable dataset",
            options=applicable_present,
            help="Quick preview of the data that will be validated.",
        )
        if preview_domain:
            st.dataframe(domain_tables[preview_domain].head(10), use_container_width=True, hide_index=False)
    else:
        st.info("No applicable datasets available yet. Load SDTM domains or add rules.")

    st.markdown("#### Rules that will be applied")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Core rules selected", len(core_rules))
    with col_b:
        st.metric("Custom rules selected", custom_rule_count)
    with col_c:
        st.metric("Total rules", len(core_rules) + custom_rule_count)

    if apply_custom and include_custom and custom_rule_count == 0:
        st.markdown(
            '<div class="alert-warning">No custom rules added yet. Add rules in the Rule Configuration tab.</div>',
            unsafe_allow_html=True,
        )
    if not apply_custom and include_custom and len(all_custom_rules_df) > 0:
        st.markdown(
            f'<div class="alert-info">Custom rules available: {len(all_custom_rules_df)} (not selected for this run).</div>',
            unsafe_allow_html=True,
        )
    if st.session_state.rules_changed and apply_custom:
        st.markdown(
            '<div class="alert-warning">You have unsaved custom rule changes. They will be used for this run, but save them to persist.</div>',
            unsafe_allow_html=True,
        )

    with st.expander(f"Custom rules preview ({custom_rule_count})", expanded=False):
        if apply_custom and include_custom and custom_rule_count:
            st.dataframe(
                custom_rules_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": st.column_config.TextColumn("Rule ID", width="small"),
                    "domain": st.column_config.TextColumn("Domain", width="small"),
                    "variable": st.column_config.TextColumn("Variable", width="small"),
                    "condition": st.column_config.TextColumn("Condition", width="large"),
                    "severity": st.column_config.TextColumn("Severity", width="small"),
                    "message": st.column_config.TextColumn("Message", width="large"),
                },
            )
        elif apply_custom and include_custom:
            st.info("No custom rules available yet.")
        else:
            st.info("Custom rules are not selected for this run.")

    with st.expander(f"Core rules preview ({len(core_rules)})", expanded=False):
        if not core_rules_df.empty:
            st.dataframe(core_rules_df.head(50), use_container_width=True, hide_index=True)
            st.caption("Showing first 50 core rules.")
        else:
            st.info("Core rules are not selected or not available.")

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
            st.session_state.last_run_validation_mode = validation_mode
            st.session_state.last_run_core_rules_df = core_rules_df if apply_core else pd.DataFrame(columns=RULE_COLUMNS)
            st.session_state.last_run_custom_rules_df = custom_rules_df if apply_custom else pd.DataFrame(columns=RULE_COLUMNS)
            st.session_state.last_run_domains = applicable_present

            if apply_core and not core_path.exists():
                st.markdown(
                    f'<div class="alert-error">Core rules not found at {core_rules_path}. Select custom rules or fix the path.</div>',
                    unsafe_allow_html=True,
                )
                st.stop()
            if apply_custom and not include_custom:
                st.markdown(
                    '<div class="alert-error">Custom rules are disabled. Enable them in Project Settings or choose standard rules only.</div>',
                    unsafe_allow_html=True,
                )
                st.stop()

            if apply_custom and include_custom:
                rules_df = get_rules_dataframe()
                rules, errors = _rules_from_editor(rules_df)
                if errors:
                    st.markdown(
                        f'<div class="alert-error">❌ <strong>Rule Errors:</strong><br>{"<br>".join(errors)}</div>',
                        unsafe_allow_html=True,
                    )
                    st.stop()
                save_custom_rules(project_name, rules)

            custom_path = custom_rules_path(project_name)
            custom_path_for_run = custom_path if apply_custom else Path("__no_custom_rules__")
            core_path_for_run = core_path if apply_core else Path("__no_core_rules__")

            # Run validation
            with st.spinner("🔍 Running validation checks..."):
                try:
                    start_time = datetime.now()
                    violations, rule_order = run_validation(domain_tables, core_path_for_run, custom_path_for_run)
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
elif selected_tab == "Results Analysis":
    if not st.session_state.validation_complete:
        st.info("⏳ Run validation in Tab 3 to see results analysis here.")
    else:
        violations = st.session_state.violations
        domain_tables = dict(st.session_state.domain_tables)
        last_mode = st.session_state.get("last_run_validation_mode", "Standard + Custom")
        last_core_rules_df = st.session_state.get("last_run_core_rules_df", pd.DataFrame(columns=RULE_COLUMNS))
        last_custom_rules_df = st.session_state.get("last_run_custom_rules_df", pd.DataFrame(columns=RULE_COLUMNS))

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

        st.markdown(
            f'<div class="alert-info">Last validation mode: <strong>{last_mode}</strong></div>',
            unsafe_allow_html=True,
        )

        if not violations:
            st.markdown(
                '<div class="alert-success">No violations found. All validation checks passed!</div>',
                unsafe_allow_html=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            violations_df = pd.DataFrame([v.__dict__ for v in violations])
            if violations_df.empty:
                st.info("No violations to analyze.")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()

            violations_df["domain"] = violations_df["domain"].astype(str).str.upper()
            violations_df["severity"] = violations_df["severity"].astype(str).str.upper()
            violations_df["rule_id"] = violations_df["rule_id"].astype(str)
            violations_df["source"] = violations_df["source"].astype(str)
            violations_df["row_index"] = pd.to_numeric(violations_df["row_index"], errors="coerce")

            total_violations = len(violations_df)
            unique_rules = violations_df["rule_id"].nunique()
            unique_domains = violations_df["domain"].nunique()
            unique_subjects = violations_df["record_key"].dropna().nunique()
            impacted_records = (
                violations_df.dropna(subset=["row_index"])
                .drop_duplicates(["domain", "row_index"])
                .shape[0]
            )

            st.markdown("### Executive summary")
            summary_cols = st.columns(5)
            summary_cols[0].metric("Total violations", total_violations)
            summary_cols[1].metric("Rules triggered", unique_rules)
            summary_cols[2].metric("Domains impacted", unique_domains)
            summary_cols[3].metric("Subjects impacted", unique_subjects if unique_subjects else "N/A")
            summary_cols[4].metric("Records impacted", impacted_records if impacted_records else "N/A")

            severity_counts = (
                violations_df["severity"]
                .value_counts()
                .reindex(["ERROR", "WARNING", "INFO"], fill_value=0)
            )
            source_counts = violations_df["source"].value_counts()
            domain_counts = violations_df["domain"].value_counts().head(10)

            chart_cols = st.columns(3)
            with chart_cols[0]:
                st.markdown("#### Severity distribution")
                st.bar_chart(severity_counts)
            with chart_cols[1]:
                st.markdown("#### Source distribution")
                st.bar_chart(source_counts)
            with chart_cols[2]:
                st.markdown("#### Top domains")
                st.bar_chart(domain_counts)

            st.markdown("### Rule coverage")
            total_rules_used = len(last_core_rules_df) + len(last_custom_rules_df)
            triggered_rules = set(violations_df["rule_id"].unique())
            rules_used_df = pd.concat([last_core_rules_df, last_custom_rules_df], ignore_index=True)
            rules_used_df["id"] = rules_used_df["id"].astype(str)
            zero_hit_rules = rules_used_df[~rules_used_df["id"].isin(triggered_rules)]

            cov_cols = st.columns(3)
            cov_cols[0].metric("Rules used", total_rules_used)
            cov_cols[1].metric("Rules with violations", unique_rules)
            cov_cols[2].metric("Rules with 0 violations", len(zero_hit_rules))

            with st.expander(f"Rules with no violations ({len(zero_hit_rules)})", expanded=False):
                if not zero_hit_rules.empty:
                    st.dataframe(
                        zero_hit_rules[["id", "domain", "variable", "severity", "message"]].head(50),
                        use_container_width=True,
                        hide_index=True,
                    )
                    st.caption("Showing first 50 rules with zero violations.")
                else:
                    st.info("All applied rules produced at least one violation.")

            st.markdown("### Filters and drill-down")
            filter_cols = st.columns(4)
            with filter_cols[0]:
                severity_filter = st.multiselect(
                    "Severity",
                    options=["ERROR", "WARNING", "INFO"],
                    default=["ERROR", "WARNING", "INFO"],
                )
            with filter_cols[1]:
                domain_options = sorted(violations_df["domain"].unique())
                domain_filter = st.multiselect(
                    "Domain",
                    options=domain_options,
                    default=domain_options,
                )
            with filter_cols[2]:
                source_options = sorted(violations_df["source"].unique())
                source_filter = st.multiselect(
                    "Source",
                    options=source_options,
                    default=source_options,
                )
            with filter_cols[3]:
                rule_search = st.text_input("Search rule/message")

            filtered_df = violations_df[
                violations_df["severity"].isin(severity_filter)
                & violations_df["domain"].isin(domain_filter)
                & violations_df["source"].isin(source_filter)
            ]

            if rule_search:
                search_lower = rule_search.lower()
                filtered_df = filtered_df[
                    filtered_df["rule_id"].str.lower().str.contains(search_lower, na=False)
                    | filtered_df["message"].str.lower().str.contains(search_lower, na=False)
                    | filtered_df["variable"].str.lower().str.contains(search_lower, na=False)
                ]

            st.metric("Filtered violations", len(filtered_df))

            if filtered_df.empty:
                st.info("No violations match the selected filters.")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()

            st.markdown("#### Top rules by violations")
            top_rules = (
                filtered_df.groupby(["rule_id", "domain", "severity"])
                .size()
                .reset_index(name="count")
                .sort_values("count", ascending=False)
                .head(10)
            )
            st.dataframe(top_rules, use_container_width=True, hide_index=True)

            st.markdown("#### Domain impact")
            domain_rows = []
            for domain, count in filtered_df["domain"].value_counts().items():
                record_count = len(domain_tables.get(domain, []))
                unique_rows = (
                    filtered_df[filtered_df["domain"] == domain]["row_index"]
                    .dropna()
                    .nunique()
                )
                rate = (unique_rows / record_count * 100) if record_count else None
                domain_rows.append(
                    {
                        "domain": domain,
                        "violations": int(count),
                        "unique_records": int(unique_rows) if unique_rows else 0,
                        "dataset_records": int(record_count),
                        "violation_rate_pct": round(rate, 2) if rate is not None else None,
                    }
                )
            domain_impact_df = pd.DataFrame(domain_rows)
            st.dataframe(domain_impact_df, use_container_width=True, hide_index=True)

            st.markdown("#### Violation details")
            st.dataframe(
                filtered_df.sort_values(["severity", "domain", "rule_id"]),
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
                },
            )

            csv = filtered_df.to_csv(index=False)
            st.download_button(
                "Export filtered results (CSV)",
                csv,
                f"violations_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv",
                use_container_width=True,
            )

            with st.expander("Drill-down by domain"):
                drill_domain = st.selectbox("Select domain", options=sorted(filtered_df["domain"].unique()))
                drill_df = filtered_df[filtered_df["domain"] == drill_domain]
                st.metric("Violations in domain", len(drill_df))

                if drill_domain in domain_tables:
                    show_data = st.checkbox("Show violating records from dataset")
                    if show_data and not drill_df.empty:
                        row_indices = [idx - 1 for idx in drill_df["row_index"].dropna().astype(int).unique()]
                        if row_indices:
                            df = domain_tables[drill_domain]
                            violating_records = df.iloc[row_indices]
                            st.dataframe(violating_records, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

# TAB 5: Help
elif selected_tab == "Help":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        """
    <div class="section-header">
      <div class="section-number">5</div>
      <div class="section-title">Help and Usage Guide</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="alert-info">This guide explains how to validate SDTM datasets with standard and custom rules.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### High-level flow")
    st.markdown(
        """
1) Load SDTM datasets (XPT files named by domain such as DM.xpt, AE.xpt, LB.xpt).  
2) Add custom rules for your study in Rule Configuration.  
3) Choose the validation type in Run Validation and review the rule preview.  
4) Run validation and export the combined report.
"""
    )

    st.markdown("### Domain-focused guidance")
    st.markdown(
        """
- DM (Demographics): confirm required identifiers such as USUBJID, and check AGE and SEX values.  
- AE (Adverse Events): verify AESTDTC and review serious or fatal outcomes.  
- LB (Laboratory): check missing units and out-of-range indicators.  
- VS (Vital Signs): review extreme values and missing measurements.
"""
    )

    st.markdown("### Custom rule tips")
    st.markdown(
        """
- Use clear rule IDs per domain (DM001, AE001, etc).  
- Use simple conditions like AGE > 100, USUBJID is missing, or SEX not in {'M','F','U'}.  
- Save rules to reuse them across runs for the same study.
"""
    )

    st.markdown("### Quick troubleshooting")
    st.markdown(
        """
- If a domain is missing, load its XPT file before running validation.  
- If you changed rules, Save them to persist for future runs.  
- If no rules appear, check the Standard vs Custom selection on Run Validation.
"""
    )

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
