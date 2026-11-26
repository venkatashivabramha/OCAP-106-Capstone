/**
 * useVoice — plays a message via Gemini TTS (if key set) or browser Speech API.
 */
import { useState, useCallback, useRef } from 'react';
import api from './api';

type VoiceState = 'idle' | 'loading' | 'playing';

export function useVoice() {
  const [state, setState] = useState<Record<string, VoiceState>>({});
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const speak = useCallback(async (msgId: string, text: string) => {
    // Stop any playing audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    window.speechSynthesis?.cancel();

    setState(prev => ({ ...prev, [msgId]: 'loading' }));

    try {
      const res = await api.post('/llm/speak/', { text });
      const { audio_b64, provider } = res.data;

      if (provider === 'gemini' && audio_b64) {
        // Decode base64 WAV and play
        const bytes = Uint8Array.from(atob(audio_b64), c => c.charCodeAt(0));
        const blob  = new Blob([bytes], { type: 'audio/wav' });
        const url   = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audioRef.current = audio;
        setState(prev => ({ ...prev, [msgId]: 'playing' }));
        audio.onended = () => {
          setState(prev => ({ ...prev, [msgId]: 'idle' }));
          URL.revokeObjectURL(url);
        };
        await audio.play();
      } else {
        // Browser Web Speech API fallback
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang  = 'en-IN';
        utterance.rate  = 0.95;
        utterance.pitch = 1.0;
        utterance.onend = () => setState(prev => ({ ...prev, [msgId]: 'idle' }));
        setState(prev => ({ ...prev, [msgId]: 'playing' }));
        window.speechSynthesis.speak(utterance);
      }
    } catch (err) {
      console.error('TTS error, falling back to browser:', err);
      // Guaranteed fallback
      try {
        const utter = new SpeechSynthesisUtterance(text);
        utter.lang = 'en-IN';
        utter.onend = () => setState(prev => ({ ...prev, [msgId]: 'idle' }));
        setState(prev => ({ ...prev, [msgId]: 'playing' }));
        window.speechSynthesis.speak(utter);
      } catch {
        setState(prev => ({ ...prev, [msgId]: 'idle' }));
      }
    }
  }, []);

  const stop = useCallback((msgId: string) => {
    audioRef.current?.pause();
    audioRef.current = null;
    window.speechSynthesis?.cancel();
    setState(prev => ({ ...prev, [msgId]: 'idle' }));
  }, []);

  const getState = (msgId: string): VoiceState => state[msgId] || 'idle';

  return { speak, stop, getState };
}
