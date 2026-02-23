import sys
import os
import yaml
import streamlit as st

# THIS MUST BE FIRST
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# NOW do the imports
from src.orchestrator import Orchestrator
# ... rest of imports
from src.utils.llm_client import LLMClient
from src.schema import FeedbackState
from src.agents.csv_reader import CSVReader
from src.agents.ticket_creator import TicketCreator

# 3. Configuration Loading
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    st.error("config.yaml not found. Please ensure it exists in the project root.")
    st.stop()

llm_config = config.get("llm", {})
llm_client = LLMClient(
    provider=llm_config.get("provider", "gemini"),
    model=llm_config.get("model", "2.5-flash"),
    api_key=llm_config.get("api_key")
)

# 4. Initialize Core Components
orchestrator = Orchestrator(llm_client=llm_client)
ticket_creator = TicketCreator() 
reader = CSVReader() 

# 5. Streamlit UI
st.set_page_config(page_title="Feedback AI", layout="wide")
st.title("📊 Multi-Agent Feedback Processing System")

uploaded_file = st.file_uploader("Upload feedback CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df = reader.read_csv(uploaded_file)
        st.subheader("Raw Feedback Data")
        st.dataframe(df, use_container_width=True)

        if st.button("Run Processing Pipeline"):
            states = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, row in df.iterrows():
                feedback_text = row.get("user_feedback", "No feedback text provided")
                status_text.text(f"Processing row {i+1} of {len(df)}...")
                
                # Run through the multi-agent pipeline
                state: FeedbackState = orchestrator.run_pipeline(feedback_text)
                states.append(state)
                
                progress_bar.progress((i + 1) / len(df))

            # Convert states into structured tickets
            tickets_df = ticket_creator.process_feedback(states)

            st.subheader("Generated Tickets")
            st.dataframe(tickets_df, use_container_width=True)

            # File Operations
            os.makedirs("output", exist_ok=True)
            output_path = "output/generated_tickets.csv"
            tickets_df.to_csv(output_path, index=False)
            st.success(f"Pipeline Complete! Tickets saved to {output_path}")
            
    except Exception as e:
        st.error(f"System Error: {e}")