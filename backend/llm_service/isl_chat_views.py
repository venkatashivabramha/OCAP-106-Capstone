"""
ISL Chat views — integrated Phase 2 endpoints
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from recognition.sign_sequence_manager import get_sequence_manager
from llm_service.conversation_manager import get_conversation_manager
from llm_service.rag_manager import get_rag_manager
from llm_service.multi_llm_client import get_llm_client
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_sign_sequence(request):
    """
    POST /api/recognition/sequence/
    { "sign_label": "HELLO", "confidence": 0.95 }
    """
    sign_label = request.data.get('sign_label')
    confidence  = float(request.data.get('confidence', 1.0))
    if not sign_label:
        return Response({'error': 'sign_label required'}, status=400)

    uid    = str(request.user.id)
    result = get_sequence_manager().add_sign(uid, sign_label, confidence)
    return Response({'success': True, **result})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def flush_sign_sequence(request):
    """
    POST /api/recognition/flush/
    Force-finalise current sign sequence into a sentence.
    """
    uid  = str(request.user.id)
    text = get_sequence_manager().flush(uid)
    return Response({'success': True, 'sentence_text': text or ''})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def isl_chat(request):
    """
    POST /api/llm/isl-chat/
    { "text": "Hello how are you", "signs": ["HELLO","HOW","YOU"] }
    Runs RAG context retrieval then sends to Gemini.
    """
    text  = request.data.get('text', '').strip()
    signs = request.data.get('signs', [])
    if not text:
        return Response({'error': 'text required'}, status=400)

    uid = str(request.user.id)
    rag_ctx = get_rag_manager().context_string(text)
    result  = get_conversation_manager().chat(uid, text, rag_ctx)

    return Response({
        'success':             True,
        'user_message':        text,
        'bot_response':        result['bot_response'],
        'provider':            result['provider'],
        'rag_used':            bool(rag_ctx),
        'conversation_length': result['conversation_length'],
        'signs_used':          signs,
        'timestamp':           result['timestamp'],
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation_history(request):
    """GET /api/llm/history/?limit=10"""
    uid   = str(request.user.id)
    limit = int(request.GET.get('limit', 10))
    msgs  = get_conversation_manager().history(uid, limit)
    return Response({'success': True, 'messages': msgs, 'total': len(msgs)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_conversation(request):
    """POST /api/llm/clear/"""
    uid = str(request.user.id)
    get_conversation_manager().clear(uid)
    get_sequence_manager().clear(uid)
    return Response({'success': True, 'message': 'Cleared'})


@api_view(['GET'])
@permission_classes([AllowAny])
def llm_provider_status(request):
    """GET /api/llm/provider-status/"""
    return Response(get_llm_client().get_status())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_stats(request):
    """GET /api/llm/stats/"""
    uid = str(request.user.id)
    return Response({
        'success':     True,
        'sequences':   get_sequence_manager().stats(uid),
        'conversation':get_conversation_manager().stats(uid),
        'knowledge_base': get_rag_manager().stats(),
    })


# ══════════════════════════════════════════════════════════════
# TTS — text-to-speech for each chat message
# ══════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
def speak_message(request):
    """
    POST /api/llm/speak/
    { "text": "Hello, how are you?" }
    Returns: { "audio_b64": "<base64 WAV>", "provider": "gemini"|"browser" }

    When GEMINI_API_KEY is set, returns real synthesised audio.
    When not set, returns provider="browser" so the frontend uses
    the browser Web Speech API as a free fallback.
    """
    text = request.data.get('text', '').strip()
    if not text:
        return Response({'error': 'text required'}, status=400)

    from llm_service.tts_service import generate_speech
    audio_b64 = generate_speech(text)

    if audio_b64:
        return Response({'audio_b64': audio_b64, 'provider': 'gemini'})
    else:
        # Tell the frontend to use browser TTS
        return Response({'audio_b64': None, 'provider': 'browser', 'text': text})
