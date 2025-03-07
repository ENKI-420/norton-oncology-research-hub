import streamlit as st
import os
from modules.digital_twins import generate_digital_twin
from modules.tumor_evolution import predict_tumor_evolution
from modules.crispr_ai import analyze_crispr_feasibility
from modules.nanoparticle_simulation import simulate_nanoparticle_delivery
from config import load_api_key
from api_oncolo_ai__jit_plugin import some_function  # Ensure this import is correct

# Constants for page names
DIGITAL_TWIN_AI = "Digital Twin AI"
TUMOR_EVOLUTION = "Tumor Evolution"
CRISPR_AI = "CRISPR AI"
NANOPARTICLE_AI = "Nanoparticle AI"

def get_api_key():
    """Load and validate the API key from Streamlit secrets."""
    api_key = st.secrets["OPENAI_API_KEY"]
    if not api_key:
        st.error("Failed to load API key. Please check your configuration.")
    return api_key

def handle_patient_id_input(button_label, callback, *args):
    """Handle patient ID input and button click events."""
    patient_id = st.text_input("Enter Patient ID:")
    if st.button(button_label):
        result = callback(patient_id, *args)
        st.json(result)

def main():
    OPENAI_API_KEY = get_api_key()
    if not OPENAI_API_KEY:
        return

    # Sidebar Navigation
    st.sidebar.title("🩺 AGILE Oncology AI Hub")
    page = st.sidebar.radio("Navigation", [DIGITAL_TWIN_AI, TUMOR_EVOLUTION, CRISPR_AI, NANOPARTICLE_AI])

    # Page Logic
    if page == DIGITAL_TWIN_AI:
        st.title("👥 Digital Twin AI System")
        handle_patient_id_input("Generate Digital Twin", generate_digital_twin)

    elif page == TUMOR_EVOLUTION:
        st.title("🔬 Tumor Evolution Prediction")
        handle_patient_id_input("Predict Tumor Evolution", predict_tumor_evolution, ["TP53", "KRAS"])

    elif page == CRISPR_AI:
        st.title("🧬 CRISPR Editing Feasibility AI")
        handle_patient_id_input("Analyze CRISPR Feasibility", analyze_crispr_feasibility, ["BRAF", "EGFR"])

    elif page == NANOPARTICLE_AI:
        st.title("💊 Nanoparticle Drug Delivery AI")
        handle_patient_id_input("Simulate Drug Delivery", simulate_nanoparticle_delivery)

    st.sidebar.caption("🔗 Powered by AI-driven Precision Medicine")

if __name__ == "__main__":
    main()import streamlit as st
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

def generate_ai_treatment_suggestions(test_results):
    if not openai_api_key:
        st.error("OpenAI API Key is missing. Please provide a valid key.")
        return None
    
    client = OpenAI(api_key=openai_api_key)
    
    try:
        # Convert DataFrame to formatted string
        results_text = "\n".join(
            [f"- {row['Test Name']}: {row['Result']} ({row['Status']})" 
             for _, row in test_results.iterrows()]
        )
        
        # Create structured prompt
        prompt = f"""As an oncology AI consultant, analyze these lab results and provide treatment suggestions:
        
        {results_text}
        
        Consider these aspects:
        1. Potential targeted therapies
        2. Relevant clinical trials
        3. Precision medicine approaches
        4. Critical result flags
        5. Recommended follow-up tests
        
        Format response in markdown with clear sections."""
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an oncology expert providing research-focused treatment suggestions. Include scientific rationales."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=700
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"AI Analysis Failed: {str(e)}")
        return None

# Main app logic for Beaker Report Analysis
if selected_option == "Beaker Report Analysis":
    st.subheader("🔬 Beaker Lab Report Analysis")
    epic_username = st.text_input("Epic Username")
    epic_password = st.text_input("Epic Password", type="password")
    patient_id = st.text_input("Patient ID")

    if st.button("Fetch Beaker Report"):
        if not all([epic_username, epic_password, patient_id]):
            st.warning("Please fill all Epic authentication fields.")
        else:
            with st.spinner("Authenticating with Epic..."):
                auth_token = authenticate_epic(epic_username, epic_password)
            
            if auth_token:
                with st.spinner("Fetching Beaker Report..."):
                    report_data = fetch_beaker_report(patient_id, auth_token)
                
                if report_data:
                    df_report = process_beaker_report(report_data)
                    st.success("✅ Beaker Report Retrieved!")
                    st.dataframe(df_report, use_container_width=True)

                    # Generate AI insights
                    with st.spinner("🧠 Analyzing results with AI..."):
                        ai_response = generate_ai_treatment_suggestions(df_report)
                        
                        if ai_response:
                            st.subheader("💡 AI-Powered Oncology Insights")
                            st.markdown(ai_response)
                            st.divider()
                            st.caption("⚠️ Note: These suggestions are research-focused and should be validated by clinical staff.")
