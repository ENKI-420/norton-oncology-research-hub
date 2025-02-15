import streamlit as st
import requests
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from langchain.tools import DuckDuckGoSearchRun
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

# Load environment variables
load_dotenv()

# Epic FHIR Credentials
EPIC_FHIR_BASE_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"
OAUTH_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"

# Sidebar Configuration
with st.sidebar:
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    epic_client_id = os.getenv("EPIC_CLIENT_ID", "")
    epic_client_secret = os.getenv("EPIC_CLIENT_SECRET", "")
    
    openai_api_key = st.text_input("OpenAI API Key", value=openai_api_key, key="chatbot_api_key", type="password")
    epic_client_id = st.text_input("Epic Client ID", value=epic_client_id, key="epic_client_id")
    epic_client_secret = st.text_input("Epic Client Secret", value=epic_client_secret, key="epic_client_secret", type="password")

    st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")
    st.markdown("[Epic EHR Integration](https://www.epic.com/)")

st.title("🔬 Norton Oncology AI Chatbot")
st.caption("🚀 AI-driven oncology assistant powered by AIDEN & Epic EHR Integration")

# Authenticate with Epic FHIR
def authenticate_epic(client_id, client_secret):
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    try:
        response = requests.post(OAUTH_URL, data=payload)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        st.error(f"Epic FHIR Authentication failed: {e}")
        return None

# Retrieve Patient Data from Epic FHIR
def get_patient_data(patient_id, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{EPIC_FHIR_BASE_URL}Patient/{patient_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch patient data: {e}")
        return None

# Retrieve Clinical Notes
def get_clinical_notes(patient_id, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{EPIC_FHIR_BASE_URL}DocumentReference?patient={patient_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch clinical notes: {e}")
        return None

# Retrieve Genomic Report
def get_genomic_report(patient_id, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{EPIC_FHIR_BASE_URL}Observation?patient={patient_id}&category=genomics"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch genomic data: {e}")
        return None

# User input for Patient ID
patient_id = st.text_input("Enter Patient ID for Oncology Analysis")

if patient_id:
    # Authenticate with Epic FHIR
    access_token = authenticate_epic(epic_client_id, epic_client_secret)
    if access_token:
        st.success("Epic FHIR Authentication Successful!")
        
        # Fetch and display patient details
        st.subheader("🔍 Patient Details")
        patient_data = get_patient_data(patient_id, access_token)
        if patient_data:
            st.json(patient_data)

        # Fetch and display clinical notes
        st.subheader("📄 Clinical Notes")
        clinical_notes = get_clinical_notes(patient_id, access_token)
        if clinical_notes:
            st.json(clinical_notes)

        # Fetch and display genomic report
        st.subheader("🧬 Genomic Data")
        genomic_report = get_genomic_report(patient_id, access_token)
        if genomic_report:
            st.json(genomic_report)

# AI-Powered Clinical Recommendations
if patient_id and access_token:
    st.subheader("🤖 AI-Powered Treatment Recommendations")
    
    if openai_api_key:
        llm = ChatOpenAI(model_name="gpt-4-turbo", openai_api_key=openai_api_key)
        search_tool = DuckDuckGoSearchRun()
        agent = initialize_agent(
            tools=[search_tool],
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
        )

        query = f"Generate a treatment plan for a patient with ID {patient_id} based on clinical notes and genomic analysis."
        with st.spinner("Generating AI-based oncology recommendations..."):
            try:
                response = agent.run(query)
                st.write("### AI Recommendations")
                st.write(response)
            except Exception as e:
                st.error(f"Error generating AI recommendations: {e}")
    else:
        st.warning("Please provide an OpenAI API key to enable AI-based recommendations.")
