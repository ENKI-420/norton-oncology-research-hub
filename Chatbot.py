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

# Sidebar Configuration for Norton Oncology Research Hub
with st.sidebar:
    st.header("🩺 Norton Oncology Research Hub")

    # Navigation menu
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

    # OpenAI API Key input (preloaded from .env but allows manual override)
    st.subheader("🔑 OpenAI API Key")
    openai_api_key = st.text_input("Enter your OpenAI API Key", value=openai_api_key, type="password")

    # Quick Links
    st.subheader("🔗 Quick Links")
    st.markdown("[Get an OpenAI API Key](https://platform.openai.com/account/api-keys)")
    st.markdown("[View the Source Code](https://github.com/agiledefensesystems/norton-oncology-chatbot)")
    st.markdown("[Epic EHR Integration](https://www.epic.com/)")

# Display selected module
st.title(f"🚀 {selected_option}")
st.caption("AI-driven oncology assistant for research, clinical insights, and precision medicine.")

# Epic Authentication Function
def authenticate_epic(username, password):
    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": os.getenv("EPIC_CLIENT_ID", ""),
        "client_secret": os.getenv("EPIC_CLIENT_SECRET", "")
    }
    response = requests.post(OAUTH_URL, data=payload)
    if response.status_code == 200:
        return response.json().get("access_token")
    st.error("Epic Authentication Failed")
    return None

# Fetch Beaker Report
def fetch_beaker_report(patient_id, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}", "Accept": "application/fhir+json"}
    response = requests.get(f"{FHIR_BASE_URL}DiagnosticReport?patient={patient_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    st.error("Failed to fetch Beaker Report")
    return None

# Process Beaker Report
def process_beaker_report(report_data):
    records = report_data.get("entry", [])
    processed = [{"Test Name": r.get("resource", {}).get("code", {}).get("text", ""),
                  "Result": r.get("resource", {}).get("result", ""),
                  "Status": r.get("resource", {}).get("status", "")} for r in records]
    return pd.DataFrame(processed)

# AI-Powered Treatment Suggestions
def generate_ai_treatment_suggestions(test_results):
    client = OpenAI(api_key=openai_api_key)
    prompt = f"Analyze these oncology test results and provide treatment suggestions:\n{test_results.to_string(index=False)}"
    response = client.completions.create(model="gpt-4-turbo", prompt=prompt, max_tokens=500)
    return response.choices[0].text.strip()

# Fetch Clinical Trials
def fetch_clinical_trials():
    response = requests.get(TRIALS_API_URL)
    if response.status_code == 200:
        return response.json()
    return None

# Epic Login UI
st.subheader("🔐 Epic EHR Login (Optional)")
epic_username = st.text_input("Epic Username")
epic_password = st.text_input("Epic Password", type="password")
if st.button("Login to Epic"):
    token = authenticate_epic(epic_username, epic_password)
    if token:
        st.session_state["auth_token"] = token
        st.success("Epic Authentication Successful")

# AI Chatbot
st.subheader("💬 AI-Powered Oncology Chatbot")
if prompt := st.text_area("Ask a question about cancer treatment, trials, or genomic analysis"):
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(model="gpt-4-turbo", messages=[{"role": "user", "content": prompt}])
    st.write("### 🤖 AI Response")
    st.write(response.choices[0].message.content)

# Beaker Report Section
st.subheader("📊 Fetch & Analyze Beaker Report")
patient_id = st.text_input("Enter Patient ID for Beaker Report")
if st.button("Fetch Report"):
    auth_token = st.session_state.get("auth_token")
    if auth_token:
        report_data = fetch_beaker_report(patient_id, auth_token)
        if report_data:
            test_results = process_beaker_report(report_data)
            st.dataframe(test_results)
            st.write("### 🤖 AI-Powered Treatment Insights")
            ai_response = generate_ai_treatment_suggestions(test_results)
            st.write(ai_response)
    else:
        st.error("Please log in to Epic first.")

# Clinical Trial Matching Section
st.subheader("🔬 AI-Driven Clinical Trial Matching")
if st.button("Find Clinical Trials"):
    trial_data = fetch_clinical_trials()
    if trial_data:
        st.json(trial_data)
    else:
        st.error("No trials found.")

st.caption("🔗 Powered by Agile Defense Systems | Norton Oncology | Epic EHR | AI-Driven Precision Medicine")
