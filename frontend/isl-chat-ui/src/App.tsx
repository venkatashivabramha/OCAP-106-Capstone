import { useState, useEffect, useRef } from 'react';
import './App.css';

const WS_BASE = window.location.hostname === 'localhost'
  ? 'ws://127.0.0.1:8000'
  : `wss://${window.location.host}`;
const API_BASE = '/api';

interface Message {
  id: string;
  type: string;
  sender: string;
  text: string;
  is_isl?: boolean;
  is_bot?: boolean;
  timestamp: string;
}

export default function App() {
  const [screen, setScreen] = useState<'join'|'chat'>('join');
  const [username, setUsername] = useState('');
  const [room] = useState('main');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
  const [typingUsers, setTypingUsers] = useState<string[]>([]);
  const [wsReady, setWsReady] = useState(false);
  const [showCam, setShowCam] = useState(false);
  const ws = useRef<WebSocket|null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const typerRef = useRef<number|null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream|null>(null);
  const [signSeq, setSignSeq] = useState<string[]>([]);
  const [capturing, setCapturing] = useState(false);
  const captureRef = useRef<number|null>(null);
  const msgCount = useRef(0);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const connect = (name: string) => {
    const socket = new WebSocket(`${WS_BASE}/ws/chat/${room}/?user=${encodeURIComponent(name)}`);
    socket.onopen = () => { setWsReady(true); };
    socket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === 'history') {
        setMessages(data.messages || []);
        msgCount.current = (data.messages||[]).length;
      } else if (data.type === 'chat_message') {
        setMessages(p => [...p, data]);
        msgCount.current++;
      } else if (data.type === 'typing') {
        if (data.user !== name) {
          setTypingUsers(p => data.is_typing ? [...new Set([...p, data.user])] : p.filter(u => u !== data.user));
        }
      } else if (data.type === 'join' || data.type === 'leave') {
        fetchUsers();
      }
    };
    socket.onclose = () => setWsReady(false);
    ws.current = socket;
  };

  const fetchUsers = async () => {
    try {
      const r = await fetch(`${API_BASE}/chat/users/?room=${room}`);
      const d = await r.json();
      setOnlineUsers(d.users || []);
    } catch {}
  };

  const handleJoin = async (e: React.FormEvent) => {
    e.preventDefault();
    const name = username.trim();
    if (!name) return;
    await fetch(`${API_BASE}/chat/join/`, {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ username: name, room })
    });
    connect(name);
    setScreen('chat');
    fetchUsers();
  };

  const send = (text: string, isIsl = false) => {
    if (!text.trim() || !ws.current || ws.current.readyState !== 1) return;
    ws.current.send(JSON.stringify({ type:'chat_message', sender:username, message:text, is_isl:isIsl }));
    setInput('');
  };

  const handleSend = (e: React.FormEvent) => { e.preventDefault(); send(input); };

  const handleTyping = () => {
    if (!ws.current || ws.current.readyState !== 1) return;
    ws.current.send(JSON.stringify({ type:'typing', user:username, is_typing:true }));
    if (typerRef.current) clearTimeout(typerRef.current);
    typerRef.current = window.setTimeout(() => {
      ws.current?.send(JSON.stringify({ type:'typing', user:username, is_typing:false }));
    }, 2000);
  };

  // Voice playback
  const speak = async (text: string) => {
    try {
      const r = await fetch(`${API_BASE}/llm/speak/`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ text })
      });
      const d = await r.json();
      if (d.audio_b64) {
        const bytes = Uint8Array.from(atob(d.audio_b64), c => c.charCodeAt(0));
        const blob = new Blob([bytes], { type:'audio/wav' });
        new Audio(URL.createObjectURL(blob)).play();
      } else {
        const u = new SpeechSynthesisUtterance(text);
        u.lang = 'en-IN'; u.rate = 0.95;
        window.speechSynthesis.speak(u);
      }
    } catch {
      const u = new SpeechSynthesisUtterance(text);
      u.lang = 'en-IN';
      window.speechSynthesis.speak(u);
    }
  };

  // ISL Camera
  const startCam = async () => {
    try {
      const s = await navigator.mediaDevices.getUserMedia({ video:{width:640,height:480,facingMode:'user'} });
      streamRef.current = s;
      if (videoRef.current) { videoRef.current.srcObject = s; await videoRef.current.play(); }
      setShowCam(true);
    } catch { alert('Camera access denied'); }
  };

  const stopCam = () => {
    if (captureRef.current) { clearInterval(captureRef.current); captureRef.current = null; }
    streamRef.current?.getTracks().forEach(t => t.stop());
    setCapturing(false); setShowCam(false); setSignSeq([]);
  };

  const grabFrame = async (): Promise<string|null> => {
    const v = videoRef.current, c = canvasRef.current;
    if (!v || !c || v.readyState < 2) return null;
    c.width = v.videoWidth||640; c.height = v.videoHeight||480;
    c.getContext('2d')!.drawImage(v,0,0,c.width,c.height);
    return c.toDataURL('image/jpeg',0.7).split(',')[1];
  };

  const recogniseOnce = async () => {
    const frame = await grabFrame();
    if (!frame) return;
    try {
      const r = await fetch(`${API_BASE}/recognition/sequence/`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ frame, sign_label:'AUTO', confidence:0.8 })
      });
      // try real recognition
      const r2 = await fetch(`${API_BASE}/recognition/recognize/`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ frame })
      });
      const d = await r2.json();
      if (d.sign_label && d.confidence_score >= 0.60) {
        setSignSeq(p => [...p, d.sign_label]);
      }
    } catch {}
  };

  const toggleCapture = () => {
    if (captureRef.current) { clearInterval(captureRef.current); captureRef.current=null; setCapturing(false); }
    else { recogniseOnce(); captureRef.current = window.setInterval(recogniseOnce, 1200); setCapturing(true); }
  };

  const sendISL = async () => {
    if (signSeq.length === 0) return;
    const text = signSeq.join(' ').toLowerCase();
    send(`🤟 ${text}`, true);
    stopCam();
  };

  if (screen === 'join') return (
    <div className="join-screen">
      <div className="join-card">
        <h1>🤟 ISL Chat</h1>
        <p>Indian Sign Language Chat — no login needed</p>
        <form onSubmit={handleJoin}>
          <input autoFocus placeholder="Enter your name" value={username}
            onChange={e => setUsername(e.target.value)} required maxLength={30}/>
          <button type="submit">Join Chat →</button>
        </form>
        <p className="hint">Share this page with a friend to chat together</p>
      </div>
    </div>
  );

  return (
    <div className="chat-app">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">🤟 ISL Chat</div>
        <div className="sidebar-you">You: <strong>{username}</strong></div>
        <div className="sidebar-section">Online ({onlineUsers.length})</div>
        {onlineUsers.map(u => (
          <div key={u} className={`sidebar-user ${u===username?'me':''}`}>
            <span className="dot"/>  {u}
          </div>
        ))}
        <div className="sidebar-room">Room: #{room}</div>
        <div className={`ws-badge ${wsReady?'ws-on':'ws-off'}`}>{wsReady?'● Live':'○ Connecting'}</div>
      </div>

      {/* Main */}
      <div className="chat-main">
        <div className="messages">
          {messages.map((m,i) => {
            const mine = m.sender === username;
            const bot  = m.is_bot;
            return (
              <div key={m.id||i} className={`msg-row ${mine?'mine':bot?'bot-row':''}`}>
                {!mine && <div className="msg-sender">{m.sender}</div>}
                <div className={`bubble ${mine?'bubble-mine':bot?'bubble-bot':'bubble-theirs'}`}>
                  <span>{m.text}</span>
                  <div className="msg-meta">
                    <span className="msg-time">{new Date(m.timestamp).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}</span>
                    <button className="voice-btn" title="Play voice" onClick={() => speak(m.text.replace(/^🤟\s*/,''))}>🔊</button>
                  </div>
                </div>
              </div>
            );
          })}
          {typingUsers.length > 0 && (
            <div className="typing">{typingUsers.join(', ')} typing<span className="dots">...</span></div>
          )}
          <div ref={bottomRef}/>
        </div>

        {/* ISL Camera Modal */}
        {showCam && (
          <div className="cam-overlay">
            <div className="cam-modal">
              <div className="cam-header">
                <span>🤟 Sign Language Input</span>
                <button onClick={stopCam}>✕</button>
              </div>
              <video ref={videoRef} autoPlay playsInline muted className="cam-video"/>
              <canvas ref={canvasRef} style={{display:'none'}}/>
              <div className="cam-signs">
                {signSeq.length===0 ? <span className="cam-hint">Press Start and sign</span>
                  : signSeq.map((s,i) => <span key={i} className="chip">{s.replace(/_/g,' ')}</span>)}
              </div>
              <div className="cam-actions">
                <button className={`cam-btn ${capturing?'cam-active':''}`} onClick={toggleCapture}>
                  {capturing?'● Signing...':'▶ Start Signing'}
                </button>
                <button className="cam-btn cam-send" onClick={sendISL} disabled={signSeq.length===0}>
                  Send 🤟
                </button>
                <button className="cam-btn cam-clear" onClick={() => setSignSeq([])}>Clear</button>
              </div>
            </div>
          </div>
        )}

        {/* Input */}
        <form className="input-bar" onSubmit={handleSend}>
          <button type="button" className="cam-trigger" onClick={startCam} title="Sign Language">🤟</button>
          <input value={input} onChange={e=>{setInput(e.target.value);handleTyping();}}
            placeholder="Type a message or click 🤟 to sign..."/>
          <button type="submit" disabled={!input.trim()}>Send ➤</button>
        </form>
      </div>
    </div>
  );
}
