# Quick Start Guide - SDTM Validation Platform

## 🚀 Getting Started in 5 Minutes

### Step 1: Installation (1 minute)

```bash
# Install required packages
pip install -r requirements.txt
```

### Step 2: Launch Application (30 seconds)

```bash
# Start the validation platform
streamlit run app/main.py
```

The app will open automatically in your browser at `http://localhost:8501`

### Step 3: Load Sample Data (1 minute)

1. Go to **Tab 1: Data Loading**
2. Click **"📥 Load Sample Data"** button
3. Wait for CDISC sample datasets to download (27 domains)
4. View domain summary in the expandable section

### Step 4: Configure Project (30 seconds)

In the **Sidebar**:
- **Project ID**: Change from "STUDY-001" to your study number
- **Protocol Number**: Update to your protocol
- **Custom Rules**: Keep enabled (default)

### Step 5: Add Custom Rules (2 minutes)

1. Go to **Tab 2: Rule Configuration**
2. **Browse Template Library** (right panel):
   - Filter by category: "Adverse Events (AE)"
   - Click "➕ Add AE001" for severe AE detection
   - Copy the displayed values
3. **Add to Rule Editor** (left panel):
   - Click "+ Add row" in the data editor
   - Paste values from template
4. Click **"💾 Save Rules"**

### Step 6: Run Validation (1 minute)

1. Go to **Tab 3: Run Validation**
2. Click **"▶️ Run Validation"** button
3. Wait for validation to complete (5-10 seconds)
4. View results summary (Errors/Warnings/Info counts)
5. Click **"📥 Download Full Validation Report"**

### Step 7: Analyze Results (Optional)

1. Go to **Tab 4: Results Analysis**
2. Use filters to focus on specific issues:
   - Filter by Severity: Select "ERROR" only
   - Filter by Domain: Select "DM", "AE"
3. Use **"🔍 Drill-Down by Domain"** to view violating records
4. Export filtered results as CSV

---

## 📚 What You Get Out of the Box

### ✅ 40 CDISC Core Rules
Pre-configured rules covering:
- **DM (Demographics)**: 10 rules - USUBJID, AGE, SEX, RFSTDTC validation
- **AE (Adverse Events)**: 7 rules - Fatal outcomes, severity, dates
- **LB (Laboratory)**: 5 rules - Test codes, dates, units
- **VS (Vital Signs)**: 4 rules - Test codes, dates
- **EX (Exposure)**: 4 rules - Treatment, dates, dose
- **CM (Conmeds)**: 2 rules - Medication name validation
- **MH (Medical History)**: 2 rules - History terms
- **DS (Disposition)**: 3 rules - Disposition events
- **SV (Subject Visits)**: 3 rules - Visit tracking

### ✅ 50+ Rule Templates
Pre-built templates for common scenarios:
- Safety signal detection
- Protocol compliance checks
- Data quality validation
- Regulatory requirements

### ✅ Production Features
- Excel report generation with multiple sheets
- Violation tracking and annotation
- CSV export for data team
- Domain-level drill-down
- Session state management

---

## 💡 Common Workflows

### Workflow 1: Daily Data QC (15 minutes)

```
1. Load overnight SDTM exports
2. Run validation with existing rules
3. Filter to ERROR severity only
4. Export violations to CSV
5. Send to SDTM programmers
```

### Workflow 2: Protocol-Specific Rules (30 minutes)

```
1. Review protocol inclusion/exclusion criteria
2. Browse template library for relevant checks
3. Add 5-10 custom rules for:
   - Age eligibility
   - Concomitant medication restrictions
   - Lab value thresholds
4. Save and document rules
5. Run validation and review
```

### Workflow 3: Pre-Submission Check (1 hour)

```
1. Load all final SDTM domains
2. Ensure all ERROR violations resolved
3. Document accepted WARNINGs
4. Generate final validation report
5. Archive report for submission package
6. Export violation log for TMF
```

### Workflow 4: Safety Review (20 minutes)

```
1. Go to Tab 4: Results Analysis
2. Filter: Severity = ERROR, WARNING
3. Filter: Domain = AE
4. Review all serious AEs
5. Drill-down to see patient records
6. Export AE violations for medical monitor
```

---

## 🎯 Real-World Examples

### Example 1: Flag Elderly Subjects

**Use Case**: Protocol excludes subjects >75 years

**Solution**: Add custom rule
```
ID: PROTO001
Domain: DM
Variable: AGE
Condition: AGE > 75
Severity: ERROR
Message: Subject exceeds protocol age limit (75 years)
```

### Example 2: Detect Treatment-Related SAEs

**Use Case**: Identify serious AEs related to study drug

**Solution**: Use templates AE004 + AE006, or create:
```
ID: PROTO002
Domain: AE
Variable: AESER
Condition: AESER in {'Y'}
Severity: WARNING
Message: Serious adverse event requires medical review
```

### Example 3: Lab Value Safety Thresholds

**Use Case**: Flag elevated liver enzymes (ALT >3x ULN)

**Solution**: Add custom rule
```
ID: PROTO003
Domain: LB
Variable: LBSTRESN
Condition: LBSTRESN > 3
Severity: WARNING
Message: ALT elevated >3x upper limit normal
```

Note: This assumes LBSTRESN is normalized to ULN multiples

### Example 4: Visit Window Compliance

**Use Case**: Ensure visits occur within protocol windows

**Solution**: Add custom rule
```
ID: PROTO004
Domain: SV
Variable: SVSTDY
Condition: SVSTDY > 14
Severity: WARNING
Message: Visit occurred outside protocol window (Day 14)
```

---

