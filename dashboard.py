"""
Streamlit dashboard for Travel Security / Safety insights.

Run with:
    streamlit run dashboard.py
"""

from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import config
import subprocess

from db_factory import DatabaseHandler
from data_cleaner import DataCleaner
from ai_predictor import InsightAnalyzer
# nlp_vectorizer import removed because the dashboard doesn't actually use it;
# keeping it here previously forced a dependency on scikit-learn during
# startup.  NLP features are exercised in separate validation/tests.


st.set_page_config(page_title="Travel Security Dashboard", layout="wide")

# show which database configuration we're using (helpful in deployment)
try:
    dbconf = config.DATABASE_CONFIG
    st.sidebar.markdown("**DB:** {}@{}:{}".format(
        dbconf.get('database',''),
        dbconf.get('host',''),
        dbconf.get('port','')
    ))
except Exception:
    pass


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
        # show error in UI for easier debugging when DB isn't reachable
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
        return analyzer._classify_dimensions_row(row)  # internal helper, but fine for UI

    dims = df.apply(row_fn, axis=1, result_type="expand")
    # Ensure boolean columns are actual booleans
    for col in ['security', 'safety', 'serenity']:
        if col in dims.columns:
            dims[col] = dims[col].astype(bool)
    return pd.concat([df, dims], axis=1)


def summarize_location(df_country: pd.DataFrame) -> str:
    if df_country.empty:
        return "No recent advisories for this location."

    analyzer = InsightAnalyzer()
    # convert back to list-of-dicts for the analyzer API
    records = df_country.to_dict(orient="records")
    example_country = df_country["country_normalized"].iloc[0]
    insight = analyzer.summarize_country(records, example_country)
    if not insight:
        return "No recent advisories for this location."

    parts = []

    # Overall grade + textual risk level
    grade = insight.risk_grade or "U"
    parts.append(f"Overall risk rating: **{grade}** ({insight.risk_level_text}).")

    if insight.has_security_issues:
        parts.append("**Security** issues reported (crime / terrorism / unrest).")
    if insight.has_safety_issues:
        parts.append("**Safety** issues reported (health / disasters / accidents).")
    if insight.has_serenity_issues:
        parts.append(
            "**Serenity** impacted (protests / strikes / political tension)."
        )
    if (
        not insight.has_security_issues
        and not insight.has_safety_issues
        and not insight.has_serenity_issues
    ):
        parts.append(
            "No major security / safety / serenity issues explicitly mentioned in recent advisories."
        )

    if insight.latest_summary:
        parts.append(
            f'Most recent advisory summary: “{insight.latest_summary}”'
        )

    # Security highlights
    if insight.security_highlights:
        parts.append("\n**Key security highlights:**")
        for h in insight.security_highlights:
            parts.append(f"- {h}")

    # Do's and Don'ts
    if insight.dos:
        parts.append("\n**Do's (recommended actions):**")
        for d in insight.dos:
            parts.append(f"- {d}")

    if insight.donts:
        parts.append("\n**Don'ts (what to avoid):**")
        for d in insight.donts:
            parts.append(f"- {d}")

    return "\n".join(parts)


