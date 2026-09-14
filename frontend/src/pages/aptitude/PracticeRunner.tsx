import React, { useEffect, useState } from 'react';
import { ArrowLeft, Check, X, ArrowRight, RotateCw, Award } from 'lucide-react';
import api from '../../services/api';
import { Loading, EmptyState } from '../../components/codequest/ui';
import type { PracticeQuestion, CheckResult } from './types';

interface Props {
  topicSlug: string;
  topicName: string;
  subtopic?: string;
  onBack: () => void;
  notify: (msg: string, tone?: 'success' | 'error') => void;
  onProgressChanged?: () => void;
}

export const PracticeRunner: React.FC<Props> = ({
  topicSlug,
  topicName,
  subtopic,
  onBack,
  notify,
  onProgressChanged,
}) => {
  const [questions, setQuestions] = useState<PracticeQuestion[] | null>(null);
  const [idx, setIdx] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [result, setResult] = useState<CheckResult | null>(null);
  const [checking, setChecking] = useState(false);
  const [correctCount, setCorrectCount] = useState(0);
  const [marks, setMarks] = useState<Record<number, boolean>>({});
  const [done, setDone] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const params: Record<string, any> = { limit: 12 };
    if (subtopic) params.subtopic = subtopic;
    api
      .get<PracticeQuestion[]>(`/aptitude/topics/${topicSlug}/questions`, { params })
      .then(({ data }) => {
        if (!cancelled) setQuestions(data);
      })
      .catch(() => {
        if (!cancelled) setQuestions([]);
      });
    return () => {
      cancelled = true;
    };
  }, [topicSlug, subtopic]);

  const q = questions && questions[idx];

  const handleSelect = async (choice: number) => {
    if (result || checking || !q) return; // locked after answering
    setSelected(choice);
    setChecking(true);
    try {
      const { data } = await api.post<CheckResult>('/aptitude/check', {
        question_id: q.id,
        choice,
      });
      setResult(data);
      setMarks((m) => ({ ...m, [idx]: data.correct }));
      if (data.correct) {
        setCorrectCount((c) => c + 1);
        if (data.points_earned > 0) notify(`Correct! +${data.points_earned} XP`, 'success');
      }
      onProgressChanged?.();
    } catch {
      notify('Could not check the answer. Try again.', 'error');
      setSelected(null);
    } finally {
      setChecking(false);
    }
  };

  const next = () => {
    if (!questions) return;
    if (idx + 1 >= questions.length) {
      setDone(true);
      return;
    }
    setIdx((i) => i + 1);
    setSelected(null);
    setResult(null);
  };

  const restart = () => {
    setIdx(0);
    setSelected(null);
    setResult(null);
    setCorrectCount(0);
    setMarks({});
    setDone(false);
    setQuestions(null);
    const params: Record<string, any> = { limit: 12 };
    if (subtopic) params.subtopic = subtopic;
    api
      .get<PracticeQuestion[]>(`/aptitude/topics/${topicSlug}/questions`, { params })
      .then(({ data }) => setQuestions(data))
      .catch(() => setQuestions([]));
  };

  if (questions === null) return <Loading label="Loading questions…" />;
  if (questions.length === 0) {
    return (
      <div className="aq-runner">
        <button className="aq-link" onClick={onBack}>
          <ArrowLeft size={14} /> Back to topics
        </button>
        <EmptyState title="No questions yet" text="This topic has no published questions." actionLabel="Back" onAction={onBack} />
      </div>
    );
  }

  if (done) {
    const total = questions.length;
    const pct = Math.round((correctCount / total) * 100);
    return (
      <div className="aq-runner">
        <div className="glass-card aq-summary">
          <div style={{ width: 60, height: 60, borderRadius: '50%', background: 'rgba(16,185,129,0.15)', color: '#34d399', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
            <Award size={30} />
          </div>
          <div className="aq-summary-score" style={{ color: pct >= 60 ? '#34d399' : pct >= 30 ? '#f59e0b' : '#ef4444' }}>
            {correctCount}/{total}
          </div>
          <p style={{ color: 'var(--text-muted)', margin: '0.5rem 0 1.5rem' }}>
            {topicName}{subtopic ? ` · ${subtopic}` : ''} — {pct}% correct
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
            <button className="aq-btn ghost" onClick={onBack}>
              <ArrowLeft size={14} /> Back to topics
            </button>
            <button className="aq-btn" onClick={restart}>
              <RotateCw size={14} /> Practise again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="aq-runner">
      <div className="aq-runner-head">
        <button className="aq-link" onClick={onBack}>
          <ArrowLeft size={14} /> {topicName}{subtopic ? ` · ${subtopic}` : ''}
        </button>
        <div className="aq-progress-pills">
          {questions.map((_, i) => (
            <span
              key={i}
              className={`aq-pip ${i === idx ? 'cur' : marks[i] === true ? 'ok' : marks[i] === false ? 'bad' : ''}`}
            />
          ))}
        </div>
      </div>

      <div className="aq-qcard">
        <div className="aq-qmeta">
          <span className="aq-tag">{q!.subtopic || q!.topic}</span>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Question {idx + 1} of {questions.length} · {q!.points} pts
            {q!.solved && <span style={{ color: '#34d399', marginLeft: 8 }}>✓ solved</span>}
          </span>
        </div>

        <div className="aq-qtext">{q!.question_text}</div>

        <div className="aq-opts">
          {q!.options.map((opt, i) => {
            let cls = 'aq-opt';
            if (result) {
              cls += ' locked';
              if (i === result.correct_index) cls += ' correct';
              else if (i === selected) cls += ' wrong';
            } else if (i === selected) {
              cls += ' sel';
            }
            return (
              <div key={i} className={cls} onClick={() => handleSelect(i)}>
                <span className="aq-opt-key">{String.fromCharCode(65 + i)}.</span>
                <span>{opt}</span>
                {result && i === result.correct_index && <Check size={16} className="aq-opt-mark" color="#34d399" />}
                {result && i === selected && !result.correct && <X size={16} className="aq-opt-mark" color="#ef4444" />}
              </div>
            );
          })}
        </div>

        {result && (
          <div className={`aq-explain ${result.correct ? 'ok' : 'bad'}`}>
            <strong>{result.correct ? 'Correct!' : 'Not quite.'}</strong>
            {result.explanation || 'Review the correct option highlighted above.'}
          </div>
        )}
      </div>

      <div className="aq-runner-foot">
        <span className="aq-score">
          Score: <b>{correctCount}</b> / {questions.length}
        </span>
        <button className="aq-btn" onClick={next} disabled={!result}>
          {idx + 1 >= questions.length ? 'Finish' : 'Next question'} <ArrowRight size={15} />
        </button>
      </div>
    </div>
  );
};
