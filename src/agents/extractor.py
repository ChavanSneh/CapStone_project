import json
from src.utils.logger import logger

class ExtractorAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def process(self, state):
        prompt = f"Extract details from: {state.raw_text}. Return JSON with platform, severity, impact, and steps_to_reproduce (as a list)."
        
        try:
            response = self.llm_client.generate(prompt)
            clean_json = response.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_json)
            
            # FIX: Ensure steps_to_reproduce is ALWAYS a string, never a list
            steps = data.get("steps_to_reproduce", "Not provided")
            if isinstance(steps, list):
                state.steps_to_reproduce = ", ".join(steps)
            else:
                state.steps_to_reproduce = str(steps)

            state.platform = data.get("platform", "Unknown")
            state.severity = data.get("severity", "Medium")
            state.impact = data.get("impact", "Medium")
            
        except Exception as e:
            state.processing_errors.append(f"Extraction Failed: {str(e)}")
            # Default values to prevent 'stuck' or empty outputs
            state.steps_to_reproduce = "Error during extraction"
            
        return state