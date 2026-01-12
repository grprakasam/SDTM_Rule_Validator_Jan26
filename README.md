# SDTM Validation Platform v2.0

**FDA Submission Ready | CDISC Compliant | Production Grade**

A comprehensive clinical data validation platform for SDTM datasets with automated CDISC core rules and customizable project-specific checks.

![Platform](https://img.shields.io/badge/Platform-Streamlit-red)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![CDISC](https://img.shields.io/badge/CDISC-SDTM%203.4-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## 🎯 Overview

This platform provides a modern, intuitive interface for validating SDTM (Study Data Tabulation Model) datasets against CDISC standards and study-specific requirements. Built for pharmaceutical companies, CROs, and clinical research organizations conducting FDA submissions.

### Key Features

✅ **40 Pre-Configured CDISC Core Rules** covering all major SDTM domains
✅ **50+ Rule Templates** for common validation scenarios
✅ **Custom Rule Builder** with syntax validation
✅ **Interactive 4-Tab Workflow** optimized for data managers
✅ **Advanced Filtering & Drill-Down** for violation analysis
✅ **Excel & CSV Export** with comprehensive reporting
✅ **Template Library** for quick rule insertion
✅ **Violation Tracking** with status management
✅ **Session Persistence** for complex workflows
✅ **Production-Ready** with audit trail capabilities

---

## 📊 Supported SDTM Domains

| Domain | Description | Core Rules | Templates |
|--------|-------------|------------|-----------|
| **DM** | Demographics | 10 | 7 |
| **AE** | Adverse Events | 7 | 6 |
| **LB** | Laboratory | 5 | 4 |
| **VS** | Vital Signs | 4 | 4 |
| **EX** | Exposure | 4 | 3 |
| **CM** | Concomitant Medications | 2 | 2 |
| **MH** | Medical History | 2 | 1 |
| **DS** | Disposition | 3 | 1 |
| **SV** | Subject Visits | 3 | - |

**Total**: 40 Core Rules + 50+ Templates

---

## 🚀 Quick Start

### Installation

```bash
# Clone or download the repository
cd CustomerRuleApp

# Install dependencies
pip install -r requirements.txt
```

### Launch

```bash
# Start the application
streamlit run app/main.py
```

The app will automatically open in your browser at `http://localhost:8501`

### First Validation (5 minutes)

1. **Load Sample Data**: Click "📥 Load Sample Data" in Tab 1
2. **Review Rules**: Browse template library in Tab 2
3. **Run Validation**: Click "▶️ Run Validation" in Tab 3
4. **Analyze Results**: Explore violations in Tab 4

📖 **Detailed Guide**: See [QUICKSTART.md](QUICKSTART.md) for step-by-step instructions

---

## 🏗️ Architecture

```
CustomerRuleApp/
├── app/
│   ├── main.py                      # Main Streamlit application
│   ├── core/
│   │   ├── rules.py                 # Rule & Violation data models
│   │   ├── rule_loader.py           # JSON rule loading
│   │   ├── rule_parser.py           # Condition parsing engine
│   │   ├── rule_engine.py           # Validation execution
│   │   ├── rule_templates.py        # 50+ pre-built templates
│   │   ├── validation.py            # Main validation orchestrator
│   │   └── violation_manager.py     # Violation tracking & annotations
│   ├── io/
│   │   ├── xpt.py                   # SAS XPT file reader
│   │   └── report.py                # Excel report generator
│   └── storage/
│       └── project.py               # Project management
├── rules/
│   └── core_rules.json              # 40 CDISC core rules
├── projects/                         # Project-specific data
│   └── <project_name>/
│       ├── custom_rules.json        # Custom rules
│       └── runs/                    # Validation runs
│           └── <timestamp>/
│               └── validation_report.xlsx
├── samples/                          # Cached sample data
├── README.md                         # This file
├── QUICKSTART.md                     # Quick start guide
└── requirements.txt                  # Python dependencies
```

---

## 🎨 User Interface

### Tab 1: Data Loading
- Upload SDTM XPT files or load CDISC samples
- View domain summaries and metrics
- Preview dataset contents
- Session state management

### Tab 2: Rule Configuration
**Left Panel**: Custom Rule Editor
- Add/edit rules with data editor
- Validate before saving
- Export rules to CSV

**Right Panel**: Template Library
- Browse 50+ pre-built templates
- Filter by category and domain
- One-click template insertion

### Tab 3: Run Validation
- Execute validation with progress indicator
- View violation summary by severity
- Preview top 20 violations
- Download comprehensive Excel report

### Tab 4: Results Analysis
- Advanced filtering (severity, domain, source)
- Domain-specific drill-down
- View violating records from datasets
- Export filtered results to CSV

---

## 📋 Rule Syntax

### Supported Patterns

```python
# Missing Value Checks
USUBJID is missing
RFSTDTC not missing

# Comparison Operators
AGE > 120
WEIGHT < 30
VISITNUM >= 1

# Set Membership
AESEV in {'SEVERE','MODERATE'}
SEX in {'M','F'}

# Range Checks
AGE between 18 and 65
VISITNUM between 1 and 12

# Equality
ARMCD == 'PLACEBO'
COUNTRY != 'USA'
```

### Rule Structure

```json
{
  "id": "PROTO001",
  "domain": "DM",
  "variable": "AGE",
  "condition": "AGE > 75",
  "severity": "ERROR",
  "message": "Subject exceeds protocol age limit"
}
```

**Severity Levels**:
- `ERROR`: Prevents submission (missing required fields, invalid data)
- `WARNING`: Requires review (optional fields, outliers)
- `INFO`: Informational flags (milestones, signals)

---

## 🔧 Configuration

### Project Settings (Sidebar)

```
Project ID: STUDY-001
Protocol Number: PRO-2024-001
Core Rules: rules/core_rules.json
Custom Rules: Enabled
```

### Custom Rules Limits

- **20 rules per domain** (increased from 10)
- **Unlimited total rules** across project
- **Validation** before saving

---

## 📦 Dependencies

```
streamlit==1.41.1      # Web application framework
pandas==2.2.3          # Data manipulation
pyreadstat==1.2.8      # SAS XPT file reader
openpyxl==3.1.5        # Excel report generation
requests                # Sample data download
```

---

## 🎯 Use Cases

### 1. Daily Data Quality Checks
Monitor data entry quality with automated validation runs

### 2. Protocol Compliance
Validate inclusion/exclusion criteria and protocol-specific requirements

### 3. Safety Signal Detection
Automatically flag severe AEs, SAEs, and fatal outcomes

### 4. Pre-Submission Validation
Comprehensive checks before FDA/EMA submission

### 5. Cross-Domain Consistency
Verify subject tracking across multiple domains

---

## 📈 Real-World Examples

### Example 1: Pediatric Study Validation

**Scenario**: Validate pediatric oncology study

**Rules Added**:
```
PROTO001: AGE < 18        → "Pediatric subject - confirmed"
PROTO002: AGE >= 18       → "Adult enrolled - verify eligibility"
PROTO003: AESEV in {'SEVERE'} → "Severe AE - medical review required"
```

### Example 2: Multi-Country Study

**Scenario**: Validate data from 50+ sites across 10 countries

**Rules Added**:
```
PROTO004: COUNTRY is missing  → "Site country required"
PROTO005: SITEID is missing   → "Site ID required for tracking"
```

### Example 3: Safety Monitoring

**Scenario**: Monitor for treatment-emergent adverse events

**Rules Added**:
```
PROTO006: AEREL in {'RELATED','PROBABLE'} → "Drug-related AE"
PROTO007: AEOUT in {'FATAL'}  → "Fatal outcome - urgent review"
```

---

## 🔬 Validation Rules

### CDISC Core Rules (40)

**Demographics (DM)** - 10 rules
- Required identifiers (USUBJID, STUDYID, SUBJID)
- Required dates (RFSTDTC)
- Age validation (range, negative)
- Sex validation
- Site and country tracking

**Adverse Events (AE)** - 7 rules
- Required identifiers and terms
- Start date validation
- Severity and seriousness assessment
- Causality evaluation
- Fatal outcome detection

**Laboratory (LB)** - 5 rules
- Test codes and names
- Collection dates
- Units validation

**Vital Signs (VS)** - 4 rules
- Test codes and names
- Collection dates

**Exposure (EX)** - 4 rules
- Treatment identification
- Start dates
- Dose documentation

**Other Domains** - 10 rules
- CM, MH, DS, SV validations

### Rule Templates (50+)

**Safety Templates**: Severe AEs, SAEs, Fatal outcomes, Drug relationship
**Protocol Templates**: Age eligibility, Exclusion criteria
**Quality Templates**: Missing data, Out-of-range values
**Regulatory Templates**: Required fields per SDTM IG

---

## 📊 Reports & Exports

### Excel Validation Report

**Sheet 1: violations** - Complete violation details
- Columns: source, rule_id, domain, variable, severity, message, condition, row_index, record_key, value
- Sorted: core rules first, then custom rules
- Formatted for easy review

**Sheet 2: summary** - Aggregated statistics
- Grouped by: source, rule_id, severity
- Count of violations per rule
- Useful for executive summary

### CSV Exports

- **Custom Rules**: Backup and documentation
- **Filtered Violations**: Subset for specific analysis
- **Timestamped**: Automatic version control

---

## 🛡️ Best Practices

### Rule Management
1. Use consistent naming convention (CORE###, PROTO###)
2. Document rule purpose in message field
3. Export rules after each update
4. Version control with Git

### Validation Schedule
- **Daily**: Quick checks during data entry
- **Weekly**: Full validation with all rules
- **Pre-Lock**: Comprehensive review before database lock
- **Pre-Submission**: Final validation with documentation

### Severity Guidelines
- **ERROR**: Must be resolved before submission
- **WARNING**: Requires review and documentation
- **INFO**: Informational only, no action required

### Documentation
- Archive validation reports in project folder
- Document accepted warnings in deviation log
- Maintain audit trail of rule changes
- Export violation log for TMF

---

## 🔐 Security & Compliance

### Data Privacy
- ✅ Local processing only (no data sent to external servers)
- ✅ Session-based data storage
- ✅ No persistent storage of uploaded data
- ✅ Automatic cleanup of temporary files

### Audit Trail
- ✅ Timestamped validation runs
- ✅ Rule change tracking
- ✅ Report generation logs
- ✅ Export history

### Regulatory Compliance
- ✅ CDISC SDTM IG v3.4 compliant
- ✅ FDA submission ready
- ✅ 21 CFR Part 11 considerations
- ✅ ICH E6 (R2) alignment

---

## 🤝 Contributing

We welcome contributions! Areas of focus:

- Additional SDTM domain support
- Advanced validation patterns
- Cross-domain checks
- Performance optimizations
- Documentation improvements

---

## 📞 Support

### Documentation
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
- [Rule Templates](app/core/rule_templates.py) - Pre-built rule library
- In-app help - Sidebar "Help & Documentation"

### Issues & Feedback
- GitHub Issues: Bug reports and feature requests
- Email: support@yourdomain.com
- Slack: #sdtm-validation

---

## 📜 License

MIT License - See LICENSE file for details

---

## 🏆 Credits

**Developed for**: Clinical Data Management & SDTM Programming Teams
**Built with**: Streamlit, Pandas, Python
**Standards**: CDISC SDTM Implementation Guide v3.4
**Target**: FDA/EMA Regulatory Submissions

---

## 🔄 Version History

### v2.0 (Current)
- ✨ 4-tab workflow redesign
- ✨ 50+ rule templates
- ✨ Advanced filtering and drill-down
- ✨ Violation tracking system
- ✨ Enhanced UI/UX
- ✨ Production-ready features

### v1.0 (Previous)
- ⚡ Basic validation engine
- ⚡ Custom rule support
- ⚡ Excel reporting

---

## 🚀 Roadmap

### Q1 2024
- [ ] Cross-domain validation rules
- [ ] Automated rule suggestions
- [ ] Batch validation mode
- [ ] API integration

### Q2 2024
- [ ] Advanced date calculations
- [ ] Machine learning anomaly detection
- [ ] Multi-study comparison
- [ ] Cloud deployment option

---

**Ready to ensure SDTM compliance? Get started in 5 minutes!** 🎯

For detailed instructions, see [QUICKSTART.md](QUICKSTART.md)
