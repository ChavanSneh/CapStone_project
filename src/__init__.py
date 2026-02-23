import streamlit as st
import requests
import os
import yaml
import json
from src.utils.logger import logger

class LLMClient:
    def __init__(self, provider="google", api_key=None, config_path="config.yaml", model=None):
        config_data = self._load_config(config_path)
        llm_config = config_data.get('llm', {})

        # Priority: 1. Manual Arg -> 2. Streamlit Cloud Secret -> 3. Config File -> 4. Env Var
        self.api_key = (
            api_key or 
            st.secrets.get("GEMINI_API_KEY") or 
            llm_config.get('api_key') or 
            config_data.get('google_api_key') or 
            os.getenv("GOOGLE_API_KEY")
        )
        
        if not self.api_key:
            st.error("Missing API Key! Please add GEMINI_API_KEY to Streamlit Secrets or config.yaml")
            return

        self.model_name = model or llm_config.get('model') or "gemini-1.5-flash"
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
    def _load_api_key(self, path):
        """Helper to pull the key from config.yaml if it exists"""
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    config = yaml.safe_load(f)
                    if config:
                        # Checks for various possible naming conventions in your YAML
                        return config.get('google_api_key') or config.get('api_key') or config.get('GOOGLE_API_KEY')
            return None
        except Exception as e:
            logger.error(f"Failed to load config.yaml: {e}")
            return None

    def generate(self, prompt: str) -> str:
        """Sends the prompt to the LLM and returns the text response."""
        if not self.api_key:
            return "ERROR: No API Key found. Check config.yaml"

        try:
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(self.url, json=payload, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Gemini API Error {response.status_code}: {response.text}")
                return f"ERROR: API Status {response.status_code}"

            data = response.json()
            # Navigate the JSON structure returned by Gemini
            candidates = data.get('candidates', [])
            if not candidates:
                return "ERROR: No response candidates"
                
            return candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            
        except Exception as e:
            logger.error(f"LLM Client Critical Failure: {e}")
            return f"ERROR: {str(e)}"