import streamlit as st
import requests

st.title("AI Resume Customizer")

jd = st.text_area("Paste Job Description")

if st.button("Generate Resume"):

    r = requests.post(
        "http://127.0.0.1:8001/generate-resume",
        params={"job_description": jd}
    )

    data = r.json()

    st.download_button(
        "Download PDF",
        open(data["pdf_path"], "rb"),
        file_name="tailored_resume.pdf"
    )

    st.text_area("Preview", data["resume_text"], height=500)