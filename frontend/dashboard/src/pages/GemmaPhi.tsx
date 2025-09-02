import React, { useCallback, useEffect, useRef, useState } from 'react';

type ChatMessage = {
  role: 'user' | 'agent';
  text: string;
  backend?: string | null;
  agentId?: string; // A or B for dual comparison
  latencyMs?: number | null;
  errors?: string[];
  timings?: Record<string, number>;
};

const BACKENDS = ['auto', 'edge', 'ollama', 'leonardo', 'jarvis', 'mistral', 'phi3', 'llama'];
const VOICES = ['amy', 'jarvis', 'leonardo', 'alan', 'southern_male'];

const GemmaPhi: React.FC = () => {
  // Core chat state
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loadingA, setLoadingA] = useState(false);
  const [loadingB, setLoadingB] = useState(false);
  // Simple backend health indicator (periodic ping to /health or /metrics/basic)
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null);
  const lastHealthCheckRef = useRef<number>(0);

  // Agent (backend) preferences
  const [backendA, setBackendA] = useState('auto');
  const [backendB, setBackendB] = useState('edge');
  const [dualMode, setDualMode] = useState(true);
  const [persona, setPersona] = useState<string | undefined>('neutral');

  // TTS config
  const [voice, setVoice] = useState('amy');
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(1);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Speech to text (whisper.cpp)
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunksRef = useRef<Blob[]>([]);

  // NEW: UI toggles for family-friendly mode
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showTimings, setShowTimings] = useState(false);
  const [simpleMode, setSimpleMode] = useState(true);
  const [showDualAgents, setShowDualAgents] = useState(false);
  const [devMode, setDevMode] = useState(false);

  const chatHistoryRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [messages]);

  const appendMessage = useCallback((m: ChatMessage) => {
    try {
      if (m.role === 'agent') {
        // Dev console insight: agent reply metadata
        // eslint-disable-next-line no-console
        console.log('[chat][agent]', m.agentId, {
          backend: m.backend,
            latencyMs: m.latencyMs,
            errors: m.errors,
            timings: m.timings,
            textSample: m.text.slice(0, 160)
        });
      } else {
        // eslint-disable-next-line no-console
        console.log('[chat][user]', m.text);
      }
    } catch { /* ignore logging issues */ }
    setMessages(prev => [...prev, m]);
  }, []);

  async function callAgent(query: string, prefer: string, agentId: 'A' | 'B') {
    const setLoading = agentId === 'A' ? setLoadingA : setLoadingB;
    setLoading(true);
    try {
      const resp = await fetch('/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, prefer, persona_key: persona })
      });
      if (!resp.ok) {
        appendMessage({ role: 'agent', text: `Error HTTP ${resp.status}`, agentId, backend: prefer });
        return;
      }
      let data: any = {};
      try {
        const text = await resp.text();
        if (text.trim().startsWith('<!doctype') || text.trim().startsWith('<html')) {
          appendMessage({ role: 'agent', text: 'Received HTML instead of JSON (proxy misroute?)', agentId, backend: prefer });
          return;
        }
        data = text ? JSON.parse(text) : {};
      } catch (parseErr: any) {
        appendMessage({ role: 'agent', text: `Parse error: ${parseErr?.message || parseErr}`, agentId, backend: prefer });
        return;
      }
      appendMessage({
        role: 'agent',
        text: data.answer || '(no answer)',
        backend: data.answer_meta?.backend,
        agentId,
        latencyMs: data.answer_meta?.latency_ms || data.answer_meta?.latencyMs,
        errors: data.answer_meta?.errors,
        timings: data.answer_meta?.timings,
      });
    } catch (e: any) {
      appendMessage({ role: 'agent', text: `Exception: ${e?.message || e}`, agentId, backend: prefer });
    } finally {
      setLoading(false);
    }
  }

  const handleSend = useCallback(async () => {
    const q = input.trim();
    if (!q) return;
    appendMessage({ role: 'user', text: q });
    setInput('');
    if (dualMode) {
      await Promise.all([
        callAgent(q, backendA, 'A'),
        callAgent(q, backendB, 'B')
      ]);
    } else {
      await callAgent(q, backendA, 'A');
    }
  }, [input, dualMode, backendA, backendB, appendMessage, persona]);

  // Health check effect (lightweight, debounced)
  useEffect(() => {
    const now = Date.now();
    if (now - lastHealthCheckRef.current < 15000) return; // 15s debounce
    lastHealthCheckRef.current = now;
    let aborted = false;
    (async () => {
      try {
        const res = await fetch('/metrics/basic', { cache: 'no-store' });
        if (!aborted) setBackendHealthy(res.ok);
      } catch {
        if (!aborted) setBackendHealthy(false);
      }
    })();
    return () => { aborted = true; };
  }, [messages.length]);

  // Log health transitions to dev console
  const prevHealthRef = useRef<boolean | null>(null);
  useEffect(() => {
    if (backendHealthy !== prevHealthRef.current) {
      // eslint-disable-next-line no-console
      console.log('[chat][health]', backendHealthy === null ? 'unknown' : backendHealthy ? 'up' : 'down');
      prevHealthRef.current = backendHealthy;
    }
  }, [backendHealthy]);

  // Expose messages for ad-hoc inspection in DevTools (window.__chatMessages)
  useEffect(() => {
    (window as any).__chatMessages = messages;
  }, [messages]);

  const handleKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  async function speak(text: string, sourceBackend?: string) {
    if (isMuted || !text) return;
    try {
      // Use Leonardo's specialized TTS if message came from Leonardo
      if (sourceBackend === 'leonardo' || voice === 'leonardo') {
        const resp = await fetch('/leonardo/speak', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            text, 
            voice: 'leonardo', 
            format: 'base64',
            emotion: 'analytical'
          })
        });
        const data = await resp.json();
        const b64 = data.audio_base64;
        if (b64) {
          const audio = new Audio('data:audio/wav;base64,' + b64);
          audio.volume = volume;
          audioRef.current = audio;
          audio.play();
          return;
        }
      }
      
      // Fallback to regular TTS
      const resp = await fetch('/audio/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, voice, format: 'base64' })
      });
      const data = await resp.json();
      const b64 = data.audio_base64 || data.audio_b64;
      if (!b64) return;
      const audio = new Audio('data:audio/wav;base64,' + b64);
      audio.volume = volume;
      audioRef.current = audio;
      audio.play();
    } catch (e) {
      console.warn('TTS error', e);
    }
  }

  const handlePlayLast = () => {
    // Find last agent message
    for (let i = messages.length - 1; i >= 0; i--) {
      const m = messages[i];
      if (m.role === 'agent') { 
        speak(m.text, m.backend || undefined); 
        break; 
      }
    }
  };

  const handleMuteToggle = () => setIsMuted(m => !m);
  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => setVolume(parseFloat(e.target.value));

  // Speech-to-text via whisper.cpp
  const startRecording = async () => {
    if (recording) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      recordedChunksRef.current = [];
      mr.ondataavailable = ev => { if (ev.data.size > 0) recordedChunksRef.current.push(ev.data); };
      mr.onstop = async () => {
        const blob = new Blob(recordedChunksRef.current, { type: 'audio/webm' });
        const fd = new FormData();
        fd.append('file', blob, 'recording.webm');
        try {
          const resp = await fetch('/audio/transcribe', { method: 'POST', body: fd });
          if (resp.ok) {
            const data = await resp.json();
            setInput(prev => (prev ? prev + ' ' : '') + (data.transcript || ''));
          } else {
            console.warn('Transcribe HTTP', resp.status);
          }
        } catch (e) {
          console.warn('Transcribe error', e);
        }
      };
      mr.start();
      mediaRecorderRef.current = mr;
      setRecording(true);
    } catch (e) {
      console.warn('Mic error', e);
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    mediaRecorderRef.current = null;
    setRecording(false);
  };

  return (
    <div style={{ 
      padding: 20, 
      fontFamily: 'sans-serif', 
      maxWidth: 1200, 
      margin: '0 auto',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #5e2750 0%, #772953 25%, #8f4e5a 50%, #a67761 75%, #bd9f68 100%)',
      color: '#f8f8f2'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 15 }}>
        <h1 style={{ margin: 0, fontSize: '1.8em', color: '#ffffff', textShadow: '0 2px 4px rgba(0,0,0,0.3)' }}>
          🤖 Multi-GPU AI Assistant
        </h1>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <button 
            onClick={() => setSimpleMode(!simpleMode)} 
            style={{ 
              padding: '8px 16px', 
              background: simpleMode ? '#e95420' : 'rgba(255,255,255,0.2)', 
              color: 'white', 
              border: '1px solid rgba(255,255,255,0.3)', 
              borderRadius: 8,
              cursor: 'pointer',
              fontSize: 14,
              boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
            }}
          >
            {simpleMode ? '👥 Family Mode' : '⚙️ Power Mode'}
          </button>
          {!simpleMode && (
            <>
              <button 
                onClick={() => setDevMode(!devMode)} 
                style={{ 
                  padding: '8px 16px', 
                  background: devMode ? '#e95420' : 'rgba(255,255,255,0.2)', 
                  color: 'white', 
                  border: '1px solid rgba(255,255,255,0.3)', 
                  borderRadius: 8,
                  cursor: 'pointer',
                  fontSize: 14,
                  boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                }}
              >
                {devMode ? '🔧 Dev Mode' : '👤 User Mode'}
              </button>
              <button 
                onClick={() => setShowTimings(!showTimings)} 
                style={{ 
                  padding: '8px 16px', 
                  background: showTimings ? '#e95420' : 'rgba(255,255,255,0.2)', 
                  color: 'white', 
                  border: '1px solid rgba(255,255,255,0.3)', 
                  borderRadius: 8,
                  cursor: 'pointer',
                  fontSize: 14,
                  boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                }}
              >
                {showTimings ? '🔍 Hide Details' : '📊 Show Details'}
              </button>
            </>
          )}
        </div>
      </div>

      {/* Advanced controls - only show when not in simple mode */}
      {!simpleMode && (
        <div style={{ 
          marginBottom: 20, 
          padding: 15, 
          background: 'rgba(255,255,255,0.1)', 
          borderRadius: 12, 
          border: '1px solid rgba(255,255,255,0.2)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
        }}>
          <div style={{ display: 'flex', gap: 20, alignItems: 'center', flexWrap: 'wrap', fontSize: 14 }}>
            {devMode && (
              <>
                <label style={{ display: 'flex', alignItems: 'center', gap: 5, color: '#f8f8f2' }}>
                  <input 
                    type="checkbox" 
                    checked={dualMode} 
                    onChange={e => setDualMode(e.target.checked)} 
                    style={{ accentColor: '#e95420' }}
                  />
                  Dual Mode (compare responses)
                </label>
                <label style={{ color: '#f8f8f2' }}>Agent A Backend:
                  <select 
                    value={backendA} 
                    onChange={e => setBackendA(e.target.value)} 
                    style={{ 
                      marginLeft: 6, 
                      padding: 6, 
                      borderRadius: 4, 
                      border: '1px solid rgba(255,255,255,0.3)',
                      background: 'rgba(255,255,255,0.1)',
                      color: '#f8f8f2'
                    }}
                  >
                    {BACKENDS.map(b => <option key={b} style={{ background: '#5e2750', color: '#f8f8f2' }}>{b}</option>)}
                  </select>
                </label>
                <label style={{ color: '#f8f8f2' }}>Agent B Backend:
                  <select 
                    value={backendB} 
                    onChange={e => setBackendB(e.target.value)} 
                    disabled={!dualMode} 
                    style={{ 
                      marginLeft: 6, 
                      padding: 6, 
                      borderRadius: 4, 
                      border: '1px solid rgba(255,255,255,0.3)',
                      background: 'rgba(255,255,255,0.1)',
                      color: '#f8f8f2'
                    }}
                  >
                    {BACKENDS.map(b => <option key={b} style={{ background: '#5e2750', color: '#f8f8f2' }}>{b}</option>)}
                  </select>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: 5, color: '#f8f8f2' }}>
                  <input 
                    type="checkbox" 
                    checked={showDualAgents} 
                    onChange={e => setShowDualAgents(e.target.checked)} 
                    style={{ accentColor: '#e95420' }}
                  />
                  Show Agent A/B Labels
                </label>
              </>
            )}
            <span style={{ 
              fontSize: 12, 
              padding: '4px 8px', 
              borderRadius: 6, 
              background: backendHealthy==null? 'rgba(255,255,255,0.2)' : backendHealthy ? '#4CAF50' : '#f44336', 
              color:'#fff',
              boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
            }}>
              {backendHealthy==null? 'health: …' : backendHealthy ? 'backend: up' : 'backend: down'}
            </span>
            <label style={{ color: '#f8f8f2' }}>Persona:
              <select 
                value={persona} 
                onChange={e => setPersona(e.target.value)} 
                style={{ 
                  marginLeft: 6, 
                  padding: 6, 
                  borderRadius: 4, 
                  border: '1px solid rgba(255,255,255,0.3)',
                  background: 'rgba(255,255,255,0.1)',
                  color: '#f8f8f2'
                }}
              >
                <option value="neutral" style={{ background: '#5e2750', color: '#f8f8f2' }}>neutral</option>
                <option value="british_butler" style={{ background: '#5e2750', color: '#f8f8f2' }}>british_butler</option>
                <option value="fun_supportive" style={{ background: '#5e2750', color: '#f8f8f2' }}>fun_supportive</option>
                <option value="terse_expert" style={{ background: '#5e2750', color: '#f8f8f2' }}>terse_expert</option>
              </select>
            </label>
            <label style={{ color: '#f8f8f2' }}>Voice:
              <select 
                value={voice} 
                onChange={e => setVoice(e.target.value)} 
                style={{ 
                  marginLeft: 6, 
                  padding: 6, 
                  borderRadius: 4, 
                  border: '1px solid rgba(255,255,255,0.3)',
                  background: 'rgba(255,255,255,0.1)',
                  color: '#f8f8f2'
                }}
              >
                {VOICES.map(v => <option key={v} style={{ background: '#5e2750', color: '#f8f8f2' }}>{v}</option>)}
              </select>
            </label>
            <button 
              onClick={handlePlayLast} 
              disabled={isMuted} 
              style={{ 
                padding: '8px 12px', 
                background: isMuted ? 'rgba(255,255,255,0.2)' : '#4CAF50', 
                color: 'white', 
                border: '1px solid rgba(255,255,255,0.3)', 
                borderRadius: 6,
                cursor: isMuted ? 'not-allowed' : 'pointer',
                boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
              }}
            >
              🔊 Play Last
            </button>
            <button 
              onClick={handleMuteToggle} 
              style={{ 
                padding: '8px 12px', 
                background: isMuted ? '#f44336' : 'rgba(255,255,255,0.2)', 
                color: 'white', 
                border: '1px solid rgba(255,255,255,0.3)', 
                borderRadius: 6,
                cursor: 'pointer',
                boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
              }}
            >
              {isMuted ? '🔇 Unmute' : '🔊 Mute'}
            </button>
            <input 
              type="range" 
              min={0} 
              max={1} 
              step={0.01} 
              value={volume} 
              onChange={handleVolumeChange} 
              style={{ width: 80, accentColor: '#e95420' }} 
            />
            {recording ? (
              <button 
                onClick={stopRecording} 
                style={{ 
                  padding: '8px 12px', 
                  background: '#f44336', 
                  color: 'white', 
                  border: '1px solid rgba(255,255,255,0.3)', 
                  borderRadius: 6,
                  cursor: 'pointer',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                }}
              >
                ⏹️ Stop Recording
              </button>
            ) : (
              <button 
                onClick={startRecording} 
                style={{ 
                  padding: '8px 12px', 
                  background: '#FF9800', 
                  color: 'white', 
                  border: '1px solid rgba(255,255,255,0.3)', 
                  borderRadius: 6,
                  cursor: 'pointer',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                }}
              >
                🎤 Record Voice
              </button>
            )}
          </div>
        </div>
      )}

      {/* Chat interface */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div style={{ display: 'flex', gap: 12 }}>
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Type your message and press Enter..."
            style={{ 
              flex: 1, 
              padding: 15, 
              fontSize: 16, 
              border: '2px solid rgba(255,255,255,0.3)', 
              borderRadius: 12,
              outline: 'none',
              transition: 'all 0.3s ease',
              background: 'rgba(255,255,255,0.1)',
              color: '#f8f8f2',
              backdropFilter: 'blur(10px)',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
            }}
            onFocus={e => {
              e.target.style.borderColor = '#e95420';
              e.target.style.boxShadow = '0 0 0 3px rgba(233, 84, 32, 0.2)';
            }}
            onBlur={e => {
              e.target.style.borderColor = 'rgba(255,255,255,0.3)';
              e.target.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
            }}
          />
          <button 
            onClick={handleSend} 
            disabled={loadingA || loadingB || !input.trim()}
            style={{ 
              padding: '15px 30px', 
              fontSize: 16, 
              background: (loadingA || loadingB || !input.trim()) ? 'rgba(255,255,255,0.2)' : 'linear-gradient(135deg, #e95420, #ff6b35)', 
              color: 'white', 
              border: '1px solid rgba(255,255,255,0.3)', 
              borderRadius: 12,
              cursor: (loadingA || loadingB || !input.trim()) ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              minWidth: 120,
              boxShadow: '0 4px 6px rgba(0,0,0,0.2)',
              fontWeight: 'bold'
            }}
            onMouseEnter={e => {
              if (!e.currentTarget.disabled) {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 12px rgba(0,0,0,0.3)';
              }
            }}
            onMouseLeave={e => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.2)';
            }}
          >
            {(loadingA || loadingB) ? '⏳ Sending...' : '📤 Send'}
          </button>
        </div>
        
        <div 
          ref={chatHistoryRef} 
          style={{ 
            height: simpleMode ? 500 : 420, 
            border: '2px solid rgba(255,255,255,0.3)', 
            borderRadius: 16,
            padding: 20, 
            overflowY: 'auto', 
            background: 'rgba(255,255,255,0.05)',
            backdropFilter: 'blur(10px)',
            boxShadow: 'inset 0 2px 8px rgba(0,0,0,0.2), 0 4px 12px rgba(0,0,0,0.1)'
          }}
        >
          {messages.length === 0 && (
            <div style={{ 
              textAlign: 'center', 
              color: 'rgba(248,248,242,0.8)', 
              fontSize: 18, 
              marginTop: 50,
              padding: 20,
              background: 'rgba(255,255,255,0.1)',
              borderRadius: 12,
              backdropFilter: 'blur(5px)'
            }}>
              👋 Welcome to your AI Assistant! <br/>
              <span style={{ fontSize: 16, opacity: 0.8 }}>
                {simpleMode ? 'Ask me anything - I\'m here to help!' : 'Start a conversation by typing a message above.'}
              </span>
            </div>
          )}
          {messages.map((m, idx) => (
            <div key={idx} style={{ 
              marginBottom: 20, 
              padding: 18, 
              background: m.role === 'user' 
                ? 'linear-gradient(135deg, rgba(233, 84, 32, 0.2), rgba(255, 107, 53, 0.2))' 
                : 'linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(139, 195, 74, 0.2))', 
              borderRadius: 16,
              border: `2px solid ${m.role === 'user' ? 'rgba(233, 84, 32, 0.3)' : 'rgba(76, 175, 80, 0.3)'}`,
              backdropFilter: 'blur(10px)',
              boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
              transition: 'transform 0.2s ease',
              cursor: 'default'
            }}
            onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'}
            onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <strong style={{ 
                  color: m.role === 'user' ? '#ff6b35' : '#81C784', 
                  fontSize: 16,
                  textShadow: '0 1px 2px rgba(0,0,0,0.3)'
                }}>
                  {m.role === 'user' ? '👤 You' : `🤖 AI Assistant${(devMode && showDualAgents && m.agentId) ? ` ${m.agentId}` : ''}`}
                </strong>
                {(!simpleMode || devMode) && (
                  <div style={{ fontSize: 12, opacity: 0.8, display: 'flex', gap: 10, alignItems: 'center' }}>
                    {m.backend && (
                      <span style={{ 
                        padding: '3px 8px', 
                        background: 'rgba(255,255,255,0.2)', 
                        borderRadius: 6,
                        border: '1px solid rgba(255,255,255,0.3)',
                        color: '#f8f8f2'
                      }}>
                        {m.backend}
                      </span>
                    )}
                    {m.latencyMs != null && (
                      <span style={{ 
                        color: m.latencyMs > 2000 ? '#ff6b6b' : '#4ecdc4',
                        fontWeight: 'bold',
                        textShadow: '0 1px 2px rgba(0,0,0,0.5)'
                      }}>
                        ⏱️ {m.latencyMs.toFixed(0)}ms
                      </span>
                    )}
                    {m.errors && m.errors.length > 0 && (
                      <span style={{ 
                        color: '#ff6b6b',
                        fontWeight: 'bold',
                        textShadow: '0 1px 2px rgba(0,0,0,0.5)'
                      }}>
                        ⚠️ {m.errors.length} errors
                      </span>
                    )}
                  </div>
                )}
              </div>
              <div style={{ 
                fontSize: 16, 
                lineHeight: 1.7, 
                color: '#f8f8f2',
                textShadow: '0 1px 2px rgba(0,0,0,0.3)'
              }}>
                {m.text}
              </div>
              {(!simpleMode || devMode) && showTimings && m.timings && (
                <details style={{ marginTop: 15 }}>
                  <summary style={{ 
                    cursor: 'pointer', 
                    fontSize: 12, 
                    color: 'rgba(248,248,242,0.8)', 
                    padding: 8,
                    background: 'rgba(255,255,255,0.1)',
                    borderRadius: 6,
                    border: '1px solid rgba(255,255,255,0.2)'
                  }}>
                    📊 Performance Details
                  </summary>
                  <pre style={{ 
                    fontSize: 11, 
                    background: 'rgba(0,0,0,0.3)', 
                    padding: 12, 
                    borderRadius: 8, 
                    marginTop: 10, 
                    overflow: 'auto',
                    border: '1px solid rgba(255,255,255,0.2)',
                    color: '#f8f8f2'
                  }}>
                    {JSON.stringify(m.timings, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          ))}
          {(loadingA || loadingB) && (
            <div style={{ 
              padding: 24, 
              background: 'linear-gradient(135deg, rgba(255, 193, 7, 0.2), rgba(255, 152, 0, 0.2))', 
              borderRadius: 16, 
              textAlign: 'center',
              color: '#fff3cd',
              fontSize: 18,
              border: '2px solid rgba(255, 193, 7, 0.3)',
              backdropFilter: 'blur(10px)',
              boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
              fontWeight: 'bold',
              textShadow: '0 1px 2px rgba(0,0,0,0.3)'
            }}>
              🤔 AI is thinking...
            </div>
          )}
          {backendHealthy === false && (
            <div style={{ 
              padding: 24, 
              background: 'linear-gradient(135deg, rgba(244, 67, 54, 0.2), rgba(233, 30, 99, 0.2))', 
              borderRadius: 16, 
              fontSize: 16, 
              color: '#ffcdd2',
              textAlign: 'center',
              border: '2px solid rgba(244, 67, 54, 0.3)',
              backdropFilter: 'blur(10px)',
              boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
              fontWeight: 'bold',
              textShadow: '0 1px 2px rgba(0,0,0,0.3)'
            }}>
              ⚠️ AI service unavailable. Please check your connection.
            </div>
          )}
        </div>
      </div>
      
      {(!simpleMode || devMode) && (
        <p style={{ 
          marginTop: 20, 
          fontSize: 12, 
          opacity: 0.7, 
          textAlign: 'center', 
          fontStyle: 'italic',
          color: 'rgba(248,248,242,0.8)',
          textShadow: '0 1px 2px rgba(0,0,0,0.3)'
        }}>
          🎙️ Speech-to-text: whisper.cpp • 🔊 Text-to-speech: Piper TTS • 🎯 Multi-GPU: Leonardo (Mistral 7B) + Jarvis (Phi3) • ⚙️ {devMode ? 'Developer' : 'Power User'} mode for advanced features
        </p>
      )}
    </div>
  );
};

export default GemmaPhi;
