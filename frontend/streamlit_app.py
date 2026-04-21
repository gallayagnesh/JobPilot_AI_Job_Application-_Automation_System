import streamlit as st
import requests
import pandas as pd

st.title("🚀 AI Job Automation Dashboard")

API_URL = "http://127.0.0.1:8000"

# Fetch jobs from backend
def fetch_jobs():
    try:
        response = requests.get(f"{API_URL}/jobs")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error("Failed to fetch jobs")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"API connection error: {e}")
        return pd.DataFrame()


df = fetch_jobs()

# DISPLAY DATA
if not df.empty:

    st.subheader("📊 All Jobs")
    st.dataframe(df)

    # Sort by score
    if "final_score" in df.columns:
        df = df.sort_values(by="final_score", ascending=False)

    # Filters
    st.subheader("🎯 Filter Jobs")

    filter_option = st.selectbox(
        "Select Decision Type",
        ["ALL", "AUTO_APPLY", "REVIEW_AND_CUSTOMIZE", "IGNORE"]
    )

    if filter_option != "ALL":
        df = df[df["decision"] == filter_option]

    st.dataframe(df)
else:
    st.warning("No jobs found")

# 🔥 HIGHLIGHT HIGH PRIORITY

st.subheader("🔥 Auto Apply Jobs")

auto_jobs = df[df["decision"] == "AUTO_APPLY"]

if not auto_jobs.empty:
    st.dataframe(auto_jobs)
else:
    st.info("No high-priority jobs yet")

# 🧠 ADD MANUAL JOB INPUT (POWER FEATURE)
st.subheader("➕ Add New Job")

jd = st.text_area("Paste Job Description")

if st.button("Process Job"):
    response = requests.post(
        f"{API_URL}/process-job",
        params={"job_description": jd}
    )

    if response.status_code == 200:
        st.success("Job processed successfully!")
        st.json(response.json())
        st.rerun()
    else:
        st.error("Processing failed")