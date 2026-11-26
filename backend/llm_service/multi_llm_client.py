"""
Gemini-Only LLM Client (100% FREE tier)
Google Gemini API via AI Studio - no credit card required
"""

import requests
import os
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')


class GeminiClient:
    """Google Gemini API client"""

    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.base_url = 'https://generativelanguage.googleapis.com/v1beta'
        self.available = bool(self.api_key) and self._check()

    def _check(self) -> bool:
        try:
            url = f"{self.base_url}/models?key={self.api_key}"
            r = requests.get(url, timeout=5)
            return r.status_code == 200
        except Exception as e:
            logger.warning(f"Gemini unavailable: {e}")
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 300) -> Tuple[str, str]:
        """Generate text. Returns (text, provider)."""
        if not self.available:
            return self._fallback(prompt), 'fallback'

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        try:
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.7,
                },
            }
            url = f"{self.base_url}/models/{GEMINI_MODEL}:generateContent?key={self.api_key}"
            r = requests.post(url, json=payload, timeout=30)

            if r.status_code == 200:
                text = r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                return text, 'gemini'

            logger.error(f"Gemini API error: {r.status_code} - {r.text[:200]}")
            return self._fallback(prompt), 'fallback'

        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return self._fallback(prompt), 'fallback'

    def _fallback(self, prompt: str) -> str:
        """Simple rule-based reply when Gemini is not configured."""
        words = prompt.strip().split()
        if any(w.upper() in ('HELLO', 'HI', 'HEY') for w in words):
            return "Hello! How can I help you today?"
        if 'HELP' in prompt.upper():
            return "I'm here to help. What do you need?"
        if any(q in prompt.upper() for q in ('HOW', 'WHAT', 'WHY', 'WHERE')):
            return "That's a good question. Could you tell me more?"
        return "I understand. Please tell me more."

    def get_status(self) -> dict:
        return {
            'available': self.available,
            'providers': ['gemini'] if self.available else [],
            'primary': 'gemini' if self.available else None,
            'gemini': self.available,
            'groq': False,
            'ollama': False,
            'model': GEMINI_MODEL if self.available else None,
            'note': 'Add GEMINI_API_KEY to backend/.env to enable' if not self.available else None,
        }


_client = None

def get_llm_client() -> GeminiClient:
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