## 📖 Understanding Rule Syntax

### Basic Patterns

#### 1. Missing Value Checks
```
USUBJID is missing          # Detects empty/null values
RFSTDTC not missing         # Ensures field is populated
```

#### 2. Comparison Operators
```
AGE > 120                   # Greater than
WEIGHT < 30                 # Less than
VISITNUM >= 1               # Greater than or equal
BMI <= 40                   # Less than or equal
SEX == 'M'                  # Equals
COUNTRY != 'USA'            # Not equals
```

#### 3. Set Membership
```
AESEV in {'SEVERE','MODERATE'}         # Value must be in set
RACE in {'WHITE','BLACK','ASIAN'}      # Multiple options
ARMCD in {'TRT','PLACEBO'}             # Treatment arms
```

#### 4. Range Checks
```
AGE between 18 and 65       # Inclusive range
VISITNUM between 1 and 12   # Visit range
BMI between 18.5 and 30     # Numeric range
```

### Advanced Examples

#### Multi-Condition Logic (Future Enhancement)
Currently not supported, but you can create multiple rules:

```
Rule 1: AGE < 18 → "Pediatric subject - verify eligibility"
Rule 2: AGE >= 18 → "Adult subject - standard protocol"
```

#### Date-Based Rules (Future Enhancement)
For now, use study day variables:

```
AESTDY < 1                  # AE before treatment start
SVSTDY > 365                # Visit after 1 year
```

---

## 🛠️ Troubleshooting

### Issue: "Domain not found"
**Solution**: Ensure XPT file is named correctly (DM.xpt, not Demographics.xpt)

### Issue: "Variable not found"
**Solution**: Check variable name spelling and case (must be uppercase: USUBJID not usubjid)

### Issue: Validation is slow
**Solution**:
- Large datasets (>100K records) may take 30-60 seconds
- Consider validating domains individually first
- Check if too many rules are configured (>100 total)

### Issue: Template not appearing
**Solution**:
- Reload the page (Ctrl+R)
- Check domain filter - template may be filtered out
- Verify domain is loaded in Tab 1

### Issue: Excel report won't download
**Solution**:
- Check browser download settings
- Ensure sufficient disk space
- Try CSV export as alternative

---

## 📊 Report Structure

### Excel Report Contents

**Sheet 1: violations**
- All violations with full details
- Sorted by: source (core → custom), severity, domain, row
- Columns: source, rule_id, domain, variable, severity, message, condition, row_index, record_key, value

**Sheet 2: summary**
- Aggregated counts by rule and severity
- Useful for high-level review
- Columns: source, rule_id, severity, count

### CSV Export (Filtered)
- Subset of violations based on selected filters
- Same column structure as Excel violations sheet
- Timestamped filename for version control

---

## 🔐 Best Practices

### 1. Project Organization
```
projects/
  ├── STUDY-001/
  │   ├── custom_rules.json
  │   └── runs/
  │       ├── 20240108_120000/
  │       │   └── validation_report.xlsx
  │       └── 20240108_140000/
  │           └── validation_report.xlsx
  ├── STUDY-002/
  └── STUDY-003/
```

### 2. Rule Naming Convention
```
CORE### - CDISC core rules (don't modify)
PROTO### - Protocol-specific rules
SITE### - Site-specific rules
TEMP### - Temporary/test rules
```

### 3. Severity Guidelines
- **ERROR**: Violations that prevent submission (missing required fields, invalid values)
- **WARNING**: Issues requiring review but may be acceptable (missing optional fields, outliers)
- **INFO**: Informational flags (study milestones, safety signals)

### 4. Documentation
- Export rules to CSV after each update
- Save validation reports in project folder
- Document accepted warnings in protocol deviation log
- Keep audit trail of rule changes

### 5. Validation Schedule
- **Daily**: Quick validation during data entry
- **Weekly**: Full validation with all rules
- **Pre-Lock**: Comprehensive validation before database lock
- **Pre-Submission**: Final validation with full documentation

---

## 🎓 Training Resources

### For Data Managers
1. Review Tab 1-3 workflow
2. Practice with sample data
3. Learn common rule patterns
4. Understand severity levels

### For SDTM Programmers
1. Focus on Tab 4 drill-down features
2. Learn to interpret rule conditions
3. Practice CSV export workflow
4. Understand violation resolution

### For Medical Monitors
1. Focus on safety-related templates
2. Learn AE filtering and drill-down
3. Review severity assessment
4. Practice exporting for review

### For Study Managers
1. Understand project configuration
2. Review validation reports structure
3. Learn documentation requirements
4. Practice submission workflow

---

## 📞 Getting Help

### In-App Help
- Check sidebar **"Help & Documentation"** section
- Review **"Rule Syntax Examples"** in Tab 2
- Use template descriptions in Template Library

### Documentation
- `README.md` - Overview and installation
- `VALIDATION_WORKFLOWS.md` - Detailed workflow guides
- `RULE_SYNTAX.md` - Complete syntax reference

### Support
- GitHub Issues: Report bugs and request features
- Email: support@yourdomain.com
- Slack: #sdtm-validation channel

---

## 🚀 Next Steps

1. **Customize for your study**:
   - Update project settings in sidebar
   - Add protocol-specific rules
   - Configure severity levels

2. **Integrate with workflow**:
   - Schedule regular validation runs
   - Set up data pipeline
   - Configure report distribution

3. **Train your team**:
   - Run training session
   - Create SOPs
   - Document procedures

4. **Monitor and improve**:
   - Track common violations
   - Refine rules based on feedback
   - Build template library

---

**Ready to validate? Start with sample data and explore the features!** 🎯
