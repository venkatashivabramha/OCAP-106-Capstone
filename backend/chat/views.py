from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json, uuid, threading

# In-memory store (fine for demo; replace with DB for production)
_lock = threading.Lock()
_rooms = {}   # room_id -> list of messages
_users = {}   # username -> room_id

DEFAULT_ROOM = 'main'

@csrf_exempt
def join(request):
    if request.method != 'POST': return JsonResponse({'error':'POST only'},status=405)
    data = json.loads(request.body)
    username = data.get('username','').strip()[:30]
    if not username: return JsonResponse({'error':'username required'},status=400)
    room = data.get('room', DEFAULT_ROOM)
    with _lock:
        _users[username] = room
        if room not in _rooms: _rooms[room] = []
    return JsonResponse({'ok':True,'username':username,'room':room})

@csrf_exempt
def messages(request):
    room = request.GET.get('room', DEFAULT_ROOM)
    since = int(request.GET.get('since', 0))
    msgs = _rooms.get(room, [])
    return JsonResponse({'messages': msgs[since:], 'total': len(msgs)})

def users(request):
    room = request.GET.get('room', DEFAULT_ROOM)
    online = [u for u,r in _users.items() if r == room]
    return JsonResponse({'users': online})


@csrf_exempt
def send_message(request):
    """HTTP fallback for sending messages when WebSocket is unavailable"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    data = json.loads(request.body)
    username = data.get('username', 'Anonymous')
    room = data.get('room', DEFAULT_ROOM)
    text = data.get('text', '').strip()
    is_isl = data.get('is_isl', False)

    if not text:
        return JsonResponse({'error': 'text required'}, status=400)

    msg = {
        'id': str(uuid.uuid4())[:8],
        'type': 'chat_message',
        'sender': username,
        'text': text,
        'is_isl': is_isl,
        'timestamp': __import__('datetime').datetime.now().isoformat(),
    }

    with _lock:
        if room not in _rooms:
            _rooms[room] = []
        _rooms[room].append(msg)
        if len(_rooms[room]) > 200:
            _rooms[room] = _rooms[room][-200:]

    return JsonResponse({'ok': True, 'message': msg})