import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime

# In-memory message store (shared across all consumer instances)
ROOMS = {}   # room -> [msg, ...]

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room = self.scope['url_route']['kwargs'].get('conversation_id', 'main')
        self.group = f'chat_{self.room}'
        self.username = self.scope.get('query_string', b'').decode()
        # parse ?user=xxx from query string
        qs = self.scope.get('query_string', b'').decode()
        for part in qs.split('&'):
            if part.startswith('user='):
                self.username = part[5:]

        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

        # Send history
        history = ROOMS.get(self.room, [])
        await self.send(text_data=json.dumps({'type': 'history', 'messages': history}))

        # Announce join
        await self.channel_layer.group_send(self.group, {
            'type': 'chat_event',
            'payload': {'type': 'join', 'user': self.username, 'timestamp': _now()}
        })

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)
        await self.channel_layer.group_send(self.group, {
            'type': 'chat_event',
            'payload': {'type': 'leave', 'user': self.username, 'timestamp': _now()}
        })

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type', 'chat_message')

        if msg_type == 'chat_message':
            msg = {
                'id': _id(),
                'type': 'chat_message',
                'sender': data.get('sender', self.username),
                'text': data.get('message', ''),
                'is_isl': data.get('is_isl', False),
                'timestamp': _now(),
            }
            # Store message
            if self.room not in ROOMS:
                ROOMS[self.room] = []
            ROOMS[self.room].append(msg)
            if len(ROOMS[self.room]) > 200:
                ROOMS[self.room] = ROOMS[self.room][-200:]

            # Broadcast to room
            await self.channel_layer.group_send(self.group, {
                'type': 'chat_event', 'payload': msg
            })

            # If ISL message, get AI response
            if data.get('is_isl') and data.get('message'):
                ai_text = await _get_ai_response(data['message'], self.room)
                if ai_text:
                    ai_msg = {
                        'id': _id(),
                        'type': 'chat_message',
                        'sender': 'AI Assistant',
                        'text': ai_text,
                        'is_bot': True,
                        'timestamp': _now(),
                    }
                    ROOMS[self.room].append(ai_msg)
                    await self.channel_layer.group_send(self.group, {
                        'type': 'chat_event', 'payload': ai_msg
                    })

        elif msg_type == 'typing':
            await self.channel_layer.group_send(self.group, {
                'type': 'chat_event',
                'payload': {'type': 'typing', 'user': data.get('user', self.username), 'is_typing': data.get('is_typing', False)}
            })

    async def chat_event(self, event):
        await self.send(text_data=json.dumps(event['payload']))


def _now():
    return datetime.now().isoformat()

def _id():
    import uuid
    return str(uuid.uuid4())[:8]

async def _get_ai_response(isl_text, room):
    try:
        import os, asyncio
        from llm_service.multi_llm_client import get_llm_client
        from llm_service.rag_manager import get_rag_manager
        from llm_service.conversation_manager import get_conversation_manager

        rag_ctx = get_rag_manager().context_string(isl_text)
        cm = get_conversation_manager()
        result = cm.chat(f'room_{room}', isl_text, rag_ctx)
        return result.get('bot_response', '')
    except Exception as e:
        return f"I understood: {isl_text}"
