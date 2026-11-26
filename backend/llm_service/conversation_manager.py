"""
Task 2.2 — Conversation Manager
Maintains per-user chat history, calls Gemini, returns responses.
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
from llm_service.multi_llm_client import get_llm_client

logger = logging.getLogger(__name__)
MAX_HISTORY = 10

SYSTEM_PROMPT = """You are a friendly assistant for an Indian Sign Language (ISL) chat app.
Users communicate via sign language converted to text — keep replies short (1-3 sentences),
simple, and encouraging. If input is unclear, politely ask for clarification."""


class ConversationHistory:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.messages: List[Dict] = []
        self.started_at = datetime.now()

    def add(self, role: str, content: str):
        self.messages.append({'role': role, 'content': content, 'ts': datetime.now().isoformat()})
        if len(self.messages) > MAX_HISTORY:
            self.messages = self.messages[-MAX_HISTORY:]

    def context(self, n: int = 6) -> str:
        recent = self.messages[-n:]
        if not recent:
            return "(new conversation)"
        lines = [f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}" for m in recent]
        return "\n".join(lines)

    def clear(self):
        self.messages = []

    def stats(self) -> Dict:
        u = sum(1 for m in self.messages if m['role'] == 'user')
        return {
            'total_messages': len(self.messages),
            'user_messages': u,
            'bot_messages': len(self.messages) - u,
            'started_at': self.started_at.isoformat(),
        }


class ConversationManager:
    def __init__(self):
        self._store: Dict[str, ConversationHistory] = {}
        self.llm = get_llm_client()

    def _hist(self, uid: str) -> ConversationHistory:
        if uid not in self._store:
            self._store[uid] = ConversationHistory(uid)
        return self._store[uid]

    def chat(self, user_id: str, text: str, rag_context: str = '') -> Dict:
        hist = self._hist(user_id)
        hist.add('user', text)

        prompt = f"{hist.context()}\n\nUser just signed: {text}"
        if rag_context:
            prompt += f"\n\n{rag_context}"
        prompt += "\n\nReply:"

        response, provider = self.llm.generate(prompt, SYSTEM_PROMPT, max_tokens=200)
        hist.add('assistant', response)

        return {
            'user_message': text,
            'bot_response': response,
            'provider': provider,
            'conversation_length': len(hist.messages),
            'timestamp': datetime.now().isoformat(),
        }

    def history(self, user_id: str, limit: int = 10) -> List[Dict]:
        return self._hist(user_id).messages[-limit:]

    def clear(self, user_id: str):
        self._hist(user_id).clear()

    def stats(self, user_id: str) -> Dict:
        return self._hist(user_id).stats()


_mgr = None

def get_conversation_manager() -> ConversationManager:
    global _mgr
    if _mgr is None:
        _mgr = ConversationManager()
    return _mgr
