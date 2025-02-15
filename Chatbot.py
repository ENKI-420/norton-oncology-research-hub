import streamlit as st
import requests
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Epic FHIR Configuration
FHIR_BASE_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"
OAUTH_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Function to authenticate user with Epic (OAuth2)
def authenticate_user(username, password):
    auth_data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': os.getenv("EPIC_CLIENT_ID", ""),
        'client_secret': os.getenv("EPIC_CLIENT_SECRET", "")
    }
    response = requests.post(OAUTH_URL, data=auth_data)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

# Function to fetch Beaker Report (Diagnostic Reports) using the OAuth token
def fetch_beaker_report(patient_id, auth_token):
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/fhir+json"
    }
    report_url = f"{FHIR_BASE_URL}DiagnosticReport?patient={patient_id}"
    response = requests.get(report_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

# Function to process and analyze Beaker data
def process_and_analyze_beaker_data(data):
    records = data.get("entry", [])
    processed_data = []
    for record in records:
        report = record.get("resource", {})
        processed_data.append({
            "Report ID": report.get("id", ""),
            "Test Name": report.get("code", {}).get("text", ""),
            "Date of Test": report.get("issued", ""),
            "Result": report.get("result", ""),
            "Status": report.get("status", "")
        })
    
    df = pd.DataFrame(processed_data)
    return df

# Function to generate AI-based treatment recommendations
def generate_ai_recommendations(test_data):
    if not OPENAI_API_KEY:
        return "OpenAI API key not found. AI analysis unavailable."

    client = OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = f"""
    Given the following oncology test results, provide a summary and potential treatment recommendations:

    {test_data.to_string(index=False)}

    Include possible next steps, referrals, or clinical trials that might be relevant for this patient.
    """

    try:
        response = client.completions.create(
            model="gpt-4-turbo",
            prompt=prompt,
            max_tokens=500
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"AI analysis error: {e}"

# Function to call after successful authentication
def fetch_and_process_patient_data(patient_id):
    if 'auth_token' not in st.session_state:
        st.error("User is not authenticated. Please log in first.")
        return
    
    auth_token = st.session_state.auth_token
    data = fetch_beaker_report(patient_id, auth_token)
    
    if data:
        test_results = process_and_analyze_beaker_data(data)
        st.write("### 🩺 Patient Beaker Test Results")
        st.dataframe(test_results)

        # AI-powered recommendation
        st.write("### 🤖 AI-Generated Treatment Insights")
        ai_response = generate_ai_recommendations(test_results)
        st.write(ai_response)
    else:
        st.error("Failed to fetch Beaker report data.")

# Streamlit User Interface for login
def user_login():
    st.subheader("🔐 Login to Epic")
    username = st.text_input("Epic Username")
    password = st.text_input("Epic Password", type="password")
    
    if st.button("Login"):
        token = authenticate_user(username, password)
        if token:
            st.session_state.auth_token = token
            st.success("Login successful! You can now fetch Beaker data.")
        else:
            st.error("Authentication failed. Please check your credentials.")

# Streamlit main function
def main():
    st.title("🔬 Norton Oncology - AI-Enhanced Beaker Report Analysis")

    if 'auth_token' in st.session_state:
        patient_id = st.text_input("Enter Patient ID")
        if st.button('Fetch Beaker Report'):
            fetch_and_process_patient_data(patient_id)
    else:
        user_login()

    # Adding Epic footer logo for assurance and security perception
    st.markdown("""
    <div style="position: fixed; bottom: 0; width: 100%; text-align: center; padding: 10px;">
        <img src="https://vendorservices.epic.com/Scripts/React/media/footerLogo.a31a1d6cb66b67c7be72.png" 
            alt="Epic Footer Logo" style="width: 150px;"/>
    </div>
    """, unsafe_allow_html=True)

    # Adding Epic UserWeb logo for user trust
    st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <img src="https://vendorservices.epic.com/Content/images/UserWeb.png" 
            alt="Epic UserWeb Logo" style="width: 200px;"/>
    </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
