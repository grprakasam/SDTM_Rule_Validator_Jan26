"""
Violation Manager - Advanced violation tracking and management
"""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json

from .rules import Violation


@dataclass
class ViolationAnnotation:
    """Annotation for a violation (comments, status, reviewer)"""
    violation_id: str  # Unique identifier for the violation
    status: str  # "New", "Under Review", "Accepted", "Fixed", "False Positive"
    reviewer: str
    comment: str
    timestamp: str
    action_taken: Optional[str] = None


class ViolationManager:
    """Manages violation tracking, annotations, and history"""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.annotations: Dict[str, ViolationAnnotation] = {}
        self.load_annotations()

    def _annotations_path(self) -> Path:
        """Get path to annotations file"""
        return Path("projects") / self.project_name / "violation_annotations.json"

    def load_annotations(self) -> None:
        """Load existing annotations from file"""
        path = self._annotations_path()
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                self.annotations = {
                    k: ViolationAnnotation(**v) for k, v in data.items()
                }
            except Exception:
                self.annotations = {}

    def save_annotations(self) -> None:
        """Save annotations to file"""
        path = self._annotations_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            k: {
                "violation_id": v.violation_id,
                "status": v.status,
                "reviewer": v.reviewer,
                "comment": v.comment,
                "timestamp": v.timestamp,
                "action_taken": v.action_taken,
            }
            for k, v in self.annotations.items()
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_violation_id(self, violation: Violation) -> str:
        """Generate unique ID for a violation"""
        return f"{violation.rule_id}_{violation.domain}_{violation.row_index}"

    def add_annotation(
        self,
        violation: Violation,
        status: str,
        reviewer: str,
        comment: str,
        action_taken: Optional[str] = None,
    ) -> None:
        """Add or update annotation for a violation"""
        violation_id = self.get_violation_id(violation)
        annotation = ViolationAnnotation(
            violation_id=violation_id,
            status=status,
            reviewer=reviewer,
            comment=comment,
            timestamp=datetime.now().isoformat(),
            action_taken=action_taken,
        )
        self.annotations[violation_id] = annotation
        self.save_annotations()

    def get_annotation(self, violation: Violation) -> Optional[ViolationAnnotation]:
        """Get annotation for a violation if it exists"""
        violation_id = self.get_violation_id(violation)
        return self.annotations.get(violation_id)

    def get_violations_by_status(
        self, violations: List[Violation], status: str
    ) -> List[Violation]:
        """Filter violations by annotation status"""
        result = []
        for v in violations:
            annotation = self.get_annotation(v)
            if annotation and annotation.status == status:
                result.append(v)
            elif not annotation and status == "New":
                result.append(v)
        return result

    def get_status_summary(self, violations: List[Violation]) -> Dict[str, int]:
        """Get count of violations by status"""
        summary = {
            "New": 0,
            "Under Review": 0,
            "Accepted": 0,
            "Fixed": 0,
            "False Positive": 0,
        }
        for v in violations:
            annotation = self.get_annotation(v)
            if annotation:
                summary[annotation.status] = summary.get(annotation.status, 0) + 1
            else:
                summary["New"] += 1
        return summary
