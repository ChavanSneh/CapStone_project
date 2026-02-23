import json
from src.schema import FeedbackState
from src.utils.llm_client import LLMClient
from src.utils.logger import logger

class ClassifierAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def process(self, state: FeedbackState) -> FeedbackState:
        raw_text = getattr(state, 'raw_text', '')
        
        prompt = f"""
        CONSTRAINT: Output ONLY valid JSON. No markdown. No preamble.
        Feedback: "{raw_text}"
        SCHEMA: {{ "category": "Bug"|"Feature Request"|"General Feedback", "priority": "High"|"Medium"|"Low", "confidence": "High"|"Medium"|"Low" }}
        """

        try:
            response = self.llm_client.generate(prompt)
            
            if response.startswith("ERROR"):
                raise ValueError(response)

            # Clean markdown backticks
            clean_content = response.strip().strip('`').replace('json', '', 1).strip()
            data = json.loads(clean_content)
            
            state.category = data.get("category", "General Feedback")
            state.priority = data.get("priority", "Low")
            state.confidence = data.get("confidence", "Medium")

            logger.info(f"Classifier: Success - {state.category}")

        except Exception as e:
            logger.error(f"Classifier Error: {e}")
            state.category = "Unclassified"
            state.processing_errors.append(f"Classifier: {str(e)}")
            
        return state