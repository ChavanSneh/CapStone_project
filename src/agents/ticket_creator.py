import pandas as pd
import uuid
import os
from typing import List
from src.schema import FeedbackState
from src.utils.logger import logger

class TicketCreator:
    """
    Ticket Creator
    - Converts classified and enriched feedback into structured engineering tickets
    - Fixed to read top-level state fields (severity, impact, etc.)
    """

    OUTPUT_COLUMNS = [
        "ticket_id",
        "title",
        "category",
        "priority",
        "steps_to_reproduce",
        "platform",
        "severity",
        "impact",
        "requested_functionality",
        "user_context",
        "processing_errors"
    ]

    def __init__(self, output_path="output/generated_tickets.csv"):
        self.output_path = output_path

    def create_ticket(self, state: FeedbackState) -> dict:
        """
        Create a structured ticket from a FeedbackState object.
        """
        def get_val(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        # UPDATED LOGIC:
        # We now pull these fields directly from 'state' instead of 'insights'
        ticket = {
            "ticket_id": str(uuid.uuid4())[:8],
            "title": self._generate_title(state),
            "category": get_val(state, "category", "Unknown"),
            "priority": get_val(state, "priority", "Low"),
            
            # These were the 'stuck' fields - now reading from the main state
            "steps_to_reproduce": get_val(state, "steps_to_reproduce", ""),
            "platform": get_val(state, "platform", ""),
            "severity": get_val(state, "severity", ""),
            "impact": get_val(state, "impact", ""),
            "requested_functionality": get_val(state, "requested_functionality", ""),
            "user_context": get_val(state, "user_context", ""),
            
            "processing_errors": "; ".join(get_val(state, "processing_errors", [])) 
                                if get_val(state, "processing_errors") else ""
        }
        return ticket

    def process_feedback(self, states: List[FeedbackState]) -> pd.DataFrame:
        """
        Process a list of FeedbackState objects into structured tickets.
        """
        tickets = []
        for state in states:
            ticket = self.create_ticket(state)
            tickets.append(ticket)

        if os.path.dirname(self.output_path):
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        tickets_df = pd.DataFrame(tickets, columns=self.OUTPUT_COLUMNS)
        tickets_df.to_csv(self.output_path, index=False)
        
        logger.info(f"TicketCreator: Saved {len(tickets)} tickets to {self.output_path}")
        return tickets_df

    def _generate_title(self, state: FeedbackState) -> str:
        def get_val(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        text = get_val(state, "raw_text", "") or ""
        category = get_val(state, "category", "Feedback")
        
        if category == "Bug":
            return f"Bug: {text[:50]}..."
        elif category == "Feature Request":
            return f"Feature: {text[:50]}..."
        else:
            return f"{category}: {text[:50]}..."