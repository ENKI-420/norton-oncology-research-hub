import streamlit as st
import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv
import openai
from openai import OpenAI
import openai.error  # for APIConnectionError and other exceptions

# Load environment variables
load_dotenv()

# Constants
FHIR_BASE_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"
OAUTH_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
TRIALS_API_URL = "https://api.3oncologyresearchhub.com/v2/studies"  # Placeholder or Mock

# Retrieve OpenAI API key from environment
openai_api_key = os.getenv("OPENAI_API_KEY", "")

# -------------------------------------------
# Hotkey / Auto-Advance Options
# -------------------------------------------
AUTO_ADVANCE_OPTIONS = {
    "Alt+N": "Proceed to Next Step",
    "Alt+R": "Refine Current Output",
    "Alt+E": "Expand Feature",
    "Alt+Q": "Quick Deploy to Production"
}

def display_hotkeys():
    """Displays hotkey info in the sidebar."""
    st.sidebar.markdown("### ⚡ Hotkey Auto-Advance Options")
    for hk, desc in AUTO_ADVANCE_OPTIONS.items():
        st.sidebar.write(f"- **{hk}**: {desc}")

# -------------------------------------------
# Streamlit App Layout
# -------------------------------------------
with st.sidebar:
    st.header("🩺 Norton Oncology Research Hub")

    # Show hotkey hints
    display_hotkeys()

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

st.title(f"🚀 {selected_option}")
st.caption("AI-driven oncology assistant for research, clinical insights, and precision medicine.")

# -------------------------------------------
# Epic Authentication & Data Fetching
# -------------------------------------------
def authenticate_epic(username, password):
    """Authenticate to Epic and return a valid token, or None if failed."""
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

def fetch_beaker_report(patient_id, auth_token):
    """Fetch a patient's Beaker Report from Epic."""
    headers = {"Authorization": f"Bearer {auth_token}", "Accept": "application/fhir+json"}
    response = requests.get(f"{FHIR_BASE_URL}DiagnosticReport?patient={patient_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    st.error("Failed to fetch Beaker Report")
    return None

def process_beaker_report(report_data):
    """Extract and format relevant fields from Beaker Report data."""
    records = report_data.get("entry", [])
    processed = []
    for r in records:
        resource = r.get("resource", {})
        test_name = resource.get("code", {}).get("text", "")
        result = resource.get("result", "")
        status = resource.get("status", "")
        processed.append({"Test Name": test_name, "Result": result, "Status": status})
    return pd.DataFrame(processed)

# -------------------------------------------
# OpenAI Helper
# -------------------------------------------
def get_ai_chat_response(user_prompt: str, api_key: str) -> str:
    """
    Safely get a GPT-based response from OpenAI. Returns a short string 
    if an error occurs, letting the app handle feedback gracefully.
    """
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.choices[0].message.content

    except openai.error.APIConnectionError:
        st.error("❌ Unable to connect to the OpenAI API. Check your API key/network.")
        return "Connection Error"

    except openai.error.OpenAIError as e:
        st.error(f"❌ OpenAI Error: {str(e)}")
        return "OpenAI Error"

    except Exception as general_exception:
        st.error(f"❌ An unexpected error occurred: {general_exception}")
        return "Unexpected Error"

# -------------------------------------------
# AI-Powered Treatment Suggestions
# -------------------------------------------
def generate_ai_treatment_suggestions(test_results_df):
    """
    Use OpenAI's GPT-based model to generate suggestions based on test results.
    Error handling is built into get_ai_chat_response().
    """
    formatted_results = test_results_df.to_string(index=False)
    prompt = (
        "Analyze these oncology test results and provide treatment suggestions:\n"
        f"{formatted_results}"
    )
    return get_ai_chat_response(prompt, openai_api_key)

# -------------------------------------------
# Clinical Trials (Placeholder or Mock)
# -------------------------------------------
def fetch_clinical_trials():
    """
    Attempt to fetch clinical trials from a placeholder API.
    If the request fails, return a mock dataset to showcase functionality.
    """
    try:
        response = requests.get(TRIALS_API_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.warning("Received an unexpected status code from the Trials API. Using mock data instead.")
    except requests.exceptions.RequestException:
        st.warning("Failed to connect to the Trials API (placeholder). Using mock data instead.")

    # Mock data to demonstrate table rendering
    mock_data = {
        "trials": [
            {
                "trial_id": "MOCK-001",
                "condition": "Breast Cancer",
                "phase": "Phase II",
                "location": "Norton Cancer Institute",
                "status": "Recruiting"
            },
            {
                "trial_id": "MOCK-002",
                "condition": "Lung Cancer",
                "phase": "Phase III",
                "location": "Norton Specialty Center",
                "status": "Active, Not Recruiting"
            }
        ]
    }
    return mock_data

# -------------------------------------------
# Epic Login UI
# -------------------------------------------
st.subheader("🔐 Epic EHR Login (Optional)")
epic_username = st.text_input("Epic Username")
epic_password = st.text_input("Epic Password", type="password")
if st.button("Login to Epic"):
    token = authenticate_epic(epic_username, epic_password)
    if token:
        st.session_state["auth_token"] = token
        st.success("Epic Authentication Successful")

# -------------------------------------------
# AI Chatbot
# -------------------------------------------
st.subheader("💬 AI-Powered Oncology Chatbot")
user_prompt = st.text_area("Ask a question about cancer treatment, trials, or genomic analysis")
if st.button("Get AI Response"):
    if user_prompt.strip():
        ai_response = get_ai_chat_response(user_prompt, openai_api_key)
        if ai_response not in ["Connection Error", "OpenAI Error", "Unexpected Error"]:
            st.write("### 🤖 AI Response")
            st.write(ai_response)
    else:
        st.warning("Please enter a question before asking for a response.")

# -------------------------------------------
# Beaker Report Section
# -------------------------------------------
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
            if ai_response not in ["Connection Error", "OpenAI Error", "Unexpected Error"]:
                st.write(ai_response)
    else:
        st.error("Please log in to Epic first.")

# -------------------------------------------
# Clinical Trial Matching Section
# -------------------------------------------
st.subheader("🔬 AI-Driven Clinical Trial Matching")
if st.button("Find Clinical Trials"):
    trial_data = fetch_clinical_trials()
    if trial_data:
        if "trials" in trial_data:
            st.write("### Trial Results")
            df_trials = pd.DataFrame(trial_data["trials"])
            st.dataframe(df_trials)
        else:
            st.json(trial_data)
    else:
        st.error("No trials found or mock data was unavailable.")

st.caption("🔗 Powered by Agile Defense Systems | Norton Oncology | Epic EHR | AI-Driven Precision Medicine")

# -------------------------------------------
# Footer with auto-advance instructions
# -------------------------------------------
st.markdown("---")
st.markdown("""
**Hotkey Auto-Advance Instructions**  
Use the following hotkeys at any point to navigate or auto-advance your workflow:

- **Alt+N**: Proceed to Next Step  
- **Alt+R**: Refine Current Output  
- **Alt+E**: Expand Feature  
- **Alt+Q**: Quick Deploy to Production  

*Pressing these keys will help you quickly jump to relevant sections or trigger expansions in the pipeline.*
""")
