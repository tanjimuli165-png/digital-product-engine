from typing import List
from pydantic import BaseModel, Field

PRODUCT_TYPES = [
    "Ebook",
    "Playbook",
    "Workbook",
    "Planner",
    "Checklist",
    "Guide",
    "Journal",
    "Tracker",
    "Action Plan",
    "Challenge",
    "Template",
    "Worksheet",
]

DESIGN_DIRECTIONS = ["Minimal Professional", "Modern Business", "Clean Workbook"]


class ProductBlueprint(BaseModel):
    opportunity_name: str
    product_type: str
    title: str
    subtitle: str = ""
    audience: str
    core_problem: str
    desired_outcome: str
    promise: str
    sections: List[str] = Field(default_factory=list)
    estimated_pages: int = 20
    exercises: List[str] = Field(default_factory=list)
    checklists: List[str] = Field(default_factory=list)
    bonuses: List[str] = Field(default_factory=list)
    design_direction: str = "Minimal Professional"
    disclaimer: str = "Research-backed product concept — an evidence-supported hypothesis, not a guaranteed seller."
