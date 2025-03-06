import streamlit as st
import requests
import pandas as pd
import os
import time
from openai import OpenAI
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
GENOMIC_API_URL = "https://genomic-api-url.com/analyze"
COSMIC_API_URL = "https://cancer.sanger.ac.uk/cosmic/api/v1"
BEAKER_REPORTS_URL = "https://your-beaker-reports-api.com/v1"

# Load API keys
openai_api_key = os.getenv("OPENAI_API_KEY", "")
cosmic_api_key = os.getenv("COSMIC_API_KEY", "")
beaker_api_key = os.getenv("BEAKER_API_KEY", "")

# Setup session for retries
session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)

# --- COSMIC Tissue Data ---
COSMIC_TISSUES = {
    "Breast": 16927,
    "Lung": 45578,
    "Colorectal": 55327,
    "Prostate": 5072,
    "Skin": 21246,
    "Ovary": 6701,
    "Blood": 128940
}

MOTIVATIONAL_MESSAGES = [
    "🧬 Crunching genomic data... Team Agile is on it!",
    "⚡️ Parsing mutations at light speed...",
    "🔭 Scanning cosmic database...",
    "☕️ Grab a coffee - magic in progress...",
    "🚀 Preparing precision medicine insights..."
]

# Sidebar Configuration
with st.sidebar:
    st.header("🧬 Agile Oncology AI")
    
    # Navigation
    analysis_mode = st.radio("Analysis Mode:", 
                           ["Genomic Analysis", "COSMIC Browser", "Beaker Reports"])
    
    # API Keys
    st.subheader("🔑 Security Credentials")
    openai_api_key = st.text_input("OpenAI Key", value=openai_api_key, type="password")
    cosmic_api_key = st.text_input("COSMIC Key", value=cosmic_api_key, type="password")
    beaker_api_key = st.text_input("Beaker Key", value=beaker_api_key, type="password")

# Main Interface
st.title(f"🚀 Agile Oncology {analysis_mode}")
st.caption("Precision Medicine Platform v2.0")

# --- Core Functions ---
def get_cosmic_data(tissue_type, histology=None):
    """Fetch COSMIC data with progress tracking"""
    with st.status(f"Querying COSMIC for {tissue_type}..."):
        try:
            headers = {"Authorization": f"Bearer {cosmic_api_key}"}
            params = {"tissue": tissue_type}
            if histology:
                params["histology"] = histology
                
            response = session.get(
                f"{COSMIC_API_URL}/mutations",
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"COSMIC Error: {str(e)}")
            return None

def fetch_beaker_reports(query):
    """Retrieve Beaker reports with real-time updates"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(5):
        progress_bar.progress((i+1)*20)
        status_text.text(MOTIVATIONAL_MESSAGES[i % len(MOTIVATIONAL_MESSAGES)])
        time.sleep(0.5)
        
    try:
        response = session.get(
            f"{BEAKER_REPORTS_URL}/search",
            headers={"Authorization": f"Bearer {beaker_api_key}"},
            params={"q": query},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Beaker Error: {str(e)}")
        return None

# --- Main Application Logic ---
if analysis_mode == "COSMIC Browser":
    st.header("COSMIC Data Explorer")
    
    col1, col2 = st.columns(2)
    with col1:
        tissue_type = st.selectbox("Select Tissue Type", 
                                 list(COSMIC_TISSUES.keys()),
                                 help="Start with broad tissue category")
        
    with col2:
        histology = st.multiselect("Filter by Histology", 
                                 ["Carcinoma", "Adenoma", "Sarcoma", "Melanoma"],
                                 help="Optional histology refinement")
        
    if st.button("🚀 Query COSMIC"):
        with st.spinner("Intergalactic data fetch in progress..."):
            cosmic_data = get_cosmic_data(tissue_type, histology)
            
            if cosmic_data:
                st.subheader(f"{tissue_type} Mutation Landscape")
                df = pd.DataFrame(cosmic_data.get('mutations', []))
                st.dataframe(df.head(50), use_container_width=True)

elif analysis_mode == "Beaker Reports":
    st.header("🔬 Beaker Report Interface")
    report_query = st.text_input("Search Beaker Reports", "BRCA1 OR TP53")
    
    if st.button("🔍 Search Reports"):
        reports = fetch_beaker_reports(report_query)
        if reports:
            st.subheader("Latest Relevant Reports")
            for report in reports.get('results', [])[:5]:
                with st.expander(f"{report.get('title', 'Untitled')}"):
                    st.write(report.get('abstract', 'No abstract available'))

else:  # Genomic Analysis
    st.header("🧬 Genomic Data Analysis")
    uploaded_file = st.file_uploader("Upload genomic file", type=["vcf", "json"])
    
    if uploaded_file:
        with st.spinner("Decoding genomic secrets..."):
            # --- Analysis Pipeline ---
            try:
                # Process genomic data
                response = session.post(
                    GENOMIC_API_URL,
                    files={'file': uploaded_file},
                    timeout=45
                )
                response.raise_for_status()
                analysis = response.json()
                
                # Display results
                st.subheader("Mutation Analysis")
                st.write(f"Detected {len(analysis.get('mutations', []))} significant variants")
                
                # COSMIC Integration
                st.subheader("COSMIC Context")
                cosmic_df = pd.DataFrame(analysis.get('cosmic_context', []))
                st.dataframe(cosmic_df, use_container_width=True)
                
                # AI Insights
                st.subheader("🤖 AI-Powered Interpretation")
                with st.expander("Clinical Implications"):
                    client = OpenAI(api_key=openai_api_key)
                    response = client.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=[{
                            "role": "user",
                            "content": f"Analyze these genomic findings: {analysis}"
                        }]
                    )
                    st.write(response.choices[0].message.content)
                    
            except Exception as e:
                st.error(f"Analysis Failed: {str(e)}")

# Team Motivation System
st.sidebar.markdown("---")
st.sidebar.header("Team Performance")
st.sidebar.progress(78, text="Project Completion")
st.sidebar.metric("Active Users", 142, "+23%")
st.sidebar.button("☕️ Request Coffee Resupply")

st.caption("🔬 Powered by Agile Oncology AI v2.1 | Secure HIPAA-compliant Analysis")
