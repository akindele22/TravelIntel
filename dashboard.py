"""
Streamlit dashboard for Travel Security / Safety insights.
Manual scraping only (no scheduler, no Playwright).
"""

from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import traceback

import config
from db_factory import DatabaseHandler
from data_cleaner import DataCleaner
from ai_predictor import InsightAnalyzer
from main import run_pipeline  # simplified manual pipeline

# ===============================
# Streamlit config
# ===============================

st.set_page_config(page_title="Travel Security Dashboard", layout="wide")

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
    """Load advisories from database"""
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
    """Add security/safety/serenity flags"""
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
    """Generate textual insights for a country"""
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
    if not (insight.has_security_issues or insight.has_safety_issues or insight.has_serenity_issues):
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
                run_pipeline()
                st.sidebar.success("Pipeline completed.")
                st.cache_data.clear()
                st.experimental_rerun()
            except Exception as e:
                st.sidebar.error(f"Pipeline failed: {e}")
                st.error(traceback.format_exc())

    # --- Filters ---
    st.sidebar.header("Filters")
    country_input = st.sidebar.text_input("Country (optional)", value="")
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
    days_back = st.sidebar.slider("Look back (days)", 30, 730, 365, 30)
    source_filter = None if source_input == "All" else source_input
    country_filter = country_input.strip() or None

    # --- Load & process data ---
    df = load_data(country_filter, source_filter, days_back)
    if df.empty:
        st.info("No advisories found.")
        return
    df = classify_dimensions(df)

    # --- KPIs ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Advisories", len(df))
    col2.metric("High Risk", int((df.get("risk_score", 0) >= 3).sum()))
    col3.metric("Countries", df["country_normalized"].nunique())
    col4.metric("Last Updated", df["date"].max().strftime("%Y-%m-%d"))

    # --- Insights ---
    st.subheader("Location Insights")
    countries = sorted(df["country_normalized"].dropna().unique())
    selected = st.selectbox("Focus country", countries)
    df_country = df[df["country_normalized"] == selected]
    st.markdown(summarize_location(df_country))

    # --- Recent advisories ---
    st.markdown("### Recent Advisories")
    st.dataframe(
        df_country.sort_values("date", ascending=False),
        use_container_width=True
    )

if __name__ == "__main__":
    main()
