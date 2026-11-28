import { useState, useEffect, useRef, useCallback } from 'react';
import './App.css';

const API = '';   // relative — Vite proxy handles it
const WS  = () => `ws://127.0.0.1:8000/ws/chat/main/`;

interface Msg { id:string; type:string; sender:string; text:string; is_isl?:boolean; is_bot?:boolean; timestamp:string; }

export default function App() {
  const [screen,   setScreen]   = useState<'join'|'chat'>('join');
  const [name,     setName]     = useState('');
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input,    setInput]    = useState('');
  const [online,   setOnline]   = useState<string[]>([]);
  const [typing,   setTyping]   = useState<string[]>([]);
  const [live,     setLive]     = useState(false);
  const [showCam,  setShowCam]  = useState(false);
  const [signs,    setSigns]    = useState<string[]>([]);
  const [capturing,setCap]      = useState(false);
  const [camErr,   setCamErr]   = useState('');

  const wsRef      = useRef<WebSocket|null>(null);
  const bottomRef  = useRef<HTMLDivElement>(null);
  const typerRef   = useRef<number|null>(null);
  const videoRef   = useRef<HTMLVideoElement>(null);
  const canvasRef  = useRef<HTMLCanvasElement>(null);
  const streamRef  = useRef<MediaStream|null>(null);
  const capRef     = useRef<number|null>(null);
  const nameRef    = useRef('');

  useEffect(() => { bottomRef.current?.scrollIntoView({behavior:'smooth'}); }, [messages]);

  /* ── WebSocket ─────────────────────────────────────────── */
  const connectWS = useCallback((username: string) => {
    nameRef.current = username;
    const sock = new WebSocket(WS() + `?user=${encodeURIComponent(username)}`);

    sock.onopen = () => {
      setLive(true);
      // announce join
      sock.send(JSON.stringify({type:'join_announce', user: username}));
      fetchOnline();
    };

    sock.onmessage = (e) => {
      const d = JSON.parse(e.data);
      if (d.type === 'history') {
        setMessages(d.messages || []);
      } else if (d.type === 'chat_message') {
        setMessages(p => [...p, d]);
      } else if (d.type === 'typing') {
        if (d.user !== username) {
          setTyping(p => d.is_typing ? [...new Set([...p,d.user])] : p.filter(u=>u!==d.user));
        }
      } else if (d.type === 'join' || d.type === 'leave') {
        setTimeout(fetchOnline, 300);
      }
    };

    sock.onclose = () => { setLive(false); setTimeout(() => connectWS(nameRef.current), 3000); };
    sock.onerror = () => sock.close();
    wsRef.current = sock;
  }, []);

  const fetchOnline = async () => {
    try { const r = await fetch(`${API}/api/chat/users/?room=main`); const d = await r.json(); setOnline(d.users||[]); } catch {}
  };

  /* ── Join ──────────────────────────────────────────────── */
  const handleJoin = async (e: React.FormEvent) => {
    e.preventDefault();
    const n = name.trim();
    if (!n) return;
    try { await fetch(`${API}/api/chat/join/`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username:n, room:'main'})}); } catch {}
    connectWS(n);
    setScreen('chat');
  };

  /* ── Send message ──────────────────────────────────────── */
  const sendMsg = (text: string, isIsl = false) => {
    if (!text.trim()) return;
    const sock = wsRef.current;
    if (sock && sock.readyState === WebSocket.OPEN) {
      sock.send(JSON.stringify({type:'chat_message', sender:name, message:text.trim(), is_isl:isIsl}));
    } else {
      // Fallback: show locally if WS not ready
      const m: Msg = {id:Date.now().toString(), type:'chat_message', sender:name, text:text.trim(), is_isl:isIsl, timestamp:new Date().toISOString()};
      setMessages(p=>[...p,m]);
    }
    setInput('');
  };

  const handleSend = (e: React.FormEvent) => { e.preventDefault(); sendMsg(input); };

  const handleTyping = () => {
    const sock = wsRef.current;
    if (sock?.readyState === WebSocket.OPEN) {
      sock.send(JSON.stringify({type:'typing', user:name, is_typing:true}));
      if (typerRef.current) clearTimeout(typerRef.current);
      typerRef.current = window.setTimeout(() => sock.send(JSON.stringify({type:'typing',user:name,is_typing:false})), 2000);
    }
  };

  /* ── Voice ─────────────────────────────────────────────── */
  const speak = async (text: string) => {
    const clean = text.replace(/^🤟\s*/,'');
    try {
      const r = await fetch(`${API}/api/llm/speak/`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text:clean})});
      const d = await r.json();
      if (d.audio_b64) {
        const bytes = Uint8Array.from(atob(d.audio_b64), c=>c.charCodeAt(0));
        new Audio(URL.createObjectURL(new Blob([bytes],{type:'audio/wav'}))).play();
        return;
      }
    } catch {}
    // Browser fallback
    const u = new SpeechSynthesisUtterance(clean);
    u.lang='en-IN'; u.rate=0.95;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
  };

  /* ── Camera ─────────────────────────────────────────────── */
  const openCam = async () => {
    setCamErr(''); setSigns([]); setShowCam(true);
    try {
      const s = await navigator.mediaDevices.getUserMedia({video:{width:640,height:480,facingMode:'user'}});
      streamRef.current = s;
      if (videoRef.current) { videoRef.current.srcObject = s; videoRef.current.play(); }
    } catch { setCamErr('Camera access denied — allow camera in browser settings'); }
  };

  const closeCam = () => {
    if (capRef.current) { clearInterval(capRef.current); capRef.current=null; }
    streamRef.current?.getTracks().forEach(t=>t.stop());
    streamRef.current=null;
    setCap(false); setShowCam(false); setSigns([]);
  };

  const grabFrame = async (): Promise<string|null> => {
    const v=videoRef.current, c=canvasRef.current;
    if (!v||!c||v.readyState<2) return null;
    c.width=v.videoWidth||640; c.height=v.videoHeight||480;
    c.getContext('2d')!.drawImage(v,0,0,c.width,c.height);
    return c.toDataURL('image/jpeg',0.75).split(',')[1];
  };

  const recogniseOnce = useCallback(async () => {
    const frame = await grabFrame();
    if (!frame) return;
    try {
      const r = await fetch(`${API}/api/recognition/recognize/`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({frame})
      });
      if (r.ok) {
        const d = await r.json();
        if (d.sign_label && d.confidence_score >= 0.55) {
          setSigns(p => { const last=p[p.length-1]; return last===d.sign_label ? p : [...p, d.sign_label]; });
        }
      }
    } catch {}
  }, []);

  const toggleCapture = () => {
    if (capRef.current) { clearInterval(capRef.current); capRef.current=null; setCap(false); }
    else { setCap(true); recogniseOnce(); capRef.current=window.setInterval(recogniseOnce, 1000); }
  };

  const sendISL = () => {
    if (signs.length===0) return;
    const text = signs.map(s=>s.replace(/_/g,' ').toLowerCase()).join(' ');
    sendMsg(`🤟 ${text}`, true);
    closeCam();
  };

  /* ── JOIN SCREEN ───────────────────────────────────────── */
  if (screen==='join') return (
    <div className="join-screen">
      <div className="join-card">
        <div className="join-logo">🤟</div>
        <h1>ISL Chat</h1>
        <p>Indian Sign Language — real-time chat</p>
        <form onSubmit={handleJoin}>
          <input autoFocus placeholder="Your name" value={name} onChange={e=>setName(e.target.value)} required maxLength={30}/>
          <button type="submit">Join Chat →</button>
        </form>
        <div className="join-hint">Open in 2 tabs with different names to chat together</div>
      </div>
    </div>
  );

  /* ── CHAT SCREEN ───────────────────────────────────────── */
  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sb-logo">🤟 ISL Chat</div>
        <div className="sb-you">You: <b>{name}</b></div>
        <div className="sb-label">Online ({online.length})</div>
        {online.map(u=>(
          <div key={u} className={`sb-user ${u===name?'sb-me':''}`}>
            <span className="sb-dot"/>  {u}
          </div>
        ))}
        <div className="sb-room">Room: #main</div>
        <div className={`sb-status ${live?'live':'offline'}`}>{live?'● Live':'○ Reconnecting…'}</div>
      </aside>

      {/* Chat */}
      <div className="chat">
        <div className="msgs">
          {messages.length===0 && (
            <div className="empty">No messages yet — say hello! 👋</div>
          )}
          {messages.map((m,i) => {
            const mine = m.sender===name;
            const bot  = m.is_bot;
            return (
              <div key={m.id||i} className={`mrow ${mine?'mmine':bot?'mbot':''}`}>
                {!mine && <div className="msender">{m.sender}{bot?' 🤖':''}</div>}
                <div className={`mbubble ${mine?'mbmine':bot?'mbbbot':'mbother'}`}>
                  <span className="mtext">{m.text}</span>
                  <div className="mmeta">
                    <span className="mtime">{new Date(m.timestamp).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}</span>
                    <button className="voicebtn" onClick={()=>speak(m.text)} title="Read aloud">🔊</button>
                  </div>
                </div>
              </div>
            );
          })}
          {typing.length>0 && <div className="typing">{typing.join(', ')} is typing…</div>}
          <div ref={bottomRef}/>
        </div>

        {/* ISL Camera Modal */}
        {showCam && (
          <div className="cam-bg" onClick={(e)=>{ if(e.target===e.currentTarget) closeCam(); }}>
            <div className="cam-box">
              <div className="cam-top">
                <span>🤟 Sign Language Input</span>
                <button onClick={closeCam}>✕</button>
              </div>
              <div className="cam-feed">
                <video ref={videoRef} autoPlay playsInline muted/>
                {capturing && <div className="cam-rec">● REC</div>}
                {camErr && <div className="cam-err">{camErr}</div>}
                {!streamRef.current && !camErr && <div className="cam-loading">Starting camera…</div>}
              </div>
              <canvas ref={canvasRef} style={{display:'none'}}/>
              <div className="cam-signs">
                {signs.length===0
                  ? <span className="cam-hint">Press Start Signing then sign in front of camera</span>
                  : signs.map((s,i)=><span key={i} className="chip">{s.replace(/_/g,' ')}</span>)
                }
              </div>
              <div className="cam-btns">
                <button className={`cbtn ${capturing?'cbtn-stop':''}`} onClick={toggleCapture}>
                  {capturing?'■ Stop':'▶ Start Signing'}
                </button>
                <button className="cbtn cbtn-clear" onClick={()=>setSigns([])} disabled={signs.length===0}>Clear</button>
                <button className="cbtn cbtn-send" onClick={sendISL} disabled={signs.length===0}>Send 🤟</button>
              </div>
            </div>
          </div>
        )}

        {/* Input */}
        <form className="ibar" onSubmit={handleSend}>
          <button type="button" className="icam" onClick={openCam} title="Sign Language Input">🤟</button>
          <input
            value={input}
            onChange={e=>{setInput(e.target.value); handleTyping();}}
            placeholder="Type a message or click 🤟 to sign…"
          />
          <button type="submit" className="isend" disabled={!input.trim()}>Send</button>
        </form>
      </div>
    </div>
  );
}
