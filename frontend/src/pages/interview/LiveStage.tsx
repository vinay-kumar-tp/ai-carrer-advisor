import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Volume2, VolumeX, PhoneOff, Mic, Square, Play, Send } from 'lucide-react';
import { speak, stopSpeaking, createRecognizer, ttsSupported, sttSupported } from './speech';
import type { Recognizer } from './speech';

interface Props {
  title: string;
  interviewerName: string;
  questionNumber: number;
  totalQuestions: number;
  question: string;
  isWarmup: boolean;
  /** true while the backend is generating the next question / final report */
  thinking: boolean;
  stream: MediaStream | null;
  onSubmit: (answerText: string) => void;
  onEnd: () => void;
}

const MAX_SECONDS = 120;

/**
 * joining   → user hasn't clicked "Join" yet
 * speaking  → interviewer is reading the question aloud
 * answering → mic is open / user is typing, timer running
 * sending   → answer submitted, waiting for backend (mirrors `thinking`)
 */
type Phase = 'joining' | 'speaking' | 'answering' | 'sending';

export const LiveStage: React.FC<Props> = ({
  title,
  interviewerName,
  questionNumber,
  totalQuestions,
  question,
  isWarmup,
  thinking,
  stream,
  onSubmit,
  onEnd,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const recognizerRef = useRef<Recognizer | null>(null);
  const timerRef = useRef<number>(0);
  const answerRef = useRef('');
  const spokenForRef = useRef<string>('');       // which question text we've already voiced
  const mutedRef = useRef(false);

  const [phase, setPhase] = useState<Phase>('joining');
  const [muted, setMuted] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [transcript, setTranscript] = useState('');
  const [typed, setTyped] = useState('');
  const [micLive, setMicLive] = useState(false);

  mutedRef.current = muted;

  // ── Keep the self-view camera attached (runs on every render; cheap + safe) ──
  useEffect(() => {
    const v = videoRef.current;
    if (v && stream && v.srcObject !== stream) {
      v.srcObject = stream;
      v.play().catch(() => {});
    }
  });

  // ── Timer + recognizer teardown ──
  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = 0;
    }
  };
  const stopRecognizer = () => {
    recognizerRef.current?.stop();
    recognizerRef.current = null;
    setMicLive(false);
  };

  // ── Open the mic + start the countdown ──
  const beginAnswering = useCallback(() => {
    setPhase('answering');
    setSeconds(0);
    setTranscript('');
    setTyped('');
    answerRef.current = '';

    stopTimer();
    timerRef.current = window.setInterval(() => {
      setSeconds((s) => {
        if (s + 1 >= MAX_SECONDS) {
          // Auto-submit at the cap.
          finishAnswer();
          return MAX_SECONDS;
        }
        return s + 1;
      });
    }, 1000);

    const rec = createRecognizer(
      (full) => {
        answerRef.current = full;
        setTranscript(full);
      },
      () => setMicLive(false),
    );
    recognizerRef.current = rec;
    if (rec) {
      rec.start();
      setMicLive(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Speak a question, then hand over to the candidate ──
  const presentQuestion = useCallback(
    (text: string) => {
      spokenForRef.current = text;
      setPhase('speaking');
      const proceed = () => {
        // Only advance if we're still on this same question.
        if (spokenForRef.current === text) beginAnswering();
      };
      if (mutedRef.current || !ttsSupported()) {
        // No voice — give a short beat so the user can read it, then open mic.
        window.setTimeout(proceed, 600);
        return;
      }
      // Safety net: if TTS never fires onend, proceed anyway after a timeout.
      const safety = window.setTimeout(proceed, Math.min(18000, 3000 + text.length * 80));
      speak(text).finally(() => {
        window.clearTimeout(safety);
        proceed();
      });
    },
    [beginAnswering],
  );

  // ── React to a NEW question arriving from the backend ──
  useEffect(() => {
    if (phase === 'joining') return;                 // wait for the Join click
    if (thinking) return;                            // backend still working
    if (!question) return;
    if (spokenForRef.current === question) return;   // already presented this one
    presentQuestion(question);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [question, thinking, phase]);

  // ── Cleanup on unmount ──
  useEffect(() => {
    return () => {
      stopTimer();
      recognizerRef.current?.stop();
      stopSpeaking();
    };
  }, []);

  // ── Submit the current answer ──
  const finishAnswer = useCallback(() => {
    stopTimer();
    stopRecognizer();
    stopSpeaking();
    const spoken = answerRef.current.trim();
    const written = typed.trim();
    const finalAnswer = [spoken, written].filter(Boolean).join(' ').trim();
    setPhase('sending');
    onSubmit(finalAnswer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [onSubmit, typed]);

  const handleJoin = () => {
    // Kick the flow off explicitly from a user gesture (needed for autoplay/mic).
    setPhase('speaking');
    presentQuestion(question);
  };

  const toggleMute = () => {
    setMuted((m) => {
      const next = !m;
      if (next) stopSpeaking();
      return next;
    });
  };

  const handleEnd = () => {
    stopTimer();
    stopRecognizer();
    stopSpeaking();
    onEnd();
  };

  // Manual mic re-arm (if the browser stopped it or the user muted then wants back)
  const restartMic = () => {
    if (phase !== 'answering') return;
    stopRecognizer();
    const rec = createRecognizer(
      (full) => {
        answerRef.current = full;
        setTranscript(full);
      },
      () => setMicLive(false),
    );
    recognizerRef.current = rec;
    if (rec) {
      rec.start();
      setMicLive(true);
    }
  };

  const remaining = MAX_SECONDS - seconds;
  const mmss = `${String(Math.floor(remaining / 60)).padStart(2, '0')}:${String(remaining % 60).padStart(2, '0')}`;

  const isSpeaking = phase === 'speaking';
  const isAnswering = phase === 'answering';
  const isSending = phase === 'sending' || thinking;

  let statusChip = 'Listening to you';
  if (phase === 'joining') statusChip = 'Ready to join';
  else if (isSending) statusChip = 'Reflecting on your response';
  else if (isSpeaking) statusChip = `${interviewerName} is speaking`;

  const canSubmit = (answerRef.current.trim().length + typed.trim().length) > 0;

  return (
    <div className="iv-stage">
      <div className="iv-stage-inner">
        {/* Header */}
        <div className="iv-stage-card iv-stage-header">
          <span className="iv-stage-qnum">
            Question {questionNumber} of {totalQuestions}<b>{title}</b>
          </span>
          <div className="iv-stage-controls">
            <span className="iv-chip-btn iv-chip-status">{statusChip}</span>
            <button className="iv-chip-btn" onClick={toggleMute} title="Toggle interviewer voice">
              {muted ? <VolumeX size={14} /> : <Volume2 size={14} />}
            </button>
            <button className="iv-chip-btn danger" onClick={handleEnd}>
              <PhoneOff size={14} /> End
            </button>
          </div>
        </div>

        {phase === 'joining' ? (
          <div className="iv-stage-card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
            <div className="iv-avatar" style={{ margin: '0 auto 1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '3rem' }}>🧑‍💼</div>
            <span className="iv-eyebrow" style={{ color: '#34d399' }}>Your interviewer is ready</span>
            <h2 style={{ margin: '0.5rem 0' }}>Join interview with voice</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: 400, margin: '0 auto 1.25rem' }}>
              {interviewerName} will speak each question, then your mic opens automatically. You can
              also type your answer at any time.
            </p>
            <button className="btn btn-primary" onClick={handleJoin}>
              <Volume2 size={16} /> Join interview
            </button>
            {!sttSupported() && (
              <p className="iv-hint" style={{ marginTop: '0.75rem' }}>
                Voice input isn&apos;t supported in this browser — you can type your answers. (Chrome/Edge recommended.)
              </p>
            )}
          </div>
        ) : (
          <>
            {/* Conversation area */}
            <div className="iv-stage-card iv-convo">
              <div style={{ display: 'flex', gap: '1.25rem' }}>
                <div className="iv-avatar-card">
                  <div className="iv-avatar" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '3.5rem' }}>🧑‍💼</div>
                  <span className="iv-avatar-name">
                    {isSpeaking && <span className="iv-speaking-dot" />} {interviewerName}
                  </span>
                  <span className="iv-avatar-role">Practice interviewer</span>
                </div>

                <div className="iv-question-panel">
                  {isSending ? (
                    <div className="iv-considering">
                      <span className="iv-dots"><span>●</span><span>●</span><span>●</span></span>
                      {interviewerName} is taking in your answer
                    </div>
                  ) : (
                    <>
                      <span className="iv-question-eyebrow">
                        {isSpeaking ? 'Interviewer speaking' : 'Your turn to respond'}
                      </span>
                      <div className="iv-question-text">{question}</div>
                    </>
                  )}
                </div>
              </div>

              <div className="iv-self-cam">
                <div className="iv-video-preview">
                  <video ref={videoRef} autoPlay muted playsInline />
                  {stream && <span className="iv-live-tag">You</span>}
                </div>
                <span className="iv-self-label">You</span>
                <span className="iv-self-sub">
                  {isAnswering ? 'Recording your answer' : 'Listening to interviewer'}
                </span>
              </div>
            </div>

            {/* Answer control bar */}
            <div className="iv-answer-bar" style={{ flexWrap: 'wrap' }}>
              <div className="iv-answer-status">
                {isAnswering ? (
                  <>
                    <span className={`iv-mic-badge ${micLive ? 'on' : ''}`}>
                      {micLive ? <span className="iv-rec-dot" /> : <Mic size={13} />}
                      {micLive ? 'Mic on' : 'Mic idle'}
                    </span>
                    <div>
                      <strong>Recording your answer</strong>
                      <span>Speak naturally, or type below. Max 02:00.</span>
                    </div>
                    <span className="iv-timer">{mmss} left</span>
                  </>
                ) : (
                  <>
                    <span className="iv-mic-badge"><Mic size={13} /> Mic off</span>
                    <div>
                      <strong>Your interviewer is {isSpeaking ? 'speaking' : 'considering your answer'}</strong>
                      <span>The conversation will continue in a moment.</span>
                    </div>
                  </>
                )}
              </div>

              {isAnswering ? (
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  {sttSupported() && !micLive && (
                    <button className="iv-chip-btn" onClick={restartMic} title="Turn mic back on">
                      <Mic size={14} /> Mic
                    </button>
                  )}
                  <button
                    className="btn"
                    style={{ background: canSubmit ? '#ef4444' : '#7f1d1d', color: '#fff' }}
                    onClick={finishAnswer}
                    disabled={!canSubmit}
                  >
                    <Square size={14} /> Finish &amp; send
                  </button>
                </div>
              ) : isSpeaking ? (
                <button className="btn btn-primary" onClick={beginAnswering}>
                  <Play size={14} /> Start answer
                </button>
              ) : (
                <button className="btn" disabled>
                  <Play size={14} /> {isWarmup ? 'Warm-up' : 'Waiting…'}
                </button>
              )}

              {/* Typed answer fallback — always available while answering */}
              {isAnswering && (
                <div style={{ display: 'flex', gap: '0.5rem', width: '100%', marginTop: '0.25rem' }}>
                  <input
                    className="input-field"
                    style={{ flex: 1 }}
                    placeholder="…or type your answer here and press Enter"
                    value={typed}
                    onChange={(e) => setTyped(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && canSubmit) finishAnswer();
                    }}
                  />
                  <button className="btn" onClick={finishAnswer} disabled={!canSubmit} title="Send">
                    <Send size={14} />
                  </button>
                </div>
              )}

              {transcript && isAnswering && (
                <div className="iv-live-transcript" style={{ width: '100%' }}>“{transcript}”</div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};
