import requests
import os
import yaml
import json
import time
import streamlit as st  # Added for Cloud Secrets
from src.utils.logger import logger

class LLMClient:
    def __init__(self, provider="google", api_key=None, config_path="config.yaml", model=None):
        config_data = self._load_config(config_path)
        llm_config = config_data.get('llm', {})

        # 1. Set Model Name (Using the 2026 stable string for v1/v1beta)
        # We use gemini-2.5-flash-lite as the default if nothing else is provided
        self.model_name = model or llm_config.get('model') or "gemini-2.5-flash-lite"
        
        # 2. Key Hierarchy: Manual Arg -> Streamlit Secrets (Cloud) -> Config File -> Env Var
        self.api_key = (
            api_key or 
            st.secrets.get("GEMINI_API_KEY") or 
            config_data.get('google_api_key') or 
            llm_config.get('api_key') or 
            os.getenv("GOOGLE_API_KEY")
        )
        
        # 3. API Endpoint (Using v1 for stability since you mentioned you use v1)
        # We use the 'v1' path instead of 'v1beta' for the 2.5 stable release
        self.url = f"https://generativelanguage.googleapis.com/v1/models/{self.model_name}:generateContent?key={self.api_key}"

    def _load_config(self, path):
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return yaml.safe_load(f) or {}
            else:
                logger.warning(f"Config file {path} not found. Falling back to Environment/Secrets.")
                return {}
        except Exception as e:
            logger.error(f"LLMClient: Config load failed: {e}")
            return {}

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            return "ERROR: API Key Missing. Check Streamlit Secrets or config.yaml"
        
        # If the model gets "stuck", this retry loop will attempt to kickstart it
        for attempt in range(3):
            try:
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                response = requests.post(self.url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get('candidates', [])
                    if candidates:
                        text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                        if not text:
                            # This is the 'stuck' case where AI returns empty
                            return "stuck"
                        return text.strip()
                    return "stuck"
                
                elif response.status_code == 429:
                    wait = (attempt + 1) * 5 
                    logger.warning(f"Quota Hit (429). Cooling down for {wait}s...")
                    time.sleep(wait)
                    continue
                
                else:
                    logger.error(f"API Error {response.status_code}: {response.text}")
                    # Per your instruction: if the API fails, we treat the output as 'stuck'
                    return "stuck"
                    
            except Exception as e:
                logger.error(f"LLM Connection Error: {e}")
                return "stuck"
        
        return "stuck"