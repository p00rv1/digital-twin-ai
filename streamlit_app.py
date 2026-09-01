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

# ---------------------------------------------------
# Patient Selection & Initial Load
# ---------------------------------------------------

from app.snapshot.patient_snapshot import get_patient_snapshot

snapshot = get_patient_snapshot(patient_id)

@st.cache_resource(show_spinner="Loading AI Pipeline & Medical Models...")
def get_pipeline():
    return DiagnosisPipeline()

# ---------------------------------------------------
# Patient Snapshot Header
# ---------------------------------------------------

st.header("🩺 Patient Snapshot")

age = snapshot.get("age", 45)
gender = snapshot.get("gender", "Unknown")

st.caption(f"**Patient ID:** {patient_id} | **Age:** {age} | **Gender:** {gender}")

biomarkers = snapshot.get("biomarkers", {})
cols = st.columns(4)

i = 0
for biomarker, info in biomarkers.items():
    analytics = info["analytics"]
    if analytics is None:
        continue

    latest = round(analytics["latest"], 2)
    change = analytics["percent_change"]
    arrow = "⬆️" if change >= 0 else "⬇️"

    cols[i % 4].metric(
        biomarker.upper(),
        latest,
        f"{change}% {arrow}"
    )
    i += 1

st.divider()

# ---------------------------------------------------
# Clinical Risk & Fibrosis Scoring
# ---------------------------------------------------

st.header("📊 Clinical Risk & Fibrosis Assessment")

clinical_scores = snapshot.get("clinical_scores", {})

r_col1, r_col2, r_col3 = st.columns(3)

with r_col1:
    fib4 = clinical_scores.get("fib4_index")
    fib4_risk = clinical_scores.get("fib4_risk", "N/A")
    st.metric("FIB-4 Index", fib4 if fib4 is not None else "N/A")
    st.caption(f"**Risk Tier:** {fib4_risk}")

with r_col2:
    de_ritis = clinical_scores.get("de_ritis_ratio")
    de_ritis_risk = clinical_scores.get("de_ritis_risk", "N/A")
    st.metric("De Ritis Ratio (AST/ALT)", de_ritis if de_ritis is not None else "N/A")
    st.caption(f"**Pattern:** {de_ritis_risk}")

with r_col3:
    apri = clinical_scores.get("apri_score")
    apri_risk = clinical_scores.get("apri_risk", "N/A")
    st.metric("APRI Score", apri if apri is not None else "N/A")
    st.caption(f"**Risk Tier:** {apri_risk}")

st.divider()

# ---------------------------------------------------
# Biomarker Trends & ML Trajectory Forecasting
# ---------------------------------------------------

st.header("📈 Biomarker Trends & 6-Month Trajectory Projection")

selected = st.selectbox(
    "Choose Biomarker",
    list(biomarkers.keys())
)

history = biomarkers[selected]["history"]
analytics = biomarkers[selected]["analytics"]

if history:
    import plotly.graph_objects as go

    df = pd.DataFrame(history)
    df["date"] = pd.to_datetime(df["date"])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["value"],
        mode='lines+markers',
        name='Historical Lab Value',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))

    if analytics and analytics.get("forecast"):
        forecast = analytics["forecast"]
        last_date = df["date"].iloc[-1]
        last_val = df["value"].iloc[-1]

        f_dates = [last_date, pd.to_datetime(forecast["future_date_90d"]), pd.to_datetime(forecast["future_date_180d"])]
        f_vals = [last_val, forecast["projected_90d"], forecast["projected_180d"]]

        fig.add_trace(go.Scatter(
            x=f_dates,
            y=f_vals,
            mode='lines+markers',
            name=f'ML Projection ({forecast["trajectory"]})',
            line=dict(color='#ff7f0e', width=3, dash='dash'),
            marker=dict(size=8, symbol='diamond')
        ))

    fig.update_layout(
        title=f"{selected.upper()} Historical & Projected Trajectory",
        xaxis_title="Date",
        yaxis_title="Value",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# ---------------------------------------------------
# AI Diagnosis Execution
# ---------------------------------------------------

if analyze:
    status_box = st.status("🧠 Running Clinical AI Pipeline & Hybrid RAG Search...", expanded=True)
    status_box.write("Step 1/3: Loading Medical Models & FAISS Vector Index...")
    pipeline = get_pipeline()

    status_box.write("Step 2/3: Searching PubMed Literature & Re-ranking Evidence...")
    result = pipeline.run(patient_id)
    status_box.write("Step 3/3: Generating Evidence-Based Diagnosis via Groq LLM...")
    status_box.update(label="✅ Clinical AI Pipeline Completed!", state="complete", expanded=False)

    query = result["query"]
    evidence = result["evidence"]
    diagnosis = result["diagnosis"]


    # =====================================================
    # Generated Query
    # =====================================================

    st.header("🔍 Generated Clinical Query")

    st.code(query)

    if result.get("crag_triggered"):
        with st.expander("⚡ Corrective RAG (CRAG) Triggered — Expanded Queries Used"):
            st.info("Initial retrieval relevance score was low (< 0.35). CRAG expanded the search across 3 domain sub-queries:")
            for idx, eq in enumerate(result.get("expanded_queries", []), 1):
                st.write(f"**Sub-query {idx}:** `{eq}`")

    st.divider()

    # =====================================================
    # Retrieved Papers & CRAG Quality Indicator
    # =====================================================

    e_col1, e_col2 = st.columns([3, 1])
    with e_col1:
        st.header("📚 Retrieved Evidence")
    with e_col2:
        quality = result.get("retrieval_quality", "HIGH")
        avg_score = result.get("avg_relevance_score", 0.0)
        st.caption(f"**Retrieval Quality:** `{quality}`")
        if avg_score > 0:
            st.caption(f"**Mean Relevance:** `{avg_score:.3f}`")

    if len(evidence) == 0:
        st.warning("No papers retrieved.")
    else:
        for i, paper in enumerate(evidence):
            title = paper.get("title") or paper.get("paper_title") or "Medical Literature Chunk"
            journal = paper.get("journal", "PubMed Central")
            pmcid = paper.get("pmcid") or paper.get("paper_id") or paper.get("chunk_id", "")
            score = paper.get("rerank_score") if paper.get("rerank_score") is not None else paper.get("score", None)
            text = paper.get("text", "")

            with st.expander(f"Paper {i+1}: {title}"):
                st.write(f"**Journal:** {journal}")
                st.write(f"**PMCID / Chunk ID:** `{pmcid}`")
                if score is not None:
                    st.write(f"**Relevance Score:** `{score:.3f}`")
                st.markdown("**Excerpt:**")
                st.write(text[:1000] + ("..." if len(text) > 1000 else ""))

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
            st.metric("Confidence", f"{confidence}%")

        st.markdown("### Reasoning")
        st.write(diagnosis.get("reasoning", ""))

        st.markdown("### Supporting Biomarkers")
        st.write(diagnosis.get("supporting_biomarkers", []))

        st.markdown("### Recommended Tests")
        st.write(diagnosis.get("recommended_tests", []))

        st.markdown("### Supporting Papers")
        st.write(diagnosis.get("supporting_papers", []))

    else:
        st.write(diagnosis)
