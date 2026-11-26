"""
ISL Chatbot for Conversation Practice
Helps users practice ISL with AI-powered conversational partner
"""

from typing import List, Dict, Optional
from .ollama_client import get_ollama_client
import logging

logger = logging.getLogger(__name__)

ISL_SYSTEM_PROMPT = """You are an ISL (Indian Sign Language) practice chatbot helper.

Your role:
- Help users practice basic ISL conversations
- Respond in simple, ISL-appropriate language
- Use ISL grammar patterns (Subject-Object-Verb order)
- Keep sentences short and clear (5-8 words max)
- Be encouraging and patient
- Suggest signs to practice

ISL Grammar Rules:
- Subject-Object-Verb word order (not Subject-Verb-Object)
- No articles (a, an, the)
- Minimal use of helping verbs
- Time expressions first
- Question words often at end
- Simple present tense preferred

Examples of ISL-style responses:
- "Hello! You name what?" (not "What is your name?")
- "I help you sign learn" (not "I will help you learn signing")
- "Today you good?" (not "How are you today?")
- "You try sign: THANK_YOU" (suggesting practice)

Be friendly, supportive, and focused on helping users practice ISL communication."""

class ISLChatbot:
    """ISL Conversation Practice Chatbot"""
    
    def __init__(self):
        self.client = get_ollama_client()
        self.conversations = {}  # Store conversation history by session_id
    
    def start_conversation(self, session_id: str) -> str:
        """Start a new ISL practice conversation"""
        self.conversations[session_id] = []
        
        greetings = [
            "Hello! I ISL helper. You practice with me. You name what?",
            "Hi! I help you ISL learn. We start? You ready?",
            "Welcome! Today we ISL practice. You good?",
        ]
        
        import random
        greeting = random.choice(greetings)
        
        self.conversations[session_id].append({
            'role': 'assistant',
            'content': greeting
        })
        
        return greeting
    
    def chat(self, session_id: str, user_message: str, recognized_sign: Optional[str] = None) -> Dict:
        """
        Process user message and generate ISL-appropriate response
        
        Args:
            session_id: Unique session identifier
            user_message: User's text message or typed input
            recognized_sign: Optional recognized sign from camera (e.g., "HELLO", "THANK_YOU")
        
        Returns:
            Dict with:
                - response: Bot's ISL-style response
                - suggestions: Suggested signs to practice
                - explanation: Optional explanation of signs
        """
        
        # Initialize conversation if needed
        if session_id not in self.conversations:
            self.start_conversation(session_id)
        
        # Build context from conversation history
        context = self.conversations[session_id][-10:]  # Last 10 messages
        
        # Add user message to history
        display_message = user_message
        if recognized_sign:
            display_message = f"[SIGNED: {recognized_sign}] {user_message}"
        
        context.append({
            'role': 'user',
            'content': user_message,
            'sign': recognized_sign
        })
        
        # Generate ISL-appropriate response
        response_text = self._generate_response(context, user_message, recognized_sign)
        
        # Add bot response to history
        context.append({
            'role': 'assistant',
            'content': response_text
        })
        
        self.conversations[session_id] = context
        
        # Generate practice suggestions
        suggestions = self._get_practice_suggestions(user_message, recognized_sign)
        
        return {
            'response': response_text,
            'suggestions': suggestions,
            'conversation_history': len(context),
            'practice_mode': True
        }
    
    def _generate_response(self, context: List[Dict], user_message: str, recognized_sign: Optional[str]) -> str:
        """Generate ISL-appropriate conversational response"""
        
        if not self.client.available:
            # Fallback responses when Ollama is not available
            return self._get_fallback_response(user_message, recognized_sign)
        
        # Build conversation context for LLM
        context_text = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Bot'}: {msg['content']}"
            for msg in context[-5:]  # Last 5 exchanges
        ])
        
        sign_context = f"\n(User just performed sign: {recognized_sign})" if recognized_sign else ""
        
        prompt = f"""Previous conversation:
{context_text}
{sign_context}

User's latest message: {user_message}

Respond in ISL-appropriate style:
- Use simple words
- Keep it short (5-8 words)
- Use ISL grammar (Subject-Object-Verb)
- Be encouraging
- Optionally suggest a sign to practice

Your response:"""
        
        response = self.client.generate(prompt, ISL_SYSTEM_PROMPT)
        
        return response if response else self._get_fallback_response(user_message, recognized_sign)
    
    def _get_fallback_response(self, user_message: str, recognized_sign: Optional[str]) -> str:
        """Fallback responses when LLM is not available"""
        
        message_lower = user_message.lower()
        
        # Greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! You good? We practice sign today?"
        
        # Name
        if 'name' in message_lower or 'called' in message_lower:
            return "My name ISL-BOT. I help you sign learn. You name what?"
        
        # Questions about learning
        if 'learn' in message_lower or 'teach' in message_lower or 'how' in message_lower:
            return "Good! You want learn? We start simple. Try sign: HELLO"
        
        # Thank you
        if 'thank' in message_lower:
            return "You welcome! You practice good. Try more sign!"
        
        # Recognition of a sign
        if recognized_sign:
            return f"Good! You sign {recognized_sign} correct! Try another?"
        
        # General response
        return "I understand. We practice more? You try next sign!"
    
    def _get_practice_suggestions(self, user_message: str, recognized_sign: Optional[str]) -> List[str]:
        """Suggest signs for user to practice next"""
        
        # Common conversation flow suggestions
        conversation_suggestions = {
            'greetings': ['HELLO', 'GOOD_MORNING', 'NICE_TO_MEET_YOU'],
            'courtesy': ['THANK_YOU', 'PLEASE', 'SORRY'],
            'questions': ['WHAT', 'WHERE', 'WHO', 'HOW'],
            'responses': ['YES', 'NO', 'OK', 'UNDERSTAND'],
            'daily': ['EAT', 'DRINK', 'WATER', 'HOME', 'WORK'],
            'feelings': ['HAPPY', 'GOOD', 'FINE', 'HELP']
        }
        
        message_lower = user_message.lower()
        
        # Suggest based on context
        if any(word in message_lower for word in ['hello', 'hi', 'start', 'begin']):
            return conversation_suggestions['greetings']
        elif any(word in message_lower for word in ['thank', 'please', 'sorry']):
            return conversation_suggestions['courtesy']
        elif 'question' in message_lower or '?' in user_message:
            return conversation_suggestions['questions']
        elif any(word in message_lower for word in ['eat', 'hungry', 'food', 'drink']):
            return conversation_suggestions['daily']
        elif any(word in message_lower for word in ['feel', 'happy', 'sad', 'good']):
            return conversation_suggestions['feelings']
        else:
            return conversation_suggestions['responses']
    
    def get_sign_explanation(self, sign_name: str) -> str:
        """Get explanation of how to perform a specific sign"""
        return self.client.explain_sign(sign_name)
    
    def reset_conversation(self, session_id: str):
        """Reset conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]


# Global chatbot instance
_chatbot_instance = None

def get_isl_chatbot() -> ISLChatbot:
    """Get or create ISL chatbot singleton"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = ISLChatbot()
    return _chatbot_instance
