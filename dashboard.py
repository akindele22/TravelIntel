"""
TravelIntel Production Dashboard
Read-only UI connected to PostgreSQL
"""

import os
from datetime import datetime

import pandas as pd
import psycopg2
import streamlit as st
from psycopg2.extras import RealDictCursor


# ----------------------------
# CONFIG
# ----------------------------

st.set_page_config(
    page_title="TravelIntel Dashboard",
    layout="wide",
)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    st.error("DATABASE_URL not configured.")
    st.stop()


# ----------------------------
# DATABASE CONNECTION
# ----------------------------

def get_connection():
    return psycopg2.connect(DATABASE_URL)


# ✅ NEW: Connection Test Block
def test_connection():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0]
    except Exception as e:
        return str(e)


# Show connection status in sidebar
st.sidebar.header("Database Status")
connection_status = test_connection()

if isinstance(connection_status, str):
    st.sidebar.error(f"Connection Failed: {connection_status}")
    st.stop()
else:
    st.sidebar.success("Database Connected")
    st.sidebar.caption(f"Connected at: {connection_status}")


@st.cache_data(ttl=300)
def fetch_advisories(country=None, source=None, days_back=365):
    """Fetch advisories from PostgreSQL with filters"""

    query = """
        SELECT
            country_normalized,
            risk_level_normalized,
            risk_score,
            sentiment_score,
            source,
            created_at
        FROM advisories
        WHERE created_at >= NOW() - INTERVAL %s
    """

    params = [f"{days_back} days"]

    if country:
        query += " AND country_normalized ILIKE %s"
        params.append(f"%{country}%")

    if source:
        query += " AND source = %s"
        params.append(source)

    query += " ORDER BY created_at DESC LIMIT 2000"

    conn = get_connection()
    try:
        df = pd.read_sql(query, conn, params=params)
    finally:
        conn.close()

    return df


# ----------------------------
# SIDEBAR FILTERS
# ----------------------------

st.sidebar.header("Filters")

country_input = st.sidebar.text_input("Country (optional)")
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
    "Look back (days)",
    min_value=30,
    max_value=730,
    value=365,
    step=30,
)

source_filter = None if source_input == "All" else source_input
country_filter = country_input.strip() or None


# ----------------------------
# LOAD DATA
# ----------------------------

with st.spinner("Loading data..."):
    df = fetch_advisories(
        country=country_filter,
        source=source_filter,
        days_back=days_back,
    )


# ----------------------------
# UI DISPLAY
# ----------------------------

st.title("🌍 Travel Intelligence Dashboard")

if df.empty:
    st.warning("No advisories found for selected filters.")
    st.stop()


col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Advisories", len(df))

with col2:
    st.metric("Countries Covered", df["country_normalized"].nunique())

with col3:
    avg_risk = round(df["risk_score"].mean(), 2)
    st.metric("Average Risk Score", avg_risk)


st.divider()

st.subheader("Risk Distribution")

risk_counts = df["risk_level_normalized"].value_counts()
st.bar_chart(risk_counts)


st.divider()

st.subheader("Recent Advisories")

st.dataframe(
    df.sort_values("created_at", ascending=False),
    use_container_width=True,
)


st.caption(
    f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
)
