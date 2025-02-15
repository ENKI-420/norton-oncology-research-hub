import streamlit as st
import requests
from openai import OpenAI
import pandas as pd
import os
import time
from dotenv import load_dotenv
from langchain.tools import DuckDuckGoSearchRun
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler

# Load environment variables
load_dotenv()

# Sidebar Configuration
with st.sidebar:
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_api_key = st.text_input("OpenAI API Key", value=openai_api_key, key="chatbot_api_key", type="password")
    st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")
    st.markdown("[Epic EHR Integration](https://www.epic.com/)")

st.title("🔬 Norton Oncology AI Chatbot")
st.caption("🚀 AI-driven oncology assistant powered by AIDEN & Epic EHR Integration")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Welcome to Norton Oncology AI. How can I assist you today?"}]
    if len(st.session_state["messages"]) > 50:
        st.session_state["messages"] = st.session_state["messages"][-50:]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
if prompt := st.chat_input("Ask about cancer treatment, clinical trials, or genomic analysis..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    # LangChain Search Agent
    llm = ChatOpenAI(model_name="gpt-4-turbo", openai_api_key=openai_api_key, streaming=True)
    search_tool = DuckDuckGoSearchRun()
    agent = initialize_agent(
        tools=[search_tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    # Process Query using LangChain & OpenAI
    with st.spinner("Fetching oncology data..."):
        try:
            response = agent.run(prompt)
        except Exception as e:
            response = f"Error processing query: {e}"

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

# Epic EHR Authentication (Optional)
OAUTH_URL = os.getenv("EPIC_OAUTH_URL", "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token")

def authenticate_epic(username, password):
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
    if st.button("Sign In to Epic", disabled=st.session_state.get("authenticating", False)):
        auth_data = authenticate_epic(epic_username, epic_password)
        if auth_data:
            st.success("Authenticated successfully!")
            st.session_state["epic_auth"] = auth_data
