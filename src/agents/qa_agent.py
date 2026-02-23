from src.schema import FeedbackState
from src.agents.base_agent import BaseAgent
from src.utils.logger import logger

class QAAgent(BaseAgent):
    """
    QAAgent
    - Performs quality assurance checks on feedback
    - Example: detect PII (emails, phone numbers) and flag issues
    - Appends errors to FeedbackState instead of raising exceptions
    """

    def process(self, state: FeedbackState) -> FeedbackState:
        logger.info("QAAgent: Validating feedback for PII and quality issues...")
        try:
            # Simple PII detection
            if "@" in state.raw_text or "phone" in state.raw_text or "contact" in state.raw_text:
                state.processing_errors.append(
                    "PII detected in feedback, cannot proceed with full processing."
                )
                state.processed = False
                logger.warning("QAAgent: PII detected, feedback flagged.")

            # Example: check for empty feedback
            if not state.raw_text.strip():
                state.processing_errors.append("Empty feedback text.")
                state.processed = False
                logger.warning("QAAgent: Empty feedback detected.")

        except Exception as e:
            state.processing_errors.append(f"QAAgent error: {e}")
            logger.error(f"QAAgent failed: {e}")

        return state