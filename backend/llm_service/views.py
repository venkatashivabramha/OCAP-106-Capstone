"""
LLM API Views
AI-powered features using Ollama
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from llm_service.ollama_client import get_ollama_client
from llm_service.isl_chatbot import get_isl_chatbot
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def translate_signs(request):
    """
    Translate sequence of ISL signs to English sentence
    POST /api/llm/translate-signs/
    Body: { "signs": ["H", "E", "L", "L", "O"] }
    """
    try:
        signs = request.data.get('signs', [])
        
        if not signs:
            return Response({'error': 'No signs provided'}, status=400)
        
        client = get_ollama_client()
        
        if not client.available:
            # Fallback: just join the signs
            return Response({
                'translation': " ".join(signs),
                'source': 'fallback',
                'note': 'Ollama not available, showing raw signs'
            })
        
        translation = client.translate_signs_to_text(signs)
        
        return Response({
            'signs': signs,
            'translation': translation,
            'source': 'ollama'
        })
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def convert_to_isl(request):
    """
    Convert English text to ISL grammar format
    POST /api/llm/convert-to-isl/
    Body: { "text": "I am going to the market tomorrow" }
    """
    try:
        text = request.data.get('text', '')
        
        if not text:
            return Response({'error': 'No text provided'}, status=400)
        
        client = get_ollama_client()
        
        if not client.available:
            return Response({
                'isl_format': text.upper(),
                'source': 'fallback',
                'note': 'Ollama not available'
            })
        
        isl_format = client.convert_to_isl_grammar(text)
        
        return Response({
            'english': text,
            'isl_format': isl_format,
            'source': 'ollama'
        })
        
    except Exception as e:
        logger.error(f"ISL conversion error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def suggest_responses(request):
    """
    Get AI-powered response suggestions based on conversation context
    POST /api/llm/suggest-responses/
    Body: {
        "context": [
            {"sender": "User1", "text": "Hello!"},
            {"sender": "User2", "text": "Hi, how are you?"}
        ],
        "num_suggestions": 3
    }
    """
    try:
        context = request.data.get('context', [])
        num_suggestions = request.data.get('num_suggestions', 3)
        
        client = get_ollama_client()
        
        if not client.available:
            return Response({
                'suggestions': ["Thank you!", "I understand", "Tell me more"],
                'source': 'fallback'
            })
        
        suggestions = client.suggest_responses(context, num_suggestions)
        
        return Response({
            'suggestions': suggestions,
            'source': 'ollama'
        })
        
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def explain_sign(request):
    """
    Get explanation of how to perform an ISL sign
    POST /api/llm/explain-sign/
    Body: { "sign": "thank you" }
    """
    try:
        sign_name = request.data.get('sign', '')
        
        if not sign_name:
            return Response({'error': 'No sign name provided'}, status=400)
        
        client = get_ollama_client()
        
        if not client.available:
            return Response({
                'sign': sign_name,
                'explanation': f"To perform the sign for '{sign_name}', please refer to an ISL dictionary or video resource.",
                'source': 'fallback'
            })
        
        explanation = client.explain_sign(sign_name)
        
        return Response({
            'sign': sign_name,
            'explanation': explanation,
            'source': 'ollama'
        })
        
    except Exception as e:
        logger.error(f"Sign explanation error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def summarize_conversation(request):
    """
    Summarize a conversation thread
    POST /api/llm/summarize/
    Body: {
        "messages": [
            {"sender": "User1", "text": "Hello!"},
            {"sender": "User2", "text": "Hi!"}
        ]
    }
    """
    try:
        messages = request.data.get('messages', [])
        
        if not messages:
            return Response({'error': 'No messages provided'}, status=400)
        
        client = get_ollama_client()
        
        if not client.available:
            return Response({
                'summary': f"Conversation with {len(messages)} messages",
                'source': 'fallback'
            })
        
        summary = client.summarize_conversation(messages)
        
        return Response({
            'message_count': len(messages),
            'summary': summary,
            'source': 'ollama'
        })
        
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def llm_status(request):
    """
    Check LLM service status
    GET /api/llm/status/
    """
    try:
        client = get_ollama_client()
        
        return Response({
            'available': client.available,
            'model': client.model if client.available else None,
            'base_url': client.base_url,
            'features': [
                'Sign Translation',
                'ISL Grammar Conversion',
                'Response Suggestions',
                'Sign Explanations',
                'Conversation Summarization',
                'ISL Chatbot Practice'
            ] if client.available else []
        })
        
    except Exception as e:
        return Response({
            'available': False,
            'error': str(e)
        })


# ============================================
# ISL CHATBOT ENDPOINTS
# ============================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot_start(request):
    """
    Start a new ISL practice conversation
    POST /api/llm/chatbot/start/
    Body: { "session_id": "optional-custom-id" }
    """
    try:
        session_id = request.data.get('session_id', f"user_{request.user.id}")
        
        chatbot = get_isl_chatbot()
        greeting = chatbot.start_conversation(session_id)
        
        return Response({
            'session_id': session_id,
            'greeting': greeting,
            'status': 'started'
        })
        
    except Exception as e:
        logger.error(f"Chatbot start error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot_message(request):
    """
    Send message to ISL chatbot
    POST /api/llm/chatbot/chat/
    Body: {
        "session_id": "user_123",
        "message": "Hello, how are you?",
        "recognized_sign": "HELLO"  # optional
    }
    """
    try:
        session_id = request.data.get('session_id', f"user_{request.user.id}")
        message = request.data.get('message', '')
        recognized_sign = request.data.get('recognized_sign')
        
        if not message and not recognized_sign:
            return Response({'error': 'Message or recognized_sign required'}, status=400)
        
        # If only sign provided, use it as message
        if not message and recognized_sign:
            message = recognized_sign
        
        chatbot = get_isl_chatbot()
        result = chatbot.chat(session_id, message, recognized_sign)
        
        return Response({
            'session_id': session_id,
            'user_message': message,
            'recognized_sign': recognized_sign,
            'bot_response': result['response'],
            'practice_suggestions': result['suggestions'],
            'conversation_length': result['conversation_history']
        })
        
    except Exception as e:
        logger.error(f"Chatbot chat error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot_reset(request):
    """
    Reset ISL chatbot conversation
    POST /api/llm/chatbot/reset/
    Body: { "session_id": "user_123" }
    """
    try:
        session_id = request.data.get('session_id', f"user_{request.user.id}")
        
        chatbot = get_isl_chatbot()
        chatbot.reset_conversation(session_id)
        
        # Start fresh conversation
        greeting = chatbot.start_conversation(session_id)
        
        return Response({
            'session_id': session_id,
            'greeting': greeting,
            'status': 'reset'
        })
        
    except Exception as e:
        logger.error(f"Chatbot reset error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot_explain_sign(request):
    """
    Get explanation for a specific ISL sign
    POST /api/llm/chatbot/explain/
    Body: { "sign": "THANK_YOU" }
    """
    try:
        sign_name = request.data.get('sign', '')
        
        if not sign_name:
            return Response({'error': 'Sign name required'}, status=400)
        
        chatbot = get_isl_chatbot()
        explanation = chatbot.get_sign_explanation(sign_name)
        
        return Response({
            'sign': sign_name,
            'explanation': explanation
        })
        
    except Exception as e:
        logger.error(f"Sign explanation error: {e}")
        return Response({'error': str(e)}, status=500)
