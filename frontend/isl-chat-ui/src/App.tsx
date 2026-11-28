import { useState, useEffect, useRef, useCallback } from 'react';
import './App.css';

interface Msg { id:string; type:string; sender:string; text:string; is_isl?:boolean; is_bot?:boolean; timestamp:string; }

export default function App() {
  const [screen,  setScreen]  = useState<'join'|'chat'>('join');
  const [nameVal, setNameVal] = useState('');
  const [msgs,    setMsgs]    = useState<Msg[]>([]);
  const [input,   setInput]   = useState('');
  const [online,  setOnline]  = useState<string[]>([]);
  const [typing,  setTyping]  = useState<string[]>([]);
  const [live,    setLive]    = useState(false);
  const [showCam, setShowCam] = useState(false);
  const [signs,   setSigns]   = useState<string[]>([]);
  const [cap,     setCap]     = useState(false);
  const [camErr,  setCamErr]  = useState('');

  // Refs - never go stale
  const nameRef   = useRef('');
  const wsRef     = useRef<WebSocket|null>(null);
  const pollRef   = useRef<number|null>(null);
  const countRef  = useRef(0);
  const typerRef  = useRef<number|null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const videoRef  = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream|null>(null);
  const capRef    = useRef<number|null>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({behavior:'smooth'}); }, [msgs]);

  // ── Fetch online users ──────────────────────────────────
  const fetchUsers = useCallback(async () => {
    try { const r=await fetch('/api/chat/users/?room=main'); const d=await r.json(); setOnline(d.users||[]); } catch {}
  },[]);

  // ── Poll messages (HTTP fallback) ───────────────────────
  const poll = useCallback(async () => {
    // Always poll — works as backup even when WS is live
    try {
      const r = await fetch(`/api/chat/messages/?room=main&since=${countRef.current}`);
      const d = await r.json();
      const newMsgs: Msg[] = (d.messages||[]).filter((m:Msg) => m);
      if (newMsgs.length > 0) {
        setMsgs(p => {
          const existing = new Set(p.map(m=>m.id));
          const fresh = newMsgs.filter(m=>!existing.has(m.id));
          if (fresh.length === 0) return p;
          countRef.current = d.total;
          return [...p, ...fresh];
        });
      }
    } catch {}
  },[]);

  // ── WebSocket ───────────────────────────────────────────
  const connectWS = useCallback((uname: string) => {
    const url = `ws://127.0.0.1:8000/ws/chat/main/?user=${encodeURIComponent(uname)}`;
    const ws  = new WebSocket(url);

    ws.onopen = () => {
      setLive(true);
      fetchUsers();
    };

    ws.onmessage = (e) => {
      const d = JSON.parse(e.data);
      if (d.type === 'history') {
        setMsgs(d.messages||[]);
        countRef.current = (d.messages||[]).length;
      } else if (d.type === 'chat_message') {
        setMsgs(p => {
          if (p.some(m=>m.id===d.id)) return p;
          countRef.current++;
          return [...p, d];
        });
      } else if (d.type === 'typing') {
        if (d.user !== uname) setTyping(p => d.is_typing ? [...new Set([...p,d.user])] : p.filter(u=>u!==d.user));
      } else if (d.type==='join'||d.type==='leave') {
        setTimeout(fetchUsers, 400);
      }
    };

    ws.onclose = () => { setLive(false); setTimeout(() => connectWS(nameRef.current), 3000); };
    ws.onerror = () => ws.close();
    wsRef.current = ws;
  },[fetchUsers]);

  // ── Join ────────────────────────────────────────────────
  const handleJoin = async (e: React.FormEvent) => {
    e.preventDefault();
    const n = nameVal.trim();
    if (!n) return;
    nameRef.current = n;
    // Register user via HTTP
    try { await fetch('/api/chat/join/', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:n,room:'main'})}); } catch {}
    connectWS(n);
    setScreen('chat');
    // Start HTTP polling as fallback (also de-dupes WS messages)
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = window.setInterval(poll, 1500);
  };

  // ── Send ────────────────────────────────────────────────
  const sendMsg = async (text: string, isIsl = false) => {
    const t = text.trim();
    if (!t) return;
    const uname = nameRef.current;

    // Optimistic UI — show immediately
    const optMsg: Msg = { id: `opt-${Date.now()}`, type:'chat_message', sender:uname, text:t, is_isl:isIsl, timestamp:new Date().toISOString() };
    setMsgs(p => [...p, optMsg]);
    setInput('');

    // Try WebSocket first (real-time delivery to others)
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({type:'chat_message', sender:uname, message:t, is_isl:isIsl}));
    }

    // Always persist via HTTP (ensures other users see it via polling)
    try {
      const r = await fetch('/api/chat/send/', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({username:uname, room:'main', text:t, is_isl:isIsl})
      });
      if (r.ok) {
        const d = await r.json();
        // Replace optimistic message with real one
        if (d.message) {
          setMsgs(p => p.map(m => m.id===optMsg.id ? {...d.message, sender:uname} : m));
        }
      }
    } catch {}
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const t = input.trim();
    if (!t) return;
    sendMsg(t);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const t = input.trim();
      if (t) sendMsg(t);
    }
  };
  const handleType = () => {
    const ws = wsRef.current;
    if (ws?.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({type:'typing',user:nameRef.current,is_typing:true}));
    if (typerRef.current) clearTimeout(typerRef.current);
    typerRef.current = window.setTimeout(() => ws.send(JSON.stringify({type:'typing',user:nameRef.current,is_typing:false})),2000);
  };

  // ── Voice ───────────────────────────────────────────────
  const speak = async (text: string) => {
    const clean = text.replace(/^🤟\s*/,'');
    try {
      const r = await fetch('/api/llm/speak/', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:clean})});
      const d = await r.json();
      if (d.audio_b64) {
        const bytes = Uint8Array.from(atob(d.audio_b64),c=>c.charCodeAt(0));
        new Audio(URL.createObjectURL(new Blob([bytes],{type:'audio/wav'}))).play();
        return;
      }
    } catch {}
    const u = new SpeechSynthesisUtterance(clean);
    u.lang='en-IN'; u.rate=0.95;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
  };

  // ── Camera ──────────────────────────────────────────────
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
    streamRef.current?.getTracks().forEach(t=>t.stop()); streamRef.current=null;
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
      const r = await fetch('/api/recognition/recognize/', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({frame})});
      if (r.ok) {
        const d = await r.json();
        if (d.sign_label && d.confidence_score >= 0.55) {
          setSigns(p => { const last=p[p.length-1]; return last===d.sign_label?p:[...p,d.sign_label]; });
        }
      }
    } catch {}
  },[]);

  const toggleCap = () => {
    if (capRef.current) { clearInterval(capRef.current); capRef.current=null; setCap(false); }
    else { setCap(true); recogniseOnce(); capRef.current=window.setInterval(recogniseOnce,1000); }
  };

  const sendISL = () => {
    if (!signs.length) return;
    sendMsg(`🤟 ${signs.map(s=>s.replace(/_/g,' ').toLowerCase()).join(' ')}`, true);
    closeCam();
  };

  // ═══════════════════════════════════════════════════════
  //  JOIN SCREEN
  // ═══════════════════════════════════════════════════════
  if (screen==='join') return (
    <div className="join-screen">
      <div className="join-card">
        <div className="join-logo">🤟</div>
        <h1>ISL Chat</h1>
        <p>Indian Sign Language — real-time chat</p>
        <form onSubmit={handleJoin}>
          <input autoFocus placeholder="Your name (e.g. Alice)" value={nameVal}
            onChange={e=>setNameVal(e.target.value)} required maxLength={30}/>
          <button type="submit">Join Chat →</button>
        </form>
        <div className="join-hint">Open in 2 browser tabs with different names to chat</div>
      </div>
    </div>
  );

  // ═══════════════════════════════════════════════════════
  //  CHAT SCREEN
  // ═══════════════════════════════════════════════════════
  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sb-logo">🤟 ISL Chat</div>
        <div className="sb-you">You: <b>{nameRef.current}</b></div>
        <div className="sb-label">Online ({online.length})</div>
        {online.map(u=>(
          <div key={u} className={`sb-user ${u===nameRef.current?'sb-me':''}`}>
            <span className="sb-dot"/>  {u}
          </div>
        ))}
        <div className="sb-room">Room: #main</div>
        <div className={`sb-status ${live?'live':'offline'}`}>
          {live ? '● Live (WebSocket)' : '○ Polling mode'}
        </div>
      </aside>

      {/* Chat area */}
      <div className="chat">
        <div className="msgs">
          {msgs.length===0 && <div className="empty">No messages yet — say hello! 👋</div>}
          {msgs.map((m,i) => {
            const mine = m.sender===nameRef.current;
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

        {/* ISL Camera */}
        {showCam && (
          <div className="cam-bg" onClick={e=>{ if(e.target===e.currentTarget) closeCam(); }}>
            <div className="cam-box">
              <div className="cam-top"><span>🤟 Sign Language Input</span><button onClick={closeCam}>✕</button></div>
              <div className="cam-feed">
                <video ref={videoRef} autoPlay playsInline muted/>
                {cap && <div className="cam-rec">● REC</div>}
                {camErr && <div className="cam-err">{camErr}</div>}
                {!streamRef.current && !camErr && <div className="cam-loading">Starting camera…</div>}
              </div>
              <canvas ref={canvasRef} style={{display:'none'}}/>
              <div className="cam-signs">
                {signs.length===0
                  ? <span className="cam-hint">Press ▶ Start Signing then sign in front of the camera</span>
                  : signs.map((s,i)=><span key={i} className="chip">{s.replace(/_/g,' ')}</span>)
                }
              </div>
              <div className="cam-btns">
                <button className={`cbtn ${cap?'cbtn-stop':''}`} onClick={toggleCap}>{cap?'■ Stop':'▶ Start Signing'}</button>
                <button className="cbtn cbtn-clear" onClick={()=>setSigns([])} disabled={!signs.length}>Clear</button>
                <button className="cbtn cbtn-send" onClick={sendISL} disabled={!signs.length}>Send 🤟</button>
              </div>
            </div>
          </div>
        )}

        {/* Input bar */}
        <form className="ibar" onSubmit={handleSend}>
          <button type="button" className="icam" onClick={openCam} title="Sign Language">🤟</button>
          <input
            value={input}
            onChange={e=>{setInput(e.target.value); handleType();}}
            onKeyDown={handleKeyDown}
            placeholder="Type a message or press Enter to send…"
            autoComplete="off"
          />
          <button type="submit" className="isend" onClick={()=>{ if(input.trim()) sendMsg(input); }}>
            Send ➤
          </button>
        </form>
      </div>
    </div>
  );
}
