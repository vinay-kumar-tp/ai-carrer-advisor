import React, { useEffect, useMemo, useRef, useState } from 'react';
import api from '../../services/api';
import { Loading } from '../../components/codequest/ui';
import type { FormQuestions, AssessmentResult } from './types';

interface Props {
  formKey: string;
  onDone: (result: AssessmentResult) => void;
  onExit: () => void;
  notify: (msg: string, tone?: 'success' | 'error') => void;
}

const fmtTime = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;

export const AssessmentRunner: React.FC<Props> = ({ formKey, onDone, onExit, notify }) => {
  const [data, setData] = useState<FormQuestions | null>(null);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [idx, setIdx] = useState(0);
  const [seconds, setSeconds] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const startRef = useRef(Date.now());

  useEffect(() => {
    api
      .get<FormQuestions>(`/personality/forms/${formKey}/questions`)
      .then(({ data }) => setData(data))
      .catch(() => setData(null));
  }, [formKey]);

  useEffect(() => {
    const t = window.setInterval(() => setSeconds(Math.floor((Date.now() - startRef.current) / 1000)), 1000);
    return () => window.clearInterval(t);
  }, []);

  const total = data?.questions.length ?? 0;
  const answeredCount = Object.keys(answers).length;
  const pctDone = total ? Math.round((answeredCount / total) * 100) : 0;

  // "Running score" ring = live snapshot of trait tilt from answered items only.
  // We use overall agreement lean (avg of answered on 0-100) as a simple, honest
  // "profile forming" indicator (the real scores come from the server on submit).
  const runningPct = useMemo(() => {
    const vals = Object.values(answers);
    if (!vals.length) return 0;
    const avg = vals.reduce((a, b) => a + b, 0) / vals.length; // 1..5
    return Math.round(((avg - 1) / 4) * 100);
  }, [answers]);

  const choose = (value: number) => {
    setAnswers((a) => ({ ...a, [idx]: value }));
    // auto-advance for a smooth flow, but not past the end
    if (idx < total - 1) {
      window.setTimeout(() => setIdx((i) => Math.min(i + 1, total - 1)), 150);
    }
  };

  const submit = async () => {
    if (!data) return;
    if (answeredCount < total) {
      notify(`Please answer all ${total} questions (${total - answeredCount} left).`, 'error');
      // jump to first unanswered
      const firstMissing = data.questions.findIndex((q) => answers[q.index] === undefined);
      if (firstMissing >= 0) setIdx(firstMissing);
      return;
    }
    setSubmitting(true);
    try {
      const responses = data.questions.map((q) => answers[q.index]);
      const { data: result } = await api.post<AssessmentResult>(
        `/personality/forms/${formKey}/submit`,
        { responses, completion_time_seconds: seconds },
      );
      onDone(result);
    } catch (e: any) {
      notify(e?.response?.data?.detail || 'Could not submit. Try again.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  if (!data) return <Loading label="Loading questions…" />;

  const q = data.questions[idx];
  const current = answers[idx];
  const isLast = idx === total - 1;

  // ring geometry
  const R = 54;
  const C = 2 * Math.PI * R;
  const dash = (pctDone / 100) * C;

  return (
    <div className="pt-runner">
      <div className="glass-card">
        <div className="pt-run-head">
          <div className="pt-qcount">
            Question {idx + 1} of {total}
            <span className="pt-badge">{data.form.short_name}</span>
          </div>
          <div className="pt-run-meta">
            <span>{answeredCount} answered</span>
            <span>{fmtTime(seconds)}</span>
            <button className="aq-link" onClick={onExit} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
              Exit
            </button>
          </div>
        </div>

        <div className="pt-progress">
          <div className="pt-progress-fill" style={{ width: `${pctDone}%` }} />
        </div>
        <div className="pt-progress-label">{pctDone}% done</div>

        <div className="pt-prompt">{data.prompt_prefix}</div>
        <div className="pt-question">{q.text}</div>

        <div className="pt-scale">
          {data.scale.map((opt) => (
            <div
              key={opt.value}
              className={`pt-opt ${current === opt.value ? 'sel' : ''}`}
              onClick={() => choose(opt.value)}
            >
              <span className="pt-opt-dot" />
              {opt.label}
            </div>
          ))}
        </div>

        <div className="pt-run-foot">
          <button className="btn btn-secondary" disabled={idx === 0} onClick={() => setIdx((i) => Math.max(0, i - 1))}>
            Previous
          </button>
          {isLast ? (
            <button className="btn btn-primary" onClick={submit} disabled={submitting}>
              {submitting ? 'Scoring…' : 'Submit & view profile'}
            </button>
          ) : (
            <button className="btn btn-primary" onClick={() => setIdx((i) => Math.min(total - 1, i + 1))}>
              Next
            </button>
          )}
        </div>
      </div>

      {/* Running score ring */}
      <div className="glass-card pt-ring-card">
        <div className="pt-ring">
          <svg width="130" height="130">
            <circle cx="65" cy="65" r={R} fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="10" />
            <circle
              cx="65" cy="65" r={R} fill="none"
              stroke={pctDone === 100 ? '#34d399' : '#f59e0b'}
              strokeWidth="10" strokeLinecap="round"
              strokeDasharray={`${dash} ${C}`}
            />
          </svg>
          <div className="pt-ring-num" style={{ color: pctDone === 100 ? '#34d399' : '#f59e0b' }}>
            {runningPct}%
          </div>
        </div>
        <div className="pt-ring-label">Running Score</div>
        <div className="pt-ring-sub">Updates as you answer</div>
      </div>
    </div>
  );
};
