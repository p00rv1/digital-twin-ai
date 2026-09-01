from statistics import mean
from datetime import datetime, timedelta
import math

from app.services.history_service import (
    get_history
)


def predict_biomarker_trajectory(history):
    """
    Fits a linear time-series regression model on historical lab dates
    to project biomarker values for +90 days (+3 months) and +180 days (+6 months).
    """
    if not history or len(history) == 0:
        return None

    if len(history) == 1:
        val = float(history[0][1])
        return {
            "projected_90d": round(val, 2),
            "projected_180d": round(val, 2),
            "slope": 0.0,
            "trajectory": "Stable ➡️",
            "future_date_90d": (history[0][0] + timedelta(days=90)).strftime("%Y-%m-%d"),
            "future_date_180d": (history[0][0] + timedelta(days=180)).strftime("%Y-%m-%d")
        }

    # Extract dates and float values
    raw_dates = [row[0] for row in history]
    values = [float(row[1]) for row in history]

    base_date = raw_dates[0]
    days = [(d - base_date).days for d in raw_dates]

    n = len(days)
    mean_d = sum(days) / n
    mean_v = sum(values) / n

    numerator = sum((days[i] - mean_d) * (values[i] - mean_v) for i in range(n))
    denominator = sum((days[i] - mean_d) ** 2 for i in range(n))

    slope = (numerator / denominator) if denominator != 0 else 0.0
    intercept = mean_v - (slope * mean_d)

    latest_day = days[-1]
    latest_date = raw_dates[-1]

    day_90 = latest_day + 90
    day_180 = latest_day + 180

    proj_90 = max(0.0, slope * day_90 + intercept)
    proj_180 = max(0.0, slope * day_180 + intercept)

    if slope > 0.02:
        trajectory = "Rapidly Increasing ⬆️" if slope > 0.1 else "Gradually Increasing ↗️"
    elif slope < -0.02:
        trajectory = "Rapidly Decreasing ⬇️" if slope < -0.1 else "Gradually Decreasing ↘️"
    else:
        trajectory = "Stable ➡️"

    return {
        "projected_90d": round(proj_90, 2),
        "projected_180d": round(proj_180, 2),
        "slope": round(slope, 4),
        "trajectory": trajectory,
        "future_date_90d": (latest_date + timedelta(days=90)).strftime("%Y-%m-%d"),
        "future_date_180d": (latest_date + timedelta(days=180)).strftime("%Y-%m-%d")
    }


def compute_clinical_scores(patient_age, latest_biomarkers):
    """
    Computes clinical liver fibrosis and risk scores:
    1. De Ritis Ratio (AST / ALT)
    2. FIB-4 Index (if Platelets available or estimated)
    3. APRI Score (if Platelets available)
    """
    ast = latest_biomarkers.get("ast")
    alt = latest_biomarkers.get("alt")
    platelets = latest_biomarkers.get("platelets") or latest_biomarkers.get("platelet_count")

    scores = {}

    # De Ritis Ratio (AST / ALT)
    if ast and alt and alt > 0:
        de_ritis = round(ast / alt, 2)
        if de_ritis > 2.0:
            de_ritis_risk = "High Risk (Severe Alcoholic Hepatitis / Cirrhosis Pattern) 🔴"
        elif de_ritis >= 1.0:
            de_ritis_risk = "Moderate Risk (Chronic Hepatitis / Fibrosis Progression) 🟡"
        else:
            de_ritis_risk = "Low Risk (Normal or Mild NAFLD Pattern) 🟢"

        scores["de_ritis_ratio"] = de_ritis
        scores["de_ritis_risk"] = de_ritis_risk
    else:
        scores["de_ritis_ratio"] = None
        scores["de_ritis_risk"] = "N/A"

    # FIB-4 Index
    age = patient_age if patient_age else 45
    if ast and alt and alt > 0:
        plt = platelets if platelets and platelets > 0 else 220.0  # standard mean fallback if unrecorded
        fib4 = (age * ast) / (plt * math.sqrt(alt))
        fib4 = round(fib4, 2)

        if fib4 < 1.45:
            fib4_risk = "Low Risk (Stage F0 - F1 Fibrosis) 🟢"
        elif fib4 <= 3.25:
            fib4_risk = "Indeterminate / Moderate Risk (Stage F2 Fibrosis) 🟡"
        else:
            fib4_risk = "High Risk (Advanced Fibrosis / Stage F3-F4 Cirrhosis) 🔴"

        scores["fib4_index"] = fib4
        scores["fib4_risk"] = fib4_risk
        scores["platelets_used"] = round(plt, 1)
    else:
        scores["fib4_index"] = None
        scores["fib4_risk"] = "N/A"

    # APRI Score
    if ast:
        plt = platelets if platelets and platelets > 0 else 220.0
        apri = ((ast / 40.0) / plt) * 100.0
        apri = round(apri, 2)

        if apri < 0.5:
            apri_risk = "Low Risk of Significant Fibrosis 🟢"
        elif apri <= 1.5:
            apri_risk = "Moderate Risk of Fibrosis 🟡"
        else:
            apri_risk = "High Risk of Cirrhosis 🔴"

        scores["apri_score"] = apri
        scores["apri_risk"] = apri_risk

    return scores


def get_biomarker_analytics(
    patient_id,
    biomarker
):
    history = get_history(
        patient_id,
        biomarker
    )

    if not history:
        return None

    values = [
        float(row[1])
        for row in history
    ]

    first = values[0]
    latest = values[-1]

    change = (
        ((latest - first) / first) * 100
        if first != 0
        else 0
    )

    forecast = predict_biomarker_trajectory(history)

    return {
        "biomarker": biomarker,
        "first": round(first, 2),
        "latest": round(latest, 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "mean": round(mean(values), 2),
        "percent_change": round(
            change,
            2
        ),
        "forecast": forecast
    }

