import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getMessages, sendMessage } from '../services/api';
import { websocketManager } from '../services/websocket';
import ISLCameraModal from '../components/ISLCameraModal';
import { useVoice } from '../services/useVoice';
import { ArrowLeft, Camera, Send, Wifi, WifiOff, Bot, Volume2, Square } from 'lucide-react';
import '../styles/ChatWindow.css';

interface Msg {
  id: string;
  sender_id: string;
  message_type: string;
  text_content: string;
  created_at: string;
  is_bot?: boolean;
}

export default function ChatWindow() {
  const { conversationId } = useParams<{ conversationId: string }>();
  const navigate = useNavigate();
  const userId   = JSON.parse(localStorage.getItem('user') || '{}').id ?? 'me';

  const [messages, setMessages]       = useState<Msg[]>([]);
  const [text, setText]               = useState('');
  const [loading, setLoading]         = useState(true);
  const [sending, setSending]         = useState(false);
  const [showCam, setShowCam]         = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [typing, setTyping]           = useState<Record<string,boolean>>({});
  const bottomRef = useRef<HTMLDivElement>(null);
  const typerRef  = useRef<number|null>(null);
  const { speak, stop, getState }     = useVoice();

  // ── WebSocket ─────────────────────────────────────────────────
  useEffect(() => {
    if (!conversationId) return;
    websocketManager.connect(conversationId);
    const uc = websocketManager.onConnectionChange(setWsConnected);
    const um = websocketManager.onMessage(data => {
      if (data.type === 'chat_message') {
        setMessages(p => {
          const dup = p.some(m => m.text_content===data.message && m.sender_id===data.sender
                               && Math.abs(new Date(m.created_at).getTime()-Date.now())<2000);
          if (dup) return p;
          return [...p, { id:`ws-${Date.now()}`, sender_id:data.sender, message_type:'text',
                          text_content:data.message, created_at:data.timestamp||new Date().toISOString() }];
        });
      } else if (data.type==='typing') {
        setTyping(p => ({ ...p, [data.user]: data.is_typing }));
      }
    });
    return () => { uc(); um(); websocketManager.disconnect(); };
  }, [conversationId]);

  // ── Load messages ─────────────────────────────────────────────
  useEffect(() => {
    if (!conversationId) return;
    (async () => {
      try { const r = await getMessages(conversationId); setMessages(r.messages||[]); }
      catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, [conversationId]);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior:'smooth' }); }, [messages]);

  // ── Send text ─────────────────────────────────────────────────
  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    const msg = text.trim();
    if (!msg || !conversationId) return;
    setText(''); setSending(true);
    const opt: Msg = { id:`opt-${Date.now()}`, sender_id:userId, message_type:'text',
                       text_content:msg, created_at:new Date().toISOString() };
    setMessages(p => [...p, opt]);
    try {
      if (wsConnected) websocketManager.sendMessage(msg, userId);
      await sendMessage(conversationId, 'text', msg);
    } catch {
      alert('Failed to send'); setMessages(p => p.filter(m => m.id!==opt.id)); setText(msg);
    } finally { setSending(false); }
  };

  const handleTyping = () => {
    if (!wsConnected) return;
    websocketManager.sendTypingIndicator(userId, true);
    if (typerRef.current) clearTimeout(typerRef.current);
    typerRef.current = window.setTimeout(() => websocketManager.sendTypingIndicator(userId, false), 2000);
  };

  // ── ISL camera result ─────────────────────────────────────────
  const handleISL = async (islText: string, botReply?: string) => {
    if (!conversationId) return;
    const userMsg: Msg = { id:`isl-${Date.now()}`, sender_id:userId, message_type:'sign',
                            text_content:`🤟 ${islText}`, created_at:new Date().toISOString() };
    setMessages(p => [...p, userMsg]);
    if (botReply) {
      const botMsg: Msg = { id:`bot-${Date.now()}`, sender_id:'ai', message_type:'text',
                             text_content:botReply, created_at:new Date().toISOString(), is_bot:true };
      setMessages(p => [...p, botMsg]);
    }
    try {
      if (wsConnected) websocketManager.sendMessage(`🤟 ${islText}`, userId);
      await sendMessage(conversationId, 'sign', `🤟 ${islText}`);
    } catch {}
  };

  const typingList = Object.entries(typing).filter(([uid,v]) => v && uid!==userId);

  if (loading) return <div className="cw-loading"><div className="spinner"/></div>;

  return (
    <div className="cw-container">
      {/* Header */}
      <div className="cw-header">
        <button className="cw-back" onClick={() => navigate('/chats')}><ArrowLeft size={22}/></button>
        <div className="cw-header-info">
          <span className="cw-title">Conversation</span>
          <span className={`cw-status ${wsConnected?'cw-on':'cw-off'}`}>
            {wsConnected ? <><Wifi size={12}/> Live</> : <><WifiOff size={12}/> Connecting…</>}
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="cw-messages">
        {messages.length===0 && (
          <div className="cw-empty">
            <p>No messages yet — say hello 👋 or use the camera 📷 to sign!</p>
          </div>
        )}

        {messages.map((m, i) => {
          const mine = m.sender_id===userId;
          const bot  = m.is_bot || m.sender_id==='ai';
          const vs   = getState(m.id);
          const cleanText = m.text_content.replace(/^🤟\s*/,'');

          return (
            <div key={m.id||i} className={`cw-row ${mine?'cw-row-mine':bot?'cw-row-bot':'cw-row-theirs'}`}>
              {bot && <span className="cw-bot-tag"><Bot size={11}/> AI</span>}
              <div className={`cw-bubble ${mine?'cw-mine':bot?'cw-bot-bubble':'cw-theirs'}`}>
                <span className="cw-text">{m.text_content}</span>
                <div className="cw-meta">
                  <span className="cw-time">
                    {new Date(m.created_at).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}
                  </span>
                  {/* ── Voice button ── */}
                  <button
                    className={`cw-voice-btn ${vs==='playing'?'cw-voice-active':''}`}
                    title={vs==='playing'?'Stop':'Play voice'}
                    onClick={() => vs==='playing' ? stop(m.id) : speak(m.id, cleanText)}
                  >
                    {vs==='loading' ? <span className="cw-voice-spin"/> :
                     vs==='playing' ? <Square size={11} fill="currentColor"/> :
                     <Volume2 size={12}/>}
                  </button>
                </div>
              </div>
            </div>
          );
        })}

        {typingList.length>0 && (
          <div className="cw-typing">
            <span>Someone is typing</span>
            <span className="cw-dots"><span/><span/><span/></span>
          </div>
        )}
        <div ref={bottomRef}/>
      </div>

      {/* ISL Modal */}
      <ISLCameraModal isOpen={showCam} onClose={() => setShowCam(false)} onTextReady={handleISL}/>

      {/* Input bar */}
      <form className="cw-input" onSubmit={handleSend}>
        <button type="button" className="cw-cam-btn" title="Sign Language Input" onClick={() => setShowCam(true)}>
          <Camera size={22}/>
        </button>
        <input
          value={text}
          onChange={e => { setText(e.target.value); handleTyping(); }}
          placeholder="Type a message or tap 📷 to sign…"
          disabled={sending}
        />
        <button type="submit" className="cw-send-btn" disabled={!text.trim()||sending}>
          <Send size={22}/>
        </button>
      </form>
    </div>
  );
}
