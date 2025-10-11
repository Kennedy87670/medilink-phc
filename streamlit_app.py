"""
MediLink PHC - Streamlit Playground
Lightweight UI to exercise triage (multilingual), forecasting, outbreaks, and resources.
"""

import os
import sys
from typing import Dict, Any, List

import streamlit as st

# Make local src/ importable
sys.path.insert(0, 'src')

from dotenv import load_dotenv
load_dotenv()

try:
    from ai_triage_service_v3 import AITriageServiceV3
except Exception:
    AITriageServiceV3 = None

try:
    from backend_prediction_service import BackendPredictionService
except Exception:
    BackendPredictionService = None


st.set_page_config(page_title="MediLink PHC - Playground", layout="wide")
st.title("🏥 MediLink PHC — Interactive Playground")
st.caption("Test multilingual triage, forecasts, outbreak alerts, and staffing.")


def _set_env_var(name: str, value: str | None):
    if value:
        os.environ[name] = value


with st.sidebar:
    st.header("Settings")

    provider = st.selectbox("AI Provider", ["groq", "gemini"], index=0)
    timeout_s = st.number_input("Timeout (seconds)", min_value=5, max_value=60, value=int(os.getenv("TIMEOUT_SECONDS", 15)))
    max_retries = st.number_input("Max Retries", min_value=0, max_value=5, value=int(os.getenv("MAX_RETRIES", 2)))

    st.subheader("API Keys")
    groq_key = st.text_input("GROQ_API_KEY", value=os.getenv("GROQ_API_KEY", ""), type="password")
    gemini_key = st.text_input("GEMINI_API_KEY", value=os.getenv("GEMINI_API_KEY", ""), type="password")

    # Apply settings to environment so services pick them up
    _set_env_var("PRIMARY_AI_PROVIDER", provider)
    _set_env_var("TIMEOUT_SECONDS", str(timeout_s))
    _set_env_var("MAX_RETRIES", str(max_retries))
    if groq_key:
        _set_env_var("GROQ_API_KEY", groq_key)
    if gemini_key:
        _set_env_var("GEMINI_API_KEY", gemini_key)

    st.markdown("---")
    st.caption("Tip: Keys are read at runtime and not stored.")


def parse_symptoms(text: str) -> List[str]:
    if not text:
        return []
    return [s.strip() for s in text.split(',') if s.strip()]


def render_triage_tab():
    st.subheader("🤖 Multilingual AI Triage")
    col1, col2 = st.columns([2, 1])

    with col1:
        age = st.number_input("Age (years)", min_value=0, max_value=120, value=30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0)
        symptoms_text = st.text_area(
            "Symptoms (comma-separated)",
            placeholder="e.g., zazzabi, body dey pain, ukwu, cough"
        )
        duration = st.text_input("Duration", value="2 days")
        med_history = st.text_input("Medical history (optional)")

        st.markdown("Vitals (optional)")
        v1, v2, v3 = st.columns(3)
        with v1:
            temp = st.number_input("Temperature (°C)", value=0.0, step=0.1)
        with v2:
            hr = st.number_input("Heart Rate (bpm)", value=0, step=1)
        with v3:
            rr = st.number_input("Respiratory Rate (/min)", value=0, step=1)
        v4, v5 = st.columns(2)
        with v4:
            bp_sys = st.number_input("BP Systolic", value=0, step=1)
        with v5:
            bp_dia = st.number_input("BP Diastolic", value=0, step=1)

        vitals: Dict[str, Any] = {}
        if temp > 0:
            vitals["temperature"] = float(temp)
        if hr > 0:
            vitals["heart_rate"] = int(hr)
        if rr > 0:
            vitals["respiratory_rate"] = int(rr)
        if bp_sys > 0 and bp_dia > 0:
            vitals["blood_pressure"] = f"{bp_sys}/{bp_dia}"

        patient = {
            "age": int(age),
            "gender": gender,
            "symptoms": parse_symptoms(symptoms_text),
            "duration": duration,
            "vital_signs": vitals,
        }
        if med_history:
            patient["medical_history"] = med_history

        run = st.button("Analyze Triage", type="primary")

    with col2:
        st.info("The model auto-detects language and translates symptoms.")
        st.code({
            "provider": os.getenv("PRIMARY_AI_PROVIDER"),
            "timeout": os.getenv("TIMEOUT_SECONDS"),
            "retries": os.getenv("MAX_RETRIES")
        }, language="json")

    if run:
        if not AITriageServiceV3:
            st.error("Triage service not available in this environment.")
            return
        if not patient.get("symptoms"):
            st.warning("Please enter at least one symptom.")
            return

        try:
            with st.spinner("Analyzing..."):
                try:
                    service = AITriageServiceV3()
                except TypeError as te:
                    # Common Groq/httpx proxies mismatch
                    if "proxies" in str(te).lower():
                        st.warning("Groq client dependency mismatch (httpx/proxies). Switch provider to 'gemini' in the sidebar or pin httpx==0.27.2.")
                        return
                    raise
                result = service.analyze_patient(patient)

            if result.get("error") and not result.get("ai_failed"):
                st.error(result.get("error"))
                return

            st.success(f"Level {result['triage_level']} — {result['triage_label']}")

            colA, colB, colC = st.columns(3)
            with colA:
                conf = result.get("confidence_score")
                if conf is not None:
                    st.metric("Confidence", f"{conf:.2f}")
                else:
                    st.metric("Confidence", "—")
            with colB:
                st.metric("Response Time (s)", result.get("response_time", 0))
            with colC:
                st.metric("Provider", result.get("provider", os.getenv("PRIMARY_AI_PROVIDER")))

            # Translation info (if available)
            trans = result.get("translation_info", {})
            if trans:
                with st.expander("Translation Details"):
                    st.write("Detected Languages:", trans.get("languages_detected", []))
                    st.write("Original:", trans.get("original_symptoms", []))
                    st.write("Translated:", trans.get("translated_symptoms", []))
                    st.json(trans.get("translation_map", {}))

            # Conditions
            conditions = result.get("conditions", [])
            if conditions:
                st.subheader("Top Conditions")
                st.table([
                    {
                        "name": c.get("name"),
                        "confidence": c.get("confidence"),
                        "reasoning": (c.get("reasoning", "") or "")[:120] + ("..." if c.get("reasoning") else "")
                    }
                    for c in conditions[:3]
                ])

            # Recommendations
            colX, colY = st.columns(2)
            with colX:
                st.subheader("Immediate Actions")
                for a in result.get("immediate_actions", [])[:5]:
                    st.write("-", a)
                st.subheader("Recommended Tests")
                for t in result.get("recommended_tests", [])[:5]:
                    st.write("-", t)
            with colY:
                st.subheader("Referral")
                st.write("Needed:", result.get("referral_needed"))
                if result.get("referral_reason"):
                    st.write(result.get("referral_reason"))
                st.subheader("Warning Signs")
                for w in result.get("warning_signs", [])[:5]:
                    st.write("-", w)

            with st.expander("Raw JSON"):
                st.json(result)

        except Exception as e:
            st.exception(e)


