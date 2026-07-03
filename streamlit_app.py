import streamlit as st
import pandas as pd
import plotly.express as px

from app.pipeline.diagnosis_pipeline import DiagnosisPipeline

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------

st.set_page_config(
    page_title="Digital Twin AI",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 Digital Twin AI")
st.caption("Evidence-Based Liver Disease Clinical Decision Support")

st.divider()

# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------

st.sidebar.header("Patient")

patient_id = st.sidebar.number_input(
    "Patient ID",
    min_value=1,
    value=1,
    step=1
)

analyze = st.sidebar.button(
    "Analyze Patient",
    use_container_width=True
)

# ---------------------------------------------------
# Run Pipeline
# ---------------------------------------------------

if analyze:

    pipeline = DiagnosisPipeline()

    with st.spinner("Analyzing patient..."):

        result = pipeline.run(patient_id)

    snapshot = result["snapshot"]
    query = result["query"]
    evidence = result["evidence"]
    diagnosis = result["diagnosis"]

    # =====================================================
    # Patient Snapshot
    # =====================================================

    st.header("🩺 Patient Snapshot")

    biomarker_data = []

    biomarkers = snapshot.get("biomarkers", {})

    cols = st.columns(4)

    i = 0

    for biomarker, info in biomarkers.items():

        analytics = info["analytics"]

        if analytics is None:
            continue

        latest = round(analytics["latest"],2)

        change = analytics["percent_change"]

        arrow = "⬆️" if change >= 0 else "⬇️"

        cols[i % 4].metric(
            biomarker.upper(),
            latest,
            f"{change}% {arrow}"
        )

        biomarker_data.append({

            "Biomarker": biomarker.upper(),

            "Latest": latest,

            "Change": change

        })

        i += 1

    st.divider()

    # =====================================================
    # Biomarker Trends
    # =====================================================

    st.header("📈 Biomarker Trends")

    selected = st.selectbox(
        "Choose Biomarker",
        list(biomarkers.keys())
    )

    history = biomarkers[selected]["history"]

    if history:

        df = pd.DataFrame(history)

        df["date"] = pd.to_datetime(df["date"])

        fig = px.line(
            df,
            x="date",
            y="value",
            markers=True,
            title=f"{selected.upper()} Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    # =====================================================
    # Generated Query
    # =====================================================

    st.header("🔍 Generated Clinical Query")

    st.code(query)

    st.divider()

    # =====================================================
    # Retrieved Papers
    # =====================================================

    st.header("📚 Retrieved Evidence")

    if len(evidence) == 0:

        st.warning("No papers retrieved.")

    else:

        for i, paper in enumerate(evidence):

            title = paper.get("paper_title", "Unknown Title")
            journal = paper.get("journal", "")
            pmcid = paper.get("paper_id", "")
            score = paper.get("score", None)
            text = paper.get("text", "")

            with st.expander(f"Paper {i+1}: {title}"):

                st.write(f"**Journal:** {journal}")

                st.write(f"**PMCID:** {pmcid}")

                if score is not None:
                    st.write(f"**Similarity Score:** {score:.3f}")

                st.write(text[:1000] + "...")

    st.divider()

    # =====================================================
    # Diagnosis
    # =====================================================

    st.header("🧠 AI Diagnosis")

    if isinstance(diagnosis, dict):

        c1, c2 = st.columns([3, 1])

        with c1:

            st.subheader(diagnosis.get("diagnosis", ""))

        with c2:

            confidence = diagnosis.get("confidence", 0)

            st.metric(
                "Confidence",
                f"{confidence}%"
            )

        st.markdown("### Reasoning")

        st.write(
            diagnosis.get("reasoning", "")
        )

        st.markdown("### Supporting Biomarkers")

        st.write(
            diagnosis.get(
                "supporting_biomarkers",
                []
            )
        )

        st.markdown("### Recommended Tests")

        st.write(
            diagnosis.get(
                "recommended_tests",
                []
            )
        )

        st.markdown("### Supporting Papers")

        st.write(
            diagnosis.get(
                "supporting_papers",
                []
            )
        )

    else:

        st.write(diagnosis)