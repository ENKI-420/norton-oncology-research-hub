import streamlit as st
import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Constants
FHIR_BASE_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"
OAUTH_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
TRIALS_API_URL = "https://api.3oncologyresearchhub.com/v2/studies"

# Load OpenAI API Key from .env
openai_api_key = os.getenv("OPENAI_API_KEY", "")

# Sidebar Configuration
with st.sidebar:
    st.header("🩺 Norton Oncology Research Hub")
    st.subheader("📌 Navigation")
    
    menu_options = [
        "Chatbot",
        "File Q&A",
        "Chat with Search",
        "Beaker Report Analysis",
        "Genomic AI Analysis",
        "Clinical Trial Matching"
    ]
    selected_option = st.radio("Select a module:", menu_options)

    st.subheader("🔑 OpenAI API Key")
    openai_api_key = st.text_input("Enter your OpenAI API Key", value=openai_api_key, type="password")

    st.subheader("🔗 Quick Links")
    st.markdown("[Get an OpenAI API Key](https://platform.openai.com/account/api-keys)")
    st.markdown("[Epic EHR Integration](https://www.epic.com/)")

# Display selected module
st.title(f"🚀 {selected_option}")
st.caption("AI-driven oncology assistant for research and precision medicine.")

# Epic Authentication Function
def authenticate_epic(username, password):
    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": os.getenv("EPIC_CLIENT_ID", ""),
        "client_secret": os.getenv("EPIC_CLIENT_SECRET", "")
    }
    try:
        response = requests.post(OAUTH_URL, data=payload)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.RequestException as e:
        st.error(f"Epic Authentication Failed: {e}")
        return None

# Fetch Beaker Report
def fetch_beaker_report(patient_id, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}", "Accept": "application/fhir+json"}
    try:
        response = requests.get(f"{FHIR_BASE_URL}DiagnosticReport?patient={patient_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch Beaker Report: {e}")
        return None

# Process Beaker Report
def process_beaker_report(report_data):
    records = report_data.get("entry", [])
    processed = [
        {
            "Test Name": r.get("resource", {}).get("code", {}).get("text", ""),
            "Result": r.get("resource", {}).get("result", ""),
            "Status": r.get("resource", {}).get("status", "")
        } for r in records
    ]
    return pd.DataFrame(processed) if processed else pd.DataFrame(columns=["Test Name", "Result", "Status"])

# AI Treatment Suggestions
def generate_ai_treatment_suggestions(test_results):
    if not openai_api_key:
        st.error("OpenAI API Key is missing. Please provide a valid key.")
        return None
    client =

