import json
import os
from typing import Any, Dict

import streamlit as st

from app.database.models import Opportunity
from app.product.product_schema import ProductBlueprint, DESIGN_DIRECTIONS


def _get_api_key() -> str:
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.getenv("GEMINI_API_KEY", "")


def recommend_product_type(opportunity: Opportunity) -> str:
    formats = " ".join(opportunity.format).lower()
    if "planner" in formats or "tracker" in formats:
        return "Planner"
    if "checklist" in formats:
        return "Checklist"
    if "workspace" in formats or "workflow" in formats:
        return "Workbook"
    return "Playbook"


def _fallback_blueprint(opportunity: Opportunity, product_type: str) -> Dict[str, Any]:
    return {
        "title": opportunity.name,
        "subtitle": opportunity.value_hook or opportunity.promise,
        "audience": opportunity.audience,
        "core_problem": opportunity.promise,
        "desired_outcome": "A clear, repeatable next step with less research and rework.",
        "promise": opportunity.promise,
        "sections": ["Start Here", "Core Workflow", "Execution Workspace", "Troubleshooting", "Results Review"],
        "estimated_pages": 20,
        "exercises": ["Five-minute diagnostic", "Weekly review checklist"],
        "checklists": ["Definition of done checklist"],
        "bonuses": ["Quick-start checklist", "One-page reference sheet"],
        "design_direction": "Minimal Professional",
    }


def generate_blueprint(opportunity: Opportunity, product_type: str) -> ProductBlueprint:
    api_key = _get_api_key()
    data = None
    if api_key:
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = (
                "You are a product strategist. Based on this research opportunity, design a "
                f"{product_type}.\n\n"
                f"Opportunity name: {opportunity.name}\n"
                f"Audience: {opportunity.audience}\n"
                f"Promise: {opportunity.promise}\n"
                f"Value hook: {opportunity.value_hook}\n"
                f"Format ideas: {', '.join(opportunity.format)}\n"
                f"Objection bucket: {opportunity.objection_bucket}\n\n"
                "Return ONLY a JSON object with these exact keys, no extra text, no markdown fences: "
                "title, subtitle, audience, core_problem, desired_outcome, promise, "
                "sections (list of 5-8 section names), estimated_pages (integer), "
                "exercises (list), checklists (list), bonuses (list), "
                f"design_direction (one of: {', '.join(DESIGN_DIRECTIONS)}).\n\n"
                "Do not claim guaranteed sales or demand. Treat this as a research-backed hypothesis."
            )
            response = model.generate_content(prompt)
            text = (response.text or "").strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.lower().startswith("json"):
                    text = text[4:]
            data = json.loads(text)
        except Exception:
            data = None
    if not data:
        data = _fallback_blueprint(opportunity, product_type)
    data["opportunity_name"] = opportunity.name
    data["product_type"] = product_type
    if data.get("design_direction") not in DESIGN_DIRECTIONS:
        data["design_direction"] = "Minimal Professional"
    return ProductBlueprint(**data)
