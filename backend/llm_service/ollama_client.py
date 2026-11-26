"""
Ollama LLM Integration for ISL Chat
Provides AI-powered features using local Ollama models
"""

import requests
import json
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url
        self.model = model
        self.available = self._check_availability()
        
    def _check_availability(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                is_available = any(self.model in name for name in model_names)
                if is_available:
                    logger.info(f"Ollama is available with model: {self.model}")
                else:
                    logger.warning(f"Ollama is running but model {self.model} not found")
                return is_available
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
        return False
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text completion using Ollama"""
        if not self.available:
            logger.warning("Ollama not available, returning fallback")
            return ""
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return ""
    
    def translate_signs_to_text(self, signs: List[str]) -> str:
        """Convert sequence of ISL signs to natural English sentence"""
        if not signs:
            return ""
        
        signs_str = " ".join(signs)
        
        prompt = f"""Convert this sequence of Indian Sign Language (ISL) finger-spelled letters into a proper English sentence:

Signs: {signs_str}

Rules:
- Combine letters into words
- Add proper spacing and punctuation
- Make it grammatically correct
- Keep it natural and conversational

English sentence:"""
        
        system_prompt = "You are an ISL (Indian Sign Language) translation assistant. Convert finger-spelled signs into proper English sentences."
        
        result = self.generate(prompt, system_prompt)
        return result or " ".join(signs)  # Fallback to original if generation fails
    
    def convert_to_isl_grammar(self, english_text: str) -> str:
        """Convert English sentence to ISL grammar/word order"""
        if not english_text:
            return ""
        
        prompt = f"""Convert this English sentence to Indian Sign Language (ISL) grammar format:

English: {english_text}

ISL Grammar Rules:
- Subject-Object-Verb word order (not Subject-Verb-Object)
- No articles (a, an, the)
- No helping verbs (is, am, are, was, were)
- Time expressions come first
- Question words at the end
- Use uppercase for signs

Example:
English: "I am going to the market tomorrow"
ISL: "TOMORROW MARKET I GO"

ISL format:"""
        
        system_prompt = "You are an ISL grammar expert. Convert English sentences to ISL sign order format."
        
        result = self.generate(prompt, system_prompt)
        return result.upper() if result else english_text.upper()
    
    def suggest_responses(self, conversation_context: List[Dict], num_suggestions: int = 3) -> List[str]:
        """Generate contextual response suggestions"""
        if not conversation_context:
            return ["Hello!", "How are you?", "Nice to meet you!"]
        
        # Build context from last few messages
        context_text = "\n".join([
            f"{msg.get('sender', 'User')}: {msg.get('text', '')}"
            for msg in conversation_context[-5:]  # Last 5 messages
        ])
        
        prompt = f"""Based on this ISL chat conversation, suggest {num_suggestions} appropriate short responses:

Conversation:
{context_text}

Generate {num_suggestions} natural, friendly response suggestions that would make sense in ISL chat context. Keep them simple and conversational.

Suggestions (one per line):"""
        
        system_prompt = "You are an ISL chat assistant helping users communicate naturally."
        
        result = self.generate(prompt, system_prompt)
        
        if result:
            suggestions = [s.strip() for s in result.split('\n') if s.strip()]
            # Remove numbering if present (1., 2., etc.)
            suggestions = [s.split('. ', 1)[-1] if '. ' in s else s for s in suggestions]
            return suggestions[:num_suggestions]
        
        return ["Thank you!", "I understand", "Tell me more"]
    
    def explain_sign(self, sign_name: str) -> str:
        """Explain how to perform an ISL sign"""
        if not sign_name:
            return ""
        
        prompt = f"""Explain how to perform the Indian Sign Language (ISL) sign for "{sign_name}":

Provide:
1. Hand shape
2. Movement direction
3. Location (where to place hand)
4. Any facial expressions

Keep it simple and clear for beginners.

Explanation:"""
        
        system_prompt = "You are an ISL teacher explaining sign language gestures clearly."
        
        result = self.generate(prompt, system_prompt)
        return result or f"Sign for '{sign_name}' - Please refer to ISL dictionary for details."
    
    def summarize_conversation(self, messages: List[Dict]) -> str:
        """Summarize a conversation thread"""
        if not messages:
            return "No messages to summarize."
        
        conversation_text = "\n".join([
            f"{msg.get('sender', 'User')}: {msg.get('text', '')}"
            for msg in messages
        ])
        
        prompt = f"""Summarize this ISL chat conversation in 2-3 sentences:

{conversation_text}

Summary:"""
        
        system_prompt = "You are a conversation summarizer. Create concise, accurate summaries."
        
        result = self.generate(prompt, system_prompt)
        return result or "Conversation about general topics."

# Global client instance
_ollama_client = None

def get_ollama_client() -> OllamaClient:
    """Get or create Ollama client singleton"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client
