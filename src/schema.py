from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class FeedbackState(BaseModel):
    """
    FeedbackState
    - Updated to include extraction fields for Severity, Impact, etc.
    """
    raw_text: str
    category: Optional[str] = "Unclassified"
    confidence: Optional[str] = None
    priority: Optional[str] = "Medium"
    
    # NEW FIELDS: These MUST be here for the Extractor to work
    severity: Optional[str] = None
    impact: Optional[str] = None
    platform: Optional[str] = None
    steps_to_reproduce: Optional[str] = None
    requested_functionality: Optional[str] = None
    user_context: Optional[str] = None

    # Status and Metadata
    insights: Optional[Dict] = {}
    processed: bool = False
    processing_errors: List[str] = []