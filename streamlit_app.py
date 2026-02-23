import sys
import os
import yaml
import streamlit as st
import pandas as pd

# 1. Path Setup
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 2. Package Imports
from src.orchestrator import Orchestrator
from src.utils.llm_client import LLMClient
from src.schema import FeedbackState
from src.agents.csv_reader import CSVReader
from src.agents.ticket_creator import TicketCreator

# 3. Streamlit Page Configuration
st.set_page_config(page_title="Feedback AI Agent", layout="wide", page_icon="📊")

# 4. Configuration & API Key Loading (Cloud-Safe)
config = {}
if os.path.exists("config.yaml"):
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f) or {}
    except Exception as e:
        st.sidebar.warning(f"Note: config.yaml exists but couldn't be read: {e}")

# Key Hierarchy: Streamlit Secrets (Cloud) -> config.yaml (Local)
llm_config = config.get("llm", {})
api_key = st.secrets.get("GEMINI_API_KEY") or llm_config.get("api_key")

if not api_key:
    st.error("🚨 **API Key Missing!** Please add 'GEMINI_API_KEY' to your Streamlit Cloud Secrets.")
    st.info("To fix this: Go to App Settings -> Secrets and add: GEMINI_API_KEY = 'your_key_here'")
    st.stop()

# 5. Initialize Core Components
@st.cache_resource
def init_components(_api_key, _llm_config):
    client = LLMClient(
        provider=_llm_config.get("provider", "google"),
        model=_llm_config.get("model", "gemini-1.5-flash"),
        api_key=_api_key
    )
    return Orchestrator(llm_client=client), TicketCreator(), CSVReader()

orchestrator, ticket_creator, reader = init_components(api_key, llm_config)

# 6. Streamlit UI
st.title("📊 Multi-Agent Feedback Processing System")
st.markdown("Automate classification and ticket generation using Agentic AI.")

uploaded_file = st.file_uploader("Upload feedback CSV (Ensure it has a 'user_feedback' column)", type=["csv"])

if uploaded_file is not None:
    try:
        df = reader.read_csv(uploaded_file)
        st.subheader("Raw Feedback Data")
        st.dataframe(df, width="stretch")

        if st.button("🚀 Run Processing Pipeline"):
            states = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Use columns for visual feedback
            for i, row in df.iterrows():
                feedback_text = row.get("user_feedback") or row.get("feedback_text") or "No feedback provided"
                status_text.text(f"Processing row {i+1} of {len(df)}...")
                
                # Run through the multi-agent pipeline
                state: FeedbackState = orchestrator.run_pipeline(feedback_text)
                states.append(state)
                
                progress_bar.progress((i + 1) / len(df))

            status_text.text("✅ All rows processed!")

            # Convert states into structured tickets
            tickets_df = ticket_creator.process_feedback(states)

            st.subheader("Generated Tickets")
            st.dataframe(tickets_df, use_container_width=True)

            # 7. File Operations & Download (The "Cloud" Fix)
            os.makedirs("output", exist_ok=True)
            output_path = "output/generated_tickets.csv"
            tickets_df.to_csv(output_path, index=False)
            
            # Create a memory buffer for the download button
            csv_data = tickets_df.to_csv(index=False).encode('utf-8')
            
            st.success("Pipeline Complete!")
            st.download_button(
                label="📥 Download Generated Tickets as CSV",
                data=csv_data,
                file_name="processed_feedback_tickets.csv",
                mime="text/csv",
                help="Click here to save the processed results to your computer."
            )
            
    except Exception as e:
        st.error(f"System Error: {e}")
        st.exception(e) # This shows the full error trace to help us debug