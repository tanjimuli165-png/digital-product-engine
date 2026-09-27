import streamlit as st

from app.database.db import ReportStore
from app.database.models import Report, Opportunity
from app.product.product_schema import PRODUCT_TYPES, DESIGN_DIRECTIONS
from app.product.strategy import generate_blueprint, recommend_product_type


def render_product_builder(report: Report, opportunity: Opportunity, store: ReportStore, user_id: str | None) -> None:
    st.divider()
    st.subheader(f"Product Builder — {opportunity.name}")

    recommended = recommend_product_type(opportunity)
    default_index = PRODUCT_TYPES.index(recommended) if recommended in PRODUCT_TYPES else 0
    st.caption(f"Recommended type: **{recommended}** (based on this opportunity's suggested format)")
    product_type = st.selectbox("Choose product type", PRODUCT_TYPES, index=default_index, key="product_type_select")

    if st.button("Generate Product Blueprint", key="generate_blueprint_btn"):
        with st.spinner("Designing product blueprint..."):
            blueprint = generate_blueprint(opportunity, product_type)
        st.session_state["current_blueprint"] = blueprint.model_dump()

    blueprint_data = st.session_state.get("current_blueprint")
    if blueprint_data:
        st.markdown("#### Review blueprint (edit anything before approving)")
        blueprint_data["title"] = st.text_input("Title", blueprint_data.get("title", ""), key="bp_title")
        blueprint_data["subtitle"] = st.text_input("Subtitle", blueprint_data.get("subtitle", ""), key="bp_subtitle")
        blueprint_data["audience"] = st.text_area("Audience", blueprint_data.get("audience", ""), height=70, key="bp_audience")
        blueprint_data["core_problem"] = st.text_area("Core problem", blueprint_data.get("core_problem", ""), height=70, key="bp_problem")
        blueprint_data["desired_outcome"] = st.text_area("Desired outcome", blueprint_data.get("desired_outcome", ""), height=70, key="bp_outcome")

        sections_text = st.text_area("Sections (one per line)", "\n".join(blueprint_data.get("sections", [])), height=140, key="bp_sections")
        blueprint_data["sections"] = [line.strip() for line in sections_text.splitlines() if line.strip()]

        blueprint_data["estimated_pages"] = st.number_input("Estimated pages", min_value=1, max_value=200, value=int(blueprint_data.get("estimated_pages", 20) or 20), key="bp_pages")

        exercises_text = st.text_area("Exercises (one per line)", "\n".join(blueprint_data.get("exercises", [])), height=90, key="bp_exercises")
        blueprint_data["exercises"] = [line.strip() for line in exercises_text.splitlines() if line.strip()]

        bonuses_text = st.text_area("Bonuses (one per line)", "\n".join(blueprint_data.get("bonuses", [])), height=90, key="bp_bonuses")
        blueprint_data["bonuses"] = [line.strip() for line in bonuses_text.splitlines() if line.strip()]

        current_design = blueprint_data.get("design_direction", "Minimal Professional")
        design_index = DESIGN_DIRECTIONS.index(current_design) if current_design in DESIGN_DIRECTIONS else 0
        blueprint_data["design_direction"] = st.selectbox("Design direction", DESIGN_DIRECTIONS, index=design_index, key="bp_design")

        st.caption("Research-backed product concept — an evidence-supported hypothesis, not a guaranteed seller.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Regenerate blueprint", key="regen_blueprint_btn"):
                with st.spinner("Regenerating..."):
                    blueprint = generate_blueprint(opportunity, product_type)
                st.session_state["current_blueprint"] = blueprint.model_dump()
                st.rerun()
        with col2:
            if st.button("Approve blueprint", key="approve_blueprint_btn"):
                report.generated_products.append(dict(blueprint_data))
                store.save(report, user_id=user_id)
                st.session_state["current_blueprint"] = None
                st.success("Blueprint approved and saved. Content generation is the next step to build.")
