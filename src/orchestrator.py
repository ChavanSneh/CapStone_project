import time
from src.schema import FeedbackState
from src.agents.classifier import ClassifierAgent
from src.agents.extractor import ExtractorAgent
from src.agents.qa_agent import QAAgent
from src.utils.logger import logger 
from src.utils.llm_client import LLMClient

class Orchestrator:
    """
    Orchestrator
    - Handles the agent sequence: Classifier -> Extractor -> QA
    - Uses sleep intervals to stay under the Gemini 2.5 Flash Lite 10 RPM limit
    """

    def __init__(self, llm_client: LLMClient):
        self.agents = [
            ClassifierAgent(llm_client=llm_client),
            ExtractorAgent(llm_client=llm_client),
            QAAgent()
        ]

    def run_pipeline(self, raw_text: str) -> FeedbackState:
        state = FeedbackState(raw_text=raw_text)
        logger.info(f"Orchestrator: Processing new feedback entry.")

        for i, agent in enumerate(self.agents):
            try:
                # MANDATORY COOLDOWN:
                # With a 10 RPM limit, we need roughly 6 seconds per request.
                # Since each row uses 2-3 agents, we sleep 5 seconds between agents.
                if i > 0:
                    logger.info("Orchestrator: Cooling down for 5s to protect quota...")
                    time.sleep(5.0) 

                logger.info(f"Orchestrator: Executing {agent.__class__.__name__}")
                state = agent.process(state)
                
                # Check for errors in the state object
                if hasattr(state, 'processing_errors') and state.processing_errors:
                    logger.warning(f"Orchestrator: Agent reported error: {state.processing_errors[-1]}")

            except Exception as e:
                error_msg = f"Orchestrator: {agent.__class__.__name__} failed: {str(e)}"
                logger.error(error_msg)
                if hasattr(state, 'processing_errors'):
                    state.processing_errors.append(error_msg)

        state.processed = True
        logger.info("Orchestrator: Pipeline finished.")
        return state