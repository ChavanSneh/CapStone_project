import requests
import os
import yaml
import json
import time
from src.utils.logger import logger

class LLMClient:
    def __init__(self, provider="google", api_key=None, config_path="config.yaml", model=None):
        config_data = self._load_config(config_path)
        llm_config = config_data.get('llm', {})

        # Switching to 'gemini-2.5-flash-lite' to use your 10 RPM quota
        self.model_name = model or llm_config.get('model') or "gemini-2.5-flash-lite"
        
        self.api_key = api_key or config_data.get('google_api_key') or llm_config.get('api_key') or os.getenv("GOOGLE_API_KEY")
        
        # 2026 v1beta endpoint
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

    def _load_config(self, path):
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return yaml.safe_load(f) or {}
            return {}
        except Exception as e:
            logger.error(f"LLMClient: Config load failed: {e}")
            return {}

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            return "ERROR: API Key Missing"
        
        # 3 Retries for 429 errors
        for attempt in range(3):
            try:
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                response = requests.post(self.url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get('candidates', [])
                    if candidates:
                        text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                        return text.strip()
                    return "ERROR: No text in response"
                
                elif response.status_code == 429:
                    wait = (attempt + 1) * 5 # Wait 5s, 10s, 15s
                    logger.warning(f"Quota Hit (429). Cooling down for {wait}s...")
                    time.sleep(wait)
                    continue
                
                else:
                    logger.error(f"API Error {response.status_code}: {response.text}")
                    return f"ERROR: API Status {response.status_code}"
                    
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        return "ERROR: Max retries reached (429)"