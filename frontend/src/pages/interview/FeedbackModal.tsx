import React, { useState } from 'react';
import { Sparkles } from 'lucide-react';

interface Props {
  onSkip: () => void;
  onSubmit: (data: {
    rating: string | null;
    hoping_to_improve: string[];
    what_should_be_better: string[];
    comment: string;
  }) => void;
}

const RATINGS: [string, string, string][] = [
  ['difficult', '😣', 'Difficult'],
  ['okay', '🙂', 'Okay'],
  ['good', '😄', 'Good'],
  ['great', '🤩', 'Great'],
];
const IMPROVE = ['Build confidence', 'Communication', 'Technical skills', 'Interview practice', 'Something else'];
const BETTER = ['Questions', 'AI voice', 'Recording', 'Interview length', 'Feedback report', 'Technical issue'];

export const FeedbackModal: React.FC<Props> = ({ onSkip, onSubmit }) => {
  const [rating, setRating] = useState<string | null>(null);
  const [improve, setImprove] = useState<string[]>([]);
  const [better, setBetter] = useState<string[]>([]);
  const [comment, setComment] = useState('');

  const toggle = (list: string[], setList: (v: string[]) => void, value: string) => {
    setList(list.includes(value) ? list.filter((v) => v !== value) : [...list, value]);
  };

  return (
    <div className="iv-modal-overlay">
      <div className="iv-modal" onClick={(e) => e.stopPropagation()}>
        <span className="iv-eyebrow"><Sparkles size={12} /> Help us improve</span>
        <h2>How did this interview feel?</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
          It takes less than a minute. Feedback stays private.
        </p>

        <div className="iv-emoji-grid">
          {RATINGS.map(([key, emoji, label]) => (
            <button
              key={key}
              className={`iv-emoji-btn ${rating === key ? 'active' : ''}`}
              onClick={() => setRating(key)}
            >
              <span className="e">{emoji}</span>
              {label}
            </button>
          ))}
        </div>

        <label className="label" style={{ fontSize: '0.82rem', fontWeight: 600 }}>What were you hoping to improve?</label>
        <div className="iv-pills" style={{ margin: '0.5rem 0 1rem' }}>
          {IMPROVE.map((t) => (
            <button key={t} className={`iv-pill ${improve.includes(t) ? 'active' : ''}`} onClick={() => toggle(improve, setImprove, t)}>
              {t}
            </button>
          ))}
        </div>

        <label className="label" style={{ fontSize: '0.82rem', fontWeight: 600 }}>What should be better?</label>
        <div className="iv-pills" style={{ margin: '0.5rem 0 1rem' }}>
          {BETTER.map((t) => (
            <button key={t} className={`iv-pill ${better.includes(t) ? 'active' : ''}`} onClick={() => toggle(better, setBetter, t)}>
              {t}
            </button>
          ))}
        </div>

        <label className="label" style={{ fontSize: '0.82rem', fontWeight: 600 }}>Anything else? <span className="iv-hint">Optional</span></label>
        <textarea
          className="input-field"
          rows={3}
          maxLength={2000}
          placeholder="Tell us what happened or what would make the experience better…"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          style={{ marginTop: '0.35rem' }}
        />

        <div className="iv-modal-actions" style={{ marginTop: '1rem' }}>
          <button className="btn" onClick={onSkip}>Skip for now</button>
          <button
            className="btn btn-primary"
            onClick={() => onSubmit({ rating, hoping_to_improve: improve, what_should_be_better: better, comment })}
          >
            Send private feedback
          </button>
        </div>
      </div>
    </div>
  );
};
