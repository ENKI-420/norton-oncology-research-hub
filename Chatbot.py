import streamlit as st
import requests
from openai import OpenAI
import pandas as pd
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sidebar Configuration
with st.sidebar:
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_api_key = st.text_input("OpenAI API Key", value=openai_api_key, key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/agiledefensesystems/norton-oncology-chatbot)"
    "[Epic EHR Integration](https://www.epic.com/)"

st.markdown("""
    <div id="NavBarLogos">
        <ul class="external-logos">
            <li class="external-logo" title="Visit Epic.com">
                <a href="https://www.epic.com/" class="oe-nav-link external-sites-epic"></a>
            </li>
            <li class="external-logo" title="Visit EpicShare">
                <a href="https://www.epicshare.org/" class="oe-nav-link external-sites-epicshare oe-nav-link-header-selected"></a>
            </li>
            <li class="external-logo" title="Visit Epic Research">
                <a href="https://epicresearch.org/" class="oe-nav-link external-sites-epicresearch"></a>
            </li>
            <li class="external-logo" title="Visit Cosmos">
                <a href="https://cosmos.epic.com/" class="oe-nav-link external-sites-cosmos"></a>
            </li>
            <li class="external-logo" title="Visit MyChart">
                <a href="https://mychart.org/" class="oe-nav-link external-sites-mychart"></a>
            </li>
            <li class="external-logo" title="Visit open.epic">
                <a href="https://open.epic.com" class="oe-nav-link external-sites-openepic"></a>
            </li>
            <li class="external-logo" title="Visit UserWeb">
                <a href="https://userweb.epic.com" class="oe-nav-link external-sites-userweb"></a>
            </li>
            <li class="external-logo" title="Visit Showroom">
                <a href="https://vendorservices.epic.com/Showroom" class="oe-nav-link external-sites-showroom"></a>
            </li>
        </ul>
    </div>

    <div class="page">
        <div id="msgBox"><div id="msgTitle"></div><div id="msgBody"></div></div>
        <a class="homelink" href="/">
            <img class="openEpicLogo" alt="hanging open sign" src="/Content/Images/logo.png?version=R41429">
        </a>
    </div>
    """, unsafe_allow_html=True)

st.title("🔬 Norton Oncology AI Assistant")
st.caption("🚀 AI-driven oncology assistant powered by Agile Defense Systems | AIDEN & Epic EHR Integration")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Welcome to Norton Oncology AI. How can I assist you today?"}]
    if len(st.session_state["messages"]) > 50:
        st.session_state["messages"] = st.session_state["messages"][-50:]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    
    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=st.session_state.messages
        )
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
    except Exception as e:
        st.error(f"API request failed: {e}")
        st.stop()

# Epic EHR Authentication
OAUTH_URL = os.getenv("EPIC_OAUTH_URL", "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token")

