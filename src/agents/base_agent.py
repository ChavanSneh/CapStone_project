import sys
import os

from abc import ABC, abstractmethod
from src.schema import FeedbackState

class BaseAgent(ABC):
    """
    BaseAgent
    - Abstract base class for all agents in the feedback pipeline
    - Ensures each agent implements a `process` method
    - Accepts and returns a FeedbackState object
    """

    @abstractmethod
    def process(self, state: FeedbackState) -> FeedbackState:
        """
        Process the given FeedbackState and return the updated state.
        Each agent should enrich or validate the state without breaking schema consistency.
        """
        pass