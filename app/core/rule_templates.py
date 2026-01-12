"""
SDTM Validation Rule Templates
Common validation patterns used in clinical data validation
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class RuleTemplate:
    id: str
    name: str
    category: str
    description: str
    domain: str
    variable: str
    condition: str
    severity: str
    message: str
    tags: List[str]


# CDISC SDTM Rule Templates organized by category
RULE_TEMPLATES: Dict[str, List[RuleTemplate]] = {
    "Demographics (DM)": [
        RuleTemplate(
            id="DM001",
            name="Missing Subject ID",
            category="Demographics (DM)",
            description="Check for missing unique subject identifier",
            domain="DM",
            variable="USUBJID",
            condition="USUBJID is missing",
            severity="ERROR",
            message="Subject unique identifier is required",
            tags=["critical", "demographics", "identifier"]
        ),
        RuleTemplate(
            id="DM002",
            name="Invalid Age Range",
            category="Demographics (DM)",
            description="Check if subject age is within acceptable range",
            domain="DM",
            variable="AGE",
            condition="AGE > 120",
            severity="ERROR",
            message="Age exceeds biologically plausible maximum (120 years)",
            tags=["demographics", "age", "data-quality"]
        ),
        RuleTemplate(
            id="DM003",
            name="Pediatric Subject Check",
            category="Demographics (DM)",
            description="Flag subjects under 18 years for pediatric protocols",
            domain="DM",
            variable="AGE",
            condition="AGE < 18",
            severity="WARNING",
            message="Pediatric subject - verify protocol eligibility",
            tags=["demographics", "age", "protocol"]
        ),
        RuleTemplate(
            id="DM004",
            name="Missing Sex",
            category="Demographics (DM)",
            description="Sex is required for demographics",
            domain="DM",
            variable="SEX",
            condition="SEX is missing",
            severity="ERROR",
            message="Sex is required for all subjects",
            tags=["demographics", "required"]
        ),
        RuleTemplate(
            id="DM005",
            name="Invalid Sex Code",
            category="Demographics (DM)",
            description="Sex must be M, F, or U per CDISC CT",
            domain="DM",
            variable="SEX",
            condition="SEX not in {'M','F','U'}",
            severity="ERROR",
            message="Sex must be M (Male), F (Female), or U (Unknown)",
            tags=["demographics", "controlled-terminology"]
        ),
        RuleTemplate(
            id="DM006",
            name="Missing Reference Start Date",
            category="Demographics (DM)",
            description="Reference start date is required",
            domain="DM",
            variable="RFSTDTC",
            condition="RFSTDTC is missing",
            severity="ERROR",
            message="Reference start date is required for all subjects",
            tags=["demographics", "dates", "required"]
        ),
        RuleTemplate(
            id="DM007",
            name="Invalid ARM Code",
            category="Demographics (DM)",
            description="ARM code should not be missing for randomized subjects",
            domain="DM",
            variable="ARM",
            condition="ARM is missing",
            severity="WARNING",
            message="Treatment arm is missing - verify if subject was randomized",
            tags=["demographics", "randomization"]
        ),
    ],
    "Adverse Events (AE)": [
        RuleTemplate(
            id="AE001",
            name="Severe AE Check",
            category="Adverse Events (AE)",
            description="Flag all severe adverse events for review",
            domain="AE",
            variable="AESEV",
            condition="AESEV in {'SEVERE'}",
            severity="WARNING",
            message="Severe adverse event reported - requires medical review",
            tags=["adverse-events", "safety", "severe"]
        ),
        RuleTemplate(
            id="AE002",
            name="Missing AE Start Date",
            category="Adverse Events (AE)",
            description="AE start date is required",
            domain="AE",
            variable="AESTDTC",
            condition="AESTDTC is missing",
            severity="ERROR",
            message="Adverse event start date is required",
            tags=["adverse-events", "dates", "required"]
        ),
        RuleTemplate(
            id="AE003",
            name="Fatal Outcome Check",
            category="Adverse Events (AE)",
            description="Flag all adverse events with fatal outcome",
            domain="AE",
            variable="AEOUT",
            condition="AEOUT in {'FATAL'}",
            severity="ERROR",
            message="Fatal adverse event - requires immediate SAE reporting",
            tags=["adverse-events", "safety", "fatal", "critical"]
        ),
        RuleTemplate(
            id="AE004",
            name="Serious AE Flag",
            category="Adverse Events (AE)",
            description="Flag all serious adverse events",
            domain="AE",
            variable="AESER",
            condition="AESER in {'Y'}",
            severity="WARNING",
            message="Serious adverse event - verify SAE reporting completed",
            tags=["adverse-events", "safety", "serious"]
        ),
        RuleTemplate(
            id="AE005",
            name="Missing AE Term",
            category="Adverse Events (AE)",
            description="Adverse event term is required",
            domain="AE",
            variable="AETERM",
            condition="AETERM is missing",
            severity="ERROR",
            message="Adverse event verbatim term is required",
            tags=["adverse-events", "required"]
        ),
        RuleTemplate(
            id="AE006",
            name="Related to Study Drug",
            category="Adverse Events (AE)",
            description="Flag AEs related to study drug",
            domain="AE",
            variable="AEREL",
            condition="AEREL in {'RELATED','PROBABLE','POSSIBLE'}",
            severity="INFO",
            message="Adverse event possibly related to study drug",
            tags=["adverse-events", "causality", "study-drug"]
        ),
    ],
    "Laboratory (LB)": [
        RuleTemplate(
            id="LB001",
            name="Out of Range High",
            category="Laboratory (LB)",
            description="Flag lab values above normal range",
            domain="LB",
            variable="LBNRIND",
            condition="LBNRIND in {'HIGH','H'}",
            severity="INFO",
            message="Lab result above normal range",
            tags=["laboratory", "out-of-range"]
        ),
        RuleTemplate(
            id="LB002",
            name="Out of Range Low",
            category="Laboratory (LB)",
            description="Flag lab values below normal range",
            domain="LB",
            variable="LBNRIND",
            condition="LBNRIND in {'LOW','L'}",
            severity="INFO",
            message="Lab result below normal range",
            tags=["laboratory", "out-of-range"]
        ),
        RuleTemplate(
            id="LB003",
            name="Missing Lab Result",
            category="Laboratory (LB)",
            description="Lab result value is required when test performed",
            domain="LB",
            variable="LBSTRESN",
            condition="LBSTRESN is missing",
            severity="WARNING",
            message="Lab result value is missing",
            tags=["laboratory", "missing-data"]
        ),
        RuleTemplate(
            id="LB004",
            name="Missing Lab Units",
            category="Laboratory (LB)",
            description="Units are required for numeric lab results",
            domain="LB",
            variable="LBSTRESU",
            condition="LBSTRESU is missing",
            severity="WARNING",
            message="Lab result units are missing",
            tags=["laboratory", "units"]
        ),
    ],
    "Vital Signs (VS)": [
        RuleTemplate(
            id="VS001",
            name="High Blood Pressure",
            category="Vital Signs (VS)",
            description="Flag potentially dangerous systolic BP",
            domain="VS",
            variable="VSSTRESN",
            condition="VSSTRESN > 180",
            severity="WARNING",
            message="Systolic BP >180 mmHg - verify if clinically significant",
            tags=["vital-signs", "blood-pressure", "safety"]
        ),
        RuleTemplate(
            id="VS002",
            name="Low Blood Pressure",
            category="Vital Signs (VS)",
            description="Flag potentially dangerous low BP",
            domain="VS",
            variable="VSSTRESN",
            condition="VSSTRESN < 80",
            severity="WARNING",
            message="Systolic BP <80 mmHg - verify if clinically significant",
            tags=["vital-signs", "blood-pressure", "safety"]
        ),
        RuleTemplate(
            id="VS003",
            name="Missing Vital Sign Value",
            category="Vital Signs (VS)",
            description="Result value required when vital sign performed",
            domain="VS",
            variable="VSSTRESN",
            condition="VSSTRESN is missing",
            severity="WARNING",
            message="Vital sign value is missing",
            tags=["vital-signs", "missing-data"]
        ),
        RuleTemplate(
            id="VS004",
            name="High Heart Rate",
            category="Vital Signs (VS)",
            description="Flag tachycardia",
            domain="VS",
            variable="VSSTRESN",
            condition="VSSTRESN > 120",
            severity="WARNING",
            message="Heart rate >120 bpm - possible tachycardia",
            tags=["vital-signs", "heart-rate", "safety"]
        ),
    ],
    "Exposure (EX)": [
        RuleTemplate(
            id="EX001",
            name="Missing Exposure Start Date",
            category="Exposure (EX)",
            description="Start date required for all exposures",
            domain="EX",
            variable="EXSTDTC",
            condition="EXSTDTC is missing",
            severity="ERROR",
            message="Exposure start date is required",
            tags=["exposure", "dates", "required"]
        ),
        RuleTemplate(
            id="EX002",
            name="Missing Dose",
            category="Exposure (EX)",
            description="Dose amount required for exposure records",
            domain="EX",
            variable="EXDOSE",
            condition="EXDOSE is missing",
            severity="ERROR",
            message="Exposure dose is required",
            tags=["exposure", "dose", "required"]
        ),
        RuleTemplate(
            id="EX003",
            name="Missing Dose Units",
            category="Exposure (EX)",
            description="Dose units required when dose specified",
            domain="EX",
            variable="EXDOSU",
            condition="EXDOSU is missing",
            severity="ERROR",
            message="Exposure dose units are required",
            tags=["exposure", "dose", "units"]
        ),
    ],
    "Concomitant Medications (CM)": [
        RuleTemplate(
            id="CM001",
            name="Missing Medication Name",
            category="Concomitant Medications (CM)",
            description="Medication name is required",
            domain="CM",
            variable="CMTRT",
            condition="CMTRT is missing",
            severity="ERROR",
            message="Concomitant medication name is required",
            tags=["conmeds", "required"]
        ),
        RuleTemplate(
            id="CM002",
            name="Missing Start Date",
            category="Concomitant Medications (CM)",
            description="Medication start date should be recorded",
            domain="CM",
            variable="CMSTDTC",
            condition="CMSTDTC is missing",
            severity="WARNING",
            message="Concomitant medication start date is missing",
            tags=["conmeds", "dates"]
        ),
    ],
    "Medical History (MH)": [
        RuleTemplate(
            id="MH001",
            name="Missing Medical History Term",
            category="Medical History (MH)",
            description="Medical history term is required",
            domain="MH",
            variable="MHTERM",
            condition="MHTERM is missing",
            severity="ERROR",
            message="Medical history term is required",
            tags=["medical-history", "required"]
        ),
    ],
    "Disposition (DS)": [
        RuleTemplate(
            id="DS001",
            name="Study Discontinuation",
            category="Disposition (DS)",
            description="Flag all study discontinuations",
            domain="DS",
            variable="DSDECOD",
            condition="DSDECOD in {'DISCONTINUED','WITHDRAWN'}",
            severity="INFO",
            message="Subject discontinued from study",
            tags=["disposition", "discontinuation"]
        ),
    ],
}


def get_all_templates() -> List[RuleTemplate]:
    """Get all rule templates as a flat list"""
    all_templates = []
    for category_templates in RULE_TEMPLATES.values():
        all_templates.extend(category_templates)
    return all_templates


def get_templates_by_category(category: str) -> List[RuleTemplate]:
    """Get rule templates for a specific category"""
    return RULE_TEMPLATES.get(category, [])


def get_templates_by_domain(domain: str) -> List[RuleTemplate]:
    """Get all rule templates for a specific domain"""
    all_templates = get_all_templates()
    return [t for t in all_templates if t.domain.upper() == domain.upper()]


def get_templates_by_tag(tag: str) -> List[RuleTemplate]:
    """Get all rule templates matching a specific tag"""
    all_templates = get_all_templates()
    return [t for t in all_templates if tag.lower() in [t.lower() for t in t.tags]]


def get_template_categories() -> List[str]:
    """Get list of all template categories"""
    return list(RULE_TEMPLATES.keys())