def main():
    st.title("Travel Security & Safety Dashboard")

        
    # --- Manual Pipeline Trigger ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Data Pipeline")
    
    if st.sidebar.button("🔄 Run Scraper Now"):
        with st.spinner("Running scraper... this may take a minute."):
            try:
                result = subprocess.run(
                    ["python", "run_all.py"],
                    capture_output=True,
                    text=True
                )
    
                if result.returncode == 0:
                    st.sidebar.success("Scraping completed successfully.")
                    st.cache_data.clear()  # clear cached data
                    st.rerun()
                else:
                    st.sidebar.error("Scraper failed.")
                    st.sidebar.text(result.stderr)
    
            except Exception as e:
                st.sidebar.error(f"Error running scraper: {e}")

    # the DataCleaner will silently fall back to dummy analyzers/lemmatizers
    # when optional dependencies are missing; no need to clutter the UI with
    # warnings.  downstream code can inspect `.sentiment_enabled` or
    # `.lemmatizer_enabled` if it really cares.
    try:
        _ = DataCleaner()
    except Exception:
        # ignore, load_data will handle errors later
        pass

    st.sidebar.header("Filters")

    country_input = st.sidebar.text_input(
        "Country (optional, partial name allowed)", value=""
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
        "Look back (days)", min_value=30, max_value=730, value=365, step=30
    )

    source_filter = None if source_input == "All" else source_input
    country_filter = country_input if country_input.strip() else None

    df = load_data(
        country_filter=country_filter,
        source_filter=source_filter,
        days_back=days_back,
    )

    if df.empty:
        st.info("No advisories found for the selected filters.")
        return

    df = classify_dimensions(df)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Advisories (filtered)", len(df))

    with col2:
        n_high = (df.get("risk_score", 0) >= 3).sum()
        st.metric("High/Very High Risk", int(n_high))

    with col3:
        st.metric("Countries covered", df["country_normalized"].nunique())

    with col4:
        latest_date = df["date"].max()
        st.metric(
            "Last updated",
            latest_date.strftime("%Y-%m-%d") if pd.notna(latest_date) else "N/A",
        )

    st.subheader("Location insights")

    all_countries = sorted(df["country_normalized"].dropna().unique())
    default_country = all_countries[0] if all_countries else None

    country_focus = st.selectbox(
        "Focus country",
        options=all_countries,
        index=all_countries.index(default_country)
        if default_country in all_countries
        else 0,
    )

    df_country = df[df["country_normalized"] == country_focus]

    st.markdown(f"### {country_focus}: Risk Rating & Guidance")
    st.markdown(summarize_location(df_country))

    st.markdown("### Concern Categories (this country)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sec_count = (df_country.get("has_security_concerns", False)).sum()
        st.metric("🛡️ Security Concerns", int(sec_count))
    
    with col2:
        safe_count = (df_country.get("has_safety_concerns", False)).sum()
        st.metric("⚕️ Safety Concerns", int(safe_count))
    
    with col3:
        ser_count = (df_country.get("has_serenity_concerns", False)).sum()
        st.metric("☮️ Serenity Concerns", int(ser_count))

    st.markdown("### Risk level distribution (this country)")
    if "risk_level_normalized" in df_country.columns:
        st.bar_chart(
            df_country["risk_level_normalized"].value_counts().sort_index()
        )

    st.markdown("### Top Keywords (this country)")
    # Extract keywords from all descriptions
    all_keywords = []
    for keywords_list in df_country.get("keywords", []):
        if isinstance(keywords_list, list):
            all_keywords.extend(keywords_list)
    
    if all_keywords:
        keyword_counts = pd.Series(all_keywords).value_counts().head(15)
        st.bar_chart(keyword_counts)
    else:
        st.info("No keywords extracted yet.")

    st.markdown("### Recent advisories (this country)")
    cols_to_show = [
        "source",
        "risk_level_normalized",
        "risk_score",
        "date",
        "keywords",
        "has_security_concerns",
        "has_safety_concerns",
        "has_serenity_concerns",
        "description_cleaned",
    ]
    cols_existing = [c for c in cols_to_show if c in df_country.columns]
    
    display_df = df_country[cols_existing].sort_values("date", ascending=False).reset_index(drop=True)
    
    # Format boolean columns with emojis
    if "has_security_concerns" in display_df.columns:
        display_df["has_security_concerns"] = display_df["has_security_concerns"].apply(
            lambda x: "🛡️ Yes" if x else "✓"
        )
    if "has_safety_concerns" in display_df.columns:
        display_df["has_safety_concerns"] = display_df["has_safety_concerns"].apply(
            lambda x: "⚕️ Yes" if x else "✓"
        )
    if "has_serenity_concerns" in display_df.columns:
        display_df["has_serenity_concerns"] = display_df["has_serenity_concerns"].apply(
            lambda x: "☮️ Yes" if x else "✓"
        )
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
    )

    st.markdown("### Global risk by country (filtered dataset)")
    if "risk_score" in df.columns:
        country_risk = (
            df.groupby("country_normalized")["risk_score"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )
        st.bar_chart(country_risk.set_index("country_normalized"))

    st.markdown("### Global Concern Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sec_global = (df.get("has_security_concerns", False)).sum()
        pct_sec = (sec_global / len(df) * 100) if len(df) > 0 else 0
        st.metric("🛡️ Security Issues (%)", f"{pct_sec:.1f}%")
    
    with col2:
        safe_global = (df.get("has_safety_concerns", False)).sum()
        pct_safe = (safe_global / len(df) * 100) if len(df) > 0 else 0
        st.metric("⚕️ Safety Issues (%)", f"{pct_safe:.1f}%")
    
    with col3:
        ser_global = (df.get("has_serenity_concerns", False)).sum()
        pct_ser = (ser_global / len(df) * 100) if len(df) > 0 else 0
        st.metric("☮️ Serenity Issues (%)", f"{pct_ser:.1f}%")


if __name__ == "__main__":
    main()

