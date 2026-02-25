"""
Streamlit dashboard for Travel Security / Safety insights.
Production-ready version with background pipeline scheduler.
"""

from datetime import datetime, timedelta,UTC
import pandas as pd
import streamlit as st
import threading
import time
import traceback

import config
from db_factory import DatabaseHandler
from data_cleaner import DataCleaner
from ai_predictor import InsightAnalyzer
from main import TravelAdvisoryPipeline


# ===============================
# CONFIG
# ===============================

PIPELINE_INTERVAL_HOURS = 3
PIPELINE_INTERVAL_SECONDS = PIPELINE_INTERVAL_HOURS * 60 * 60


st.set_page_config(page_title="Travel Security Dashboard", layout="wide")


# ===============================
# BACKGROUND PIPELINE SCHEDULER
# ===============================

def pipeline_scheduler():
    """
    Runs pipeline every X hours in background thread.
    """
    while True:
        try:
           print(f"[{datetime.now(UTC)}] Running pipeline...")
            pipeline = TravelAdvisoryPipeline()
            pipeline.run_full_pipeline()
            print(f"[{datetime.now(UTC)}] Pipeline finished successfully.")
        except Exception:
            print("Pipeline error:")
            traceback.print_exc()

        print(f"Sleeping {PIPELINE_INTERVAL_HOURS} hours...")
        time.sleep(PIPELINE_INTERVAL_SECONDS)


def start_pipeline_once():
    """
    Ensures background scheduler starts only once.
    Prevents duplicate threads on Streamlit reruns.
    """
    if "pipeline_thread_started" not in st.session_state:
        thread = threading.Thread(
            target=pipeline_scheduler,
            daemon=True
        )
        thread.start()
        st.session_state.pipeline_thread_started = True
        print("Background scheduler started.")


# Start scheduler immediately
start_pipeline_once()


# ===============================
# SHOW DATABASE INFO (SIDEBAR)
# ===============================

try:
    dbconf = config.DATABASE_CONFIG
    st.sidebar.markdown("**DB:** {}@{}:{}".format(
        dbconf.get('database',''),
        dbconf.get('host',''),
        dbconf.get('port','')
    ))
except Exception:
    pass


# ===============================
# DATA LOADING
# ===============================

@st.cache_data(show_spinner=False)
def load_data(country_filter=None, source_filter=None, days_back: int = 365):
    try:
        db = DatabaseHandler()
        advisories = db.get_advisories(
            country=country_filter,
            source=source_filter,
            limit=5000,
        )
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
    finally:
        try:
            db.close()
        except Exception:
            pass

    if not advisories:
        return pd.DataFrame()

    cleaner = DataCleaner()
    cleaned = cleaner.clean_batch(advisories)
    df = cleaner.create_dataframe(cleaned)

    cutoff = datetime.utcnow() - timedelta(days=days_back)
    if "date" in df.columns:
        df = df[df["date"] >= cutoff]

    return df


def classify_dimensions(df: pd.DataFrame) -> pd.DataFrame:
    analyzer = InsightAnalyzer()

    def row_fn(row: pd.Series):
        return analyzer._classify_dimensions_row(row)

    dims = df.apply(row_fn, axis=1, result_type="expand")

    for col in ['security', 'safety', 'serenity']:
        if col in dims.columns:
            dims[col] = dims[col].astype(bool)

    return pd.concat([df, dims], axis=1)


# ===============================
# LOCATION SUMMARY
# ===============================

def summarize_location(df_country: pd.DataFrame) -> str:
    if df_country.empty:
        return "No recent advisories for this location."

    analyzer = InsightAnalyzer()
    records = df_country.to_dict(orient="records")
    example_country = df_country["country_normalized"].iloc[0]
    insight = analyzer.summarize_country(records, example_country)

    if not insight:
        return "No recent advisories for this location."

    parts = []

    grade = insight.risk_grade or "U"
    parts.append(f"Overall risk rating: **{grade}** ({insight.risk_level_text}).")

    if insight.has_security_issues:
        parts.append("**Security** issues reported.")
    if insight.has_safety_issues:
        parts.append("**Safety** issues reported.")
    if insight.has_serenity_issues:
        parts.append("**Serenity** impacted.")
    if (
        not insight.has_security_issues
        and not insight.has_safety_issues
        and not insight.has_serenity_issues
    ):
        parts.append("No major concerns mentioned.")

    if insight.latest_summary:
        parts.append(f'Most recent advisory: “{insight.latest_summary}”')

    if insight.security_highlights:
        parts.append("\n**Security highlights:**")
        for h in insight.security_highlights:
            parts.append(f"- {h}")

    if insight.dos:
        parts.append("\n**Do's:**")
        for d in insight.dos:
            parts.append(f"- {d}")

    if insight.donts:
        parts.append("\n**Don'ts:**")
        for d in insight.donts:
            parts.append(f"- {d}")

    return "\n".join(parts)


# ===============================
# MAIN UI
# ===============================

def main():
    st.title("🌍 Travel Security & Safety Dashboard")

    # --- Manual Pipeline Trigger ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Data Pipeline")

    if st.sidebar.button("🔄 Run Pipeline Now"):
        with st.spinner("Running pipeline..."):
            try:
                pipeline = TravelAdvisoryPipeline()
                pipeline.run_full_pipeline()
                st.sidebar.success("Pipeline completed.")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Pipeline failed: {e}")

    st.sidebar.header("Filters")

    country_input = st.sidebar.text_input(
        "Country (optional)", value=""
    )

    source_input = st.sidebar.selectbox(
        "Source",
        options=[
            "All",
            "US State Department",
            "UK FCDO",
            "Smart Traveller (Australia)",
            "IATA Travel Centre",
            "Canada Travel",
        ],
    )

    days_back = st.sidebar.slider(
        "Look back (days)", 30, 730, 365, 30
    )

    source_filter = None if source_input == "All" else source_input
    country_filter = country_input.strip() or None

    df = load_data(country_filter, source_filter, days_back)

    if df.empty:
        st.info("No advisories found.")
        return

    df = classify_dimensions(df)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Advisories", len(df))
    col2.metric("High Risk", int((df.get("risk_score", 0) >= 3).sum()))
    col3.metric("Countries", df["country_normalized"].nunique())
    col4.metric("Last Updated", df["date"].max().strftime("%Y-%m-%d"))

    st.subheader("Location Insights")

    countries = sorted(df["country_normalized"].dropna().unique())
    selected = st.selectbox("Focus country", countries)

    df_country = df[df["country_normalized"] == selected]

    st.markdown(summarize_location(df_country))

    st.markdown("### Recent Advisories")
    st.dataframe(
        df_country.sort_values("date", ascending=False),
        use_container_width=True
    )


if __name__ == "__main__":
    main()
