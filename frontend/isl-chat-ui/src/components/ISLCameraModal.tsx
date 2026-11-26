import { useState, useEffect, useRef, useCallback } from 'react';
import { recognizeSign, addSignToSequence, flushSignSequence, islChat } from '../services/api';
import { Camera, X, Send, Trash2, Sparkles } from 'lucide-react';
import '../styles/ISLCameraModal.css';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onTextReady: (text: string, botResponse?: string) => void;
}

const INTERVAL_MS = 1200;

export default function ISLCameraModal({ isOpen, onClose, onTextReady }: Props) {
  const videoRef    = useRef<HTMLVideoElement>(null);
  const canvasRef   = useRef<HTMLCanvasElement>(null);
  const streamRef   = useRef<MediaStream | null>(null);
  const timerRef    = useRef<number | null>(null);

  const [ready, setReady]           = useState(false);
  const [capturing, setCapturing]   = useState(false);
  const [currentSign, setSign]      = useState('');
  const [confidence, setConf]       = useState(0);
  const [sequence, setSequence]     = useState<string[]>([]);
  const [sentence, setSentence]     = useState('');
  const [thinking, setThinking]     = useState(false);
  const [camError, setCamError]     = useState('');

  useEffect(() => {
    if (isOpen) { startCam(); }
    return stopCam;
  }, [isOpen]);

  const startCam = async () => {
    setCamError('');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width:640, height:480, facingMode:'user' } });
      streamRef.current = stream;
      if (videoRef.current) { videoRef.current.srcObject = stream; await videoRef.current.play(); }
      setReady(true);
    } catch (e) { setCamError('Camera access denied. Please allow camera permissions.'); }
  };

  const stopCam = () => {
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    streamRef.current?.getTracks().forEach(t => t.stop());
    streamRef.current = null;
    setReady(false); setCapturing(false);
  };

  const grabFrame = useCallback(async (): Promise<string|null> => {
    const v = videoRef.current, c = canvasRef.current;
    if (!v || !c || v.readyState < 2) return null;
    c.width = v.videoWidth || 640; c.height = v.videoHeight || 480;
    c.getContext('2d')!.drawImage(v, 0, 0, c.width, c.height);
    return c.toDataURL('image/jpeg', 0.7).split(',')[1];
  }, []);

  const recogniseOnce = useCallback(async () => {
    const frame = await grabFrame();
    if (!frame) return;
    try {
      const res = await recognizeSign(frame);
      if (res?.sign_label && res.confidence_score >= 0.60) {
        setSign(res.sign_label); setConf(res.confidence_score);
        const seq = await addSignToSequence(res.sign_label, res.confidence_score);
        setSequence(seq.current_sequence || []);
        if (seq.sentence_text) setSentence(p => p ? p + ' ' + seq.sentence_text : seq.sentence_text);
      }
    } catch {}
  }, [grabFrame]);

  const toggleCapture = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current); timerRef.current = null; setCapturing(false);
    } else {
      recogniseOnce();
      timerRef.current = window.setInterval(recogniseOnce, INTERVAL_MS);
      setCapturing(true);
    }
  };

  const handleFlush = async () => {
    try { const r = await flushSignSequence(); if (r.sentence_text) setSentence(p => p ? p+' '+r.sentence_text : r.sentence_text); setSequence([]); } catch {}
  };

  const handleClear = () => { setSentence(''); setSequence([]); setSign(''); };

  const handleSend = async () => {
    const text = (sentence || sequence.join(' ')).trim();
    if (!text) return;
    setThinking(true);
    try {
      const r = await islChat(text, sequence);
      onTextReady(text, r.bot_response);
    } catch { onTextReady(text); }
    finally { setThinking(false); stopCam(); onClose(); }
  };

  if (!isOpen) return null;

  return (
    <div className="islcam-overlay">
      <div className="islcam-modal">
        <div className="islcam-header">
          <h3><Camera size={18}/> ISL Sign Input</h3>
          <button onClick={() => { stopCam(); onClose(); }} className="islcam-x"><X size={18}/></button>
        </div>

        <div className="islcam-video-wrap">
          <video ref={videoRef} autoPlay playsInline muted />
          <canvas ref={canvasRef} style={{display:'none'}}/>
          {currentSign && <div className="islcam-badge">🤟 {currentSign.replace(/_/g,' ')} <span>{Math.round(confidence*100)}%</span></div>}
          {!ready && !camError && <div className="islcam-overlay-msg">Starting camera…</div>}
          {camError && <div className="islcam-overlay-msg islcam-err">{camError}</div>}
          {capturing && <div className="islcam-recording-dot"/>}
        </div>

        <div className="islcam-seq">
          <span className="islcam-seq-label">Signs:</span>
          {sequence.length === 0 && !sentence
            ? <span className="islcam-hint">Press Start and sign into the camera</span>
            : sequence.map((s,i) => <span key={i} className="islcam-chip">{s.replace(/_/g,' ')}</span>)}
        </div>

        {(sentence || sequence.length > 0) && (
          <div className="islcam-sentence">
            <Sparkles size={13}/> <em>{sentence || sequence.join(' ').toLowerCase()}</em>
          </div>
        )}

        <div className="islcam-actions">
          <button className={`islcam-btn ${capturing ? 'islcam-btn-active' : 'islcam-btn-primary'}`} onClick={toggleCapture} disabled={!ready}>
            <Camera size={15}/> {capturing ? '● Signing…' : 'Start Signing'}
          </button>
          <button className="islcam-btn islcam-btn-sec" onClick={handleFlush} disabled={sequence.length===0}>
            <Sparkles size={15}/> End Sentence
          </button>
          <button className="islcam-btn islcam-btn-danger" onClick={handleClear} disabled={!sentence && sequence.length===0}>
            <Trash2 size={15}/>
          </button>
          <button className="islcam-btn islcam-btn-send" onClick={handleSend} disabled={thinking||(!sentence&&sequence.length===0)}>
            <Send size={15}/> {thinking ? 'Thinking…' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}
