import React, { useState } from 'react';
import api from '../services/api';
import { Bot, Send, Award, Sparkles, CheckCircle2 } from 'lucide-react';

export const InterviewCoachPage: React.FC = () => {
  const [session, setSession] = useState<any>(null);
  const [jobContext, setJobContext] = useState('Full Stack Engineer');
  const [mode, setMode] = useState('structured');
  const [starting, setStarting] = useState(false);
  const [answerText, setAnswerText] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleStartSession = async (e: React.FormEvent) => {
    e.preventDefault();
    setStarting(true);
    try {
      const res = await api.post('/interview/start', { mode, job_context: jobContext });
      setSession({
        id: res.data.session_id,
        messages: [{ role: 'interviewer', content: res.data.first_question }],
        completed: false,
        scores: null
      });
    } catch (err) {
      console.error(err);
    } finally {
      setStarting(false);
    }
  };

  const handleSendAnswer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!answerText.trim() || !session) return;
    setSubmitting(true);
    try {
      const updatedMessages = [...session.messages, { role: 'candidate', content: answerText }];
      setSession({ ...session, messages: updatedMessages });
      const currentAns = answerText;
      setAnswerText('');

      const res = await api.post(`/interview/${session.id}/answer`, { answer_text: currentAns });

      if (res.data.completed) {
        setSession({
          ...session,
          completed: true,
          scores: res.data.scores,
          feedback: res.data.feedback,
          messages: res.data.transcript || updatedMessages
        });
      } else {
        setSession({
          ...session,
          messages: [...updatedMessages, { role: 'interviewer', content: res.data.next_question }]
        });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '850px', margin: '0 auto' }}>
      <div>
        <h2>AI Interview Coach — Mock Practice Engine</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Practice technical and STAR behavioral interview questions with turn-by-turn AI evaluation.</p>
      </div>

      {!session ? (
        <div className="glass-card">
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Bot color="var(--accent-purple)" /> Configure Mock Interview Session
          </h3>

          <form onSubmit={handleStartSession} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label className="label">Target Role / Context</label>
              <input type="text" className="input-field" value={jobContext} onChange={(e) => setJobContext(e.target.value)} placeholder="e.g. Frontend React Developer, Backend Engineer" required />
            </div>

            <div>
              <label className="label">Interview Engine Mode</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div
                  onClick={() => setMode('structured')}
                  style={{
                    padding: '1rem',
                    borderRadius: '8px',
                    background: mode === 'structured' ? 'rgba(99,102,241,0.2)' : 'rgba(10,13,20,0.5)',
                    border: mode === 'structured' ? '1px solid var(--accent-primary)' : '1px solid var(--border-color)',
                    cursor: 'pointer'
                  }}
                >
                  <strong style={{ display: 'block', marginBottom: '0.25rem' }}>Structured Mode</strong>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Standard rubric of core behavioral and technical questions.</span>
                </div>

                <div
                  onClick={() => setMode('adaptive')}
                  style={{
                    padding: '1rem',
                    borderRadius: '8px',
                    background: mode === 'adaptive' ? 'rgba(139,92,246,0.2)' : 'rgba(10,13,20,0.5)',
                    border: mode === 'adaptive' ? '1px solid var(--accent-purple)' : '1px solid var(--border-color)',
                    cursor: 'pointer'
                  }}
                >
                  <strong style={{ display: 'block', marginBottom: '0.25rem' }}>Adaptive AI Mode</strong>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>LLM dynamically asks follow-up questions based on your answers.</span>
                </div>
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ marginTop: '0.5rem' }} disabled={starting}>
              <Sparkles size={16} /> {starting ? 'Initializing AI Interviewer...' : 'Start Interview Session'}
            </button>
          </form>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Chat Transcript Area */}
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', minHeight: '380px', maxHeight: '500px', overflowY: 'auto', padding: '1.5rem' }}>
            {session.messages.map((m: any, i: number) => (
              <div
                key={i}
                style={{
                  alignSelf: m.role === 'interviewer' ? 'flex-start' : 'flex-end',
                  maxWidth: '75%',
                  padding: '1rem',
                  borderRadius: '12px',
                  background: m.role === 'interviewer' ? 'rgba(18,24,38,0.9)' : 'linear-gradient(135deg, var(--accent-primary), var(--accent-primary-hover))',
                  border: m.role === 'interviewer' ? '1px solid var(--border-color)' : 'none',
                  color: 'white',
                  fontSize: '0.9rem',
                  lineHeight: '1.5'
                }}
              >
                <strong style={{ display: 'block', fontSize: '0.75rem', color: m.role === 'interviewer' ? 'var(--accent-secondary)' : '#e0e7ff', marginBottom: '0.35rem', textTransform: 'capitalize' }}>
                  {m.role}
                </strong>
                {m.content}
              </div>
            ))}
          </div>

          {session.completed ? (
            <div className="glass-card" style={{ textAlign: 'center', padding: '2rem' }}>
              <div style={{ width: '56px', height: '56px', borderRadius: '50%', background: 'rgba(16,185,129,0.15)', color: '#34d399', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
                <Award size={28} />
              </div>
              <h3>Interview Complete!</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.5rem', marginBottom: '1.5rem' }}>{session.feedback}</p>

              <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', marginBottom: '1.5rem' }}>
                <div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Communication</span>
                  <h3 style={{ color: '#34d399' }}>{session.scores?.communication}%</h3>
                </div>
                <div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Technical Depth</span>
                  <h3 style={{ color: '#818cf8' }}>{session.scores?.technical_depth}%</h3>
                </div>
                <div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Overall Score</span>
                  <h3 style={{ color: '#a78bfa' }}>{session.scores?.overall}%</h3>
                </div>
              </div>

              <button onClick={() => setSession(null)} className="btn btn-primary">Start New Interview</button>
            </div>
          ) : (
            <form onSubmit={handleSendAnswer} style={{ display: 'flex', gap: '0.75rem' }}>
              <input
                type="text"
                className="input-field"
                placeholder="Type your response here..."
                value={answerText}
                onChange={(e) => setAnswerText(e.target.value)}
                disabled={submitting}
                required
              />
              <button type="submit" className="btn btn-primary" disabled={submitting}>
                <Send size={16} /> Send
              </button>
            </form>
          )}
        </div>
      )}
    </div>
  );
};