def render_forecast_tab():
    st.subheader("📈 Patient Volume Forecast (7–30 days)")
    if not BackendPredictionService:
        st.info("BackendPredictionService not available in this environment.")
        return
    days = st.slider("Days Ahead", 7, 30, 7)
    run = st.button("Generate Forecast")
    if run:
        service = BackendPredictionService()
        res = service.get_patient_forecast(days_ahead=days)
        if not res.get("success"):
            st.error(res.get("error", {}).get("user_message", "Forecast unavailable."))
            return
        data = res["data"]
        st.write("Period:", data["forecast_period"])
        st.write("Summary:", data["summary"])
        st.dataframe(data["forecast"])


def render_outbreak_tab():
    st.subheader("🚨 Outbreak Detection")
    if not BackendPredictionService:
        st.info("BackendPredictionService not available in this environment.")
        return
    disease = st.text_input("Disease", value="Malaria")
    current = st.number_input("Current Cases", min_value=0, value=25)
    history = st.text_input("Historical Cases (comma-separated)", value="20,22,18,25,21")
    run = st.button("Analyze Outbreak")
    if run:
        try:
            hist = [int(x.strip()) for x in history.split(',') if x.strip()]
        except Exception:
            st.warning("Please enter valid historical counts.")
            return
        service = BackendPredictionService()
        res = service.check_outbreak(disease, "Test Region", current, hist)
        if not res.get("success"):
            st.error(res.get("error", {}).get("user_message", "Unable to analyze outbreak."))
            return
        data = res["data"]
        st.write("Status:", "SEVERE" if data["severity"] == "severe" else ("ALERT" if data["is_outbreak"] else "NORMAL"))
        st.json(data)


def render_resources_tab():
    st.subheader("🧰 Resource Optimization")
    if not BackendPredictionService:
        st.info("BackendPredictionService not available in this environment.")
        return
    patients = st.number_input("Predicted Patients", min_value=0, value=120)
    col1, col2, col3 = st.columns(3)
    with col1:
        nurses = st.number_input("Nurses", min_value=0, value=3)
    with col2:
        doctors = st.number_input("Doctors", min_value=0, value=1)
    with col3:
        pharmacists = st.number_input("Pharmacists", min_value=0, value=1)
    facility = st.selectbox("Facility Type", ["standard", "busy", "rural"], index=0)
    run = st.button("Recommend Resources")
    if run:
        service = BackendPredictionService()
        res = service.recommend_resources(patients, {"nurses": nurses, "doctors": doctors, "pharmacists": pharmacists}, facility)
        if not res.get("success"):
            st.error(res.get("error", {}).get("user_message", "Unable to recommend resources."))
            return
        data = res["data"]
        st.json(data)


tab1, tab2, tab3, tab4 = st.tabs(["Triage", "Forecast", "Outbreak", "Resources"])
with tab1:
    render_triage_tab()
with tab2:
    render_forecast_tab()
with tab3:
    render_outbreak_tab()
with tab4:
    render_resources_tab()

st.markdown("---")
st.caption("Note: Some features depend on local data and installed dependencies (Prophet, pandas).")

# Diagnostics / environment check
with st.expander("Environment & Dependency Check"):
    import importlib
    def _check(mod: str):
        try:
            m = importlib.import_module(mod)
            ver = getattr(m, "__version__", "")
            st.success(f"{mod} ✓ {ver}")
            return True
        except Exception as e:
            st.warning(f"{mod} ✗ ({e})")
            return False

    st.write("Packages:")
    has_pandas = _check("pandas")
    has_prophet = _check("prophet")
    _check("groq")
    _check("google.generativeai")
    _check("httpx")

    st.write("Data:")
    import os as _os
    pv = _os.path.exists("data/patient_visits.csv")
    if pv:
        st.success("data/patient_visits.csv ✓")
    else:
        st.warning("data/patient_visits.csv ✗ (needed for forecast)")

    st.write("API Keys:")
    groq_ok = bool(_os.getenv("GROQ_API_KEY"))
    gem_ok = bool(_os.getenv("GEMINI_API_KEY"))
    st.write("GROQ_API_KEY:", "✓" if groq_ok else "—")
    st.write("GEMINI_API_KEY:", "✓" if gem_ok else "—")