def authenticate_epic():
    auth_url = f"{OAUTH_URL}?response_type=code&client_id={os.getenv('EPIC_CLIENT_ID')}&redirect_uri={os.getenv('EPIC_REDIRECT_URI')}"
    st.markdown(f"[Click here to authenticate with Epic]({auth_url})")
    return None
    try:
        response = requests.post(OAUTH_URL, data={
            "grant_type": "password",
            "username": username,
            "password": password
        }, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Authentication failed: {e}")
        return None

st.subheader("🩺 Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    epic_username = st.text_input("Epic Username")
    epic_password = st.text_input("Epic Password", type="password")
    show_password = st.checkbox("Show Password")
    if show_password:
        epic_password = st.text_input("Epic Password", value=epic_password, type="default")
    if st.button("Sign In to Epic", disabled=st.session_state.get("authenticating", False)):
    st.session_state["authenticating"] = True
    authenticate_epic()
        st.session_state["authenticating"] = True
        token_data = authenticate_epic(epic_username, epic_password)
        if token_data:
            st.session_state["auth_token"] = token_data.get("access_token")
            st.session_state["refresh_token"] = token_data.get("refresh_token")
            st.session_state["token_expiry"] = token_data.get("expires_in") + time.time()
            st.session_state["user_id"] = epic_username
            st.success("Authenticated successfully!")
        st.session_state["authenticating"] = False

@st.cache_data(ttl=300)
def get_patient_data(patient_id):
    try:
        import asyncio
import httpx

async def fetch_patient_history(patient_id):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.oncologyhub.com/patients/history", params={"patientId": patient_id}, timeout=10)
        response.raise_for_status()
        return response.json()

@st.cache_data(ttl=300)
def get_patient_data(patient_id):
    return asyncio.run(fetch_patient_history(patient_id))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching patient data: {e}")
        return {}

patient_id = st.text_input("Enter Epic Patient ID for History Retrieval")
if st.button("Retrieve History"):
    with st.spinner("Fetching patient history..."):
        st.json(get_patient_data(patient_id))

with col2:
    if st.button("🧬 Run Genomic Analysis"):
    with st.spinner("Running genomic analysis..."):
        try:
                    response = requests.post("https://api.oncolo.ai/genomics/mutation_analysis", json={
                "patient_id": patient_id,
                "gene_variants": ["TP53", "BRCA1"],
                "predicted_impact": "High-Risk"
            })
            response.raise_for_status()
            st.json(response.json())
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching genomic analysis: {e}")
        st.write("Analyzing oncogenic mutations...")
        response = requests.post("https://api.oncolo.ai/genomics/mutation_analysis", json={
            "patient_id": patient_id,
            "gene_variants": ["TP53", "BRCA1"],
            "predicted_impact": "High-Risk"
        })
        st.json(response.json())

with col3:
    if st.button("🔗 Connect Clinical Trials"):
        st.write("Fetching AI-matched clinical trials...")
        response = requests.get("https://api.3oncologyresearchhub.com/v2/studies")
        st.json(response.json())

# Beaker Report Integration
FHIR_BASE_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"

def fetch_beaker_report(patient_id, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}", "Accept": "application/fhir+json"}
    report_url = f"{FHIR_BASE_URL}DiagnosticReport?patient={patient_id}"
    try:
        response = requests.get(report_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching Beaker report: {e}")
        return None

with st.expander("📊 Fetch Beaker Report"):
    patient_id = st.text_input("Enter Patient ID for Beaker Report")
    if st.button("Fetch Report"):
    with st.toast("Fetching Beaker report...", icon="🔄"):
        try:
                    auth_token = st.session_state.get("auth_token")
            if not auth_token or ("token_expiry" in st.session_state and time.time() > st.session_state["token_expiry"]):
    refresh_token = st.session_state.get("refresh_token")
    if refresh_token:
        try:
            refresh_response = requests.post(OAUTH_URL, data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            })
            refresh_response.raise_for_status()
            new_token_data = refresh_response.json()
            st.session_state["auth_token"] = new_token_data.get("access_token")
            st.session_state["token_expiry"] = new_token_data.get("expires_in") + time.time()
            st.success("Session refreshed.")
        except requests.exceptions.RequestException as e:
            st.error(f"Session expired. Please sign in again: {e}")
            return
                report_data = fetch_beaker_report(patient_id, auth_token)
                if report_data:
                    st.json(report_data)
                else:
                    st.error("Failed to fetch Beaker report data.")
            else:
                st.error("User is not authenticated. Please sign in first.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching Beaker report: {e}")
            if report_data:
                st.json(report_data)
            else:
                st.error("Failed to fetch Beaker report data.")
        else:
            st.error("User is not authenticated. Please sign in first.")
        auth_token = st.session_state.get("auth_token")
        if auth_token:
            report_data = fetch_beaker_report(patient_id, auth_token)
            if report_data:
                st.json(report_data)
            else:
                st.error("Failed to fetch Beaker report data.")
        else:
            st.error("User is not authenticated. Please sign in first.")

st.caption("🔗 Powered by Agile Defense Systems | Norton Oncology | Epic EHR | AI-Driven Precision Medicine")
