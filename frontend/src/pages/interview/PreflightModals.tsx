import React, { useEffect, useRef, useState } from 'react';
import { X, Check, Camera, Mic, ArrowRight } from 'lucide-react';

/* ─── Readiness modal ("Ready to make this one count?") ─────────── */

interface ReadinessProps {
  onClose: () => void;
  onContinue: () => void;
}

export const ReadinessModal: React.FC<ReadinessProps> = ({ onClose, onContinue }) => {
  const [ready, setReady] = useState(false);
  const steps = [
    ['Settle in', 'Choose a quiet place. We will check your camera and microphone before anything begins.'],
    ['Have a real conversation', 'Listen fully, then answer naturally. Follow-up questions adapt to what you actually say.'],
    ['Learn from the report', 'Your responses are evaluated in the background and turned into focused practice priorities.'],
  ];

  return (
    <div className="iv-modal-overlay" onClick={onClose}>
      <div className="iv-modal" onClick={(e) => e.stopPropagation()}>
        <button className="iv-modal-close" onClick={onClose}><X size={16} /></button>
        <span className="iv-eyebrow">Your practice interview</span>
        <h2>Ready to make this one count?</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
          This is a conversation, not a test. Take a breath, be yourself, and explain your thinking aloud.
        </p>

        {steps.map(([title, desc], i) => (
          <div className="iv-step-row" key={i}>
            <div className="iv-step-num">{String(i + 1).padStart(2, '0')}</div>
            <div>
              <strong>{title}</strong>
              <span>{desc}</span>
            </div>
          </div>
        ))}

        <label className="iv-check-row">
          <input type="checkbox" checked={ready} onChange={(e) => setReady(e.target.checked)} />
          I&apos;m ready, and I know I can retry a question if audio fails.
        </label>

        <div className="iv-modal-actions">
          <button className="btn" onClick={onClose}>Not yet</button>
          <button className="btn btn-primary" disabled={!ready} onClick={onContinue}>
            Check my camera &amp; microphone <ArrowRight size={15} />
          </button>
        </div>
      </div>
    </div>
  );
};

/* ─── Device check modal ─────────────────────────────────────────── */

interface DeviceCheckProps {
  onCancel: () => void;
  onStart: (stream: MediaStream | null) => void;
}

export const DeviceCheckModal: React.FC<DeviceCheckProps> = ({ onCancel, onStart }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number>(0);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const [camOk, setCamOk] = useState(false);
  const [micOk, setMicOk] = useState(false);
  const [level, setLevel] = useState(0);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play().catch(() => {});
        }
        setCamOk(stream.getVideoTracks().length > 0);

        // Audio level meter — proves the mic is delivering signal.
        const AudioCtx = (window as any).AudioContext || (window as any).webkitAudioContext;
        const ctx: AudioContext = new AudioCtx();
        audioCtxRef.current = ctx;
        const src = ctx.createMediaStreamSource(stream);
        const analyser = ctx.createAnalyser();
        analyser.fftSize = 512;
        src.connect(analyser);
        const data = new Uint8Array(analyser.frequencyBinCount);
        const tick = () => {
          analyser.getByteFrequencyData(data);
          const avg = data.reduce((a, b) => a + b, 0) / data.length;
          setLevel(avg);
          if (avg > 8) setMicOk(true);
          rafRef.current = requestAnimationFrame(tick);
        };
        tick();
      } catch (e: any) {
        setErr('We could not access your camera or microphone. Check browser permissions and try again.');
      }
    })();

    return () => {
      cancelled = true;
      cancelAnimationFrame(rafRef.current);
      audioCtxRef.current?.close().catch(() => {});
      // Note: stream is intentionally NOT stopped here when starting — it is
      // handed off to the live stage. On cancel we stop it explicitly below.
    };
  }, []);

  const stopStream = () => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  };

  const handleCancel = () => {
    stopStream();
    onCancel();
  };

  const handleStart = () => {
    onStart(streamRef.current);
  };

  const bothOk = camOk && micOk;

  return (
    <div className="iv-modal-overlay" onClick={handleCancel}>
      <div className="iv-modal" onClick={(e) => e.stopPropagation()}>
        <span className="iv-eyebrow">Required before the interview</span>
        <h2>Check your camera and microphone</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
          You&apos;ll always see this live check. Your browser only shows its permission prompt when access has not already been granted.
        </p>

        <div className="iv-device-grid">
          <div className="iv-video-preview">
            <video ref={videoRef} muted playsInline />
            {camOk && <span className="iv-live-tag">Camera live</span>}
          </div>
          <div className="iv-device-status">
            <div className={`iv-status-card ${camOk ? 'ok' : ''}`}>
              <span className="iv-status-dot">{camOk ? <Check size={13} /> : <Camera size={13} />}</span>
              <div>
                <strong style={{ display: 'block', fontSize: '0.85rem' }}>Camera</strong>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {camOk ? 'Live video received' : 'Waiting for video…'}
                </span>
              </div>
            </div>
            <div className={`iv-status-card ${micOk ? 'ok' : ''}`}>
              <span className="iv-status-dot">{micOk ? <Check size={13} /> : <Mic size={13} />}</span>
              <div>
                <strong style={{ display: 'block', fontSize: '0.85rem' }}>Microphone</strong>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {micOk ? 'Voice signal detected' : 'Say something to test…'}
                </span>
              </div>
            </div>
            <div className="iv-bar-track" style={{ marginTop: '0.25rem' }}>
              <div className="iv-bar-fill" style={{ width: `${Math.min(100, level * 2)}%`, background: '#34d399' }} />
            </div>
            {bothOk && (
              <span style={{ color: '#34d399', fontSize: '0.8rem', fontWeight: 600 }}>
                Both devices are working. You can start the interview.
              </span>
            )}
          </div>
        </div>

        {err && <p style={{ color: '#fca5a5', fontSize: '0.83rem' }}>{err}</p>}

        <div className="iv-modal-actions">
          <button className="btn" onClick={handleCancel}>Cancel</button>
          <button className="btn btn-primary" onClick={handleStart}>Start interview</button>
        </div>
      </div>
    </div>
  );
};
