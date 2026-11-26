// WebSocket Manager for Real-Time Chat
class WebSocketManager {
  private ws: WebSocket | null = null;
  private conversationId: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private messageHandlers: ((data: any) => void)[] = [];
  private connectionHandlers: ((connected: boolean) => void)[] = [];

  connect(conversationId: string) {
    if (this.ws && this.conversationId === conversationId) {
      return; // Already connected to this conversation
    }

    this.disconnect();
    this.conversationId = conversationId;
    
    const wsUrl = `ws://127.0.0.1:8000/ws/chat/${conversationId}/`;
    console.log('[WebSocket] Connecting to:', wsUrl);

    try {
      this.ws = new WebSocket(wsUrl);
      this.setupEventHandlers();
    } catch (error) {
      console.error('[WebSocket] Connection error:', error);
      this.handleReconnect();
    }
  }

  private setupEventHandlers() {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('[WebSocket] Connected');
      this.reconnectAttempts = 0;
      this.notifyConnectionHandlers(true);
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('[WebSocket] Message received:', data);
        this.notifyMessageHandlers(data);
      } catch (error) {
        console.error('[WebSocket] Parse error:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('[WebSocket] Error:', error);
    };

    this.ws.onclose = () => {
      console.log('[WebSocket] Disconnected');
      this.notifyConnectionHandlers(false);
      this.handleReconnect();
    };
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.conversationId) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
      setTimeout(() => {
        if (this.conversationId) {
          this.connect(this.conversationId);
        }
      }, delay);
    }
  }

  sendMessage(message: string, sender: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'chat_message',
        message,
        sender,
        timestamp: new Date().toISOString(),
      }));
    } else {
      console.error('[WebSocket] Not connected');
    }
  }

  sendTypingIndicator(user: string, isTyping: boolean) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'typing',
        user,
        is_typing: isTyping,
      }));
    }
  }

  onMessage(handler: (data: any) => void) {
    this.messageHandlers.push(handler);
    return () => {
      this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
    };
  }

  onConnectionChange(handler: (connected: boolean) => void) {
    this.connectionHandlers.push(handler);
    return () => {
      this.connectionHandlers = this.connectionHandlers.filter(h => h !== handler);
    };
  }

  private notifyMessageHandlers(data: any) {
    this.messageHandlers.forEach(handler => handler(data));
  }

  private notifyConnectionHandlers(connected: boolean) {
    this.connectionHandlers.forEach(handler => handler(connected));
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.conversationId = null;
    this.reconnectAttempts = 0;
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export const websocketManager = new WebSocketManager();
