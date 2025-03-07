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
    main()
