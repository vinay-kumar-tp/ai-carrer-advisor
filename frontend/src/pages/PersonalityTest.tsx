import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Sparkles, Award } from 'lucide-react';

export const PersonalityTestPage: React.FC = () => {
  const [questions, setQuestions] = useState<any[]>([]);
  const [answers, setAnswers] = useState<number[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchQuestions();
    fetchMyResult();
  }, []);

  const fetchQuestions = async () => {
    try {
      const res = await api.get('/personality/questions');
      setQuestions(res.data);
      setAnswers(new Array(res.data.length).fill(3)); // neutral baseline
    } catch (err) {
      console.error(err);
    }
  };

  const fetchMyResult = async () => {
    try {
      const res = await api.get('/personality/my-result');
      setResult(res.data);
    } catch (err) {
      // not completed yet
    }
  };

  const handleAnswerChange = (qIdx: number, val: number) => {
    const updated = [...answers];
    updated[qIdx] = val;
    setAnswers(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post('/personality/submit', { answers });
      setResult(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '800px', margin: '0 auto' }}>
      <div>
        <h2>Big Five Personality Inventory (OCEAN Model)</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Discover your workplace personality traits to personalize soft-skills coaching and career pathing.</p>
      </div>

      {result ? (
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles color="var(--accent-purple)" /> Your Big Five Personality Profile
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {Object.entries(result).map(([trait, score]: [string, any]) => (
              <div key={trait}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem', textTransform: 'capitalize', fontWeight: 600 }}>
                  <span>{trait}</span>
                  <span>{score}%</span>
                </div>
                <div style={{ width: '100%', height: '10px', background: 'rgba(255,255,255,0.1)', borderRadius: '5px', overflow: 'hidden' }}>
                  <div style={{ width: `${score}%`, height: '100%', background: 'linear-gradient(90deg, var(--accent-purple), var(--accent-pink))' }} />
                </div>
              </div>
            ))}
          </div>

          <button onClick={() => setResult(null)} className="btn btn-secondary" style={{ alignSelf: 'flex-start' }}>
            Retake Assessment
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {questions.map((q, idx) => (
            <div key={q.id} style={{ paddingBottom: '1rem', borderBottom: idx < questions.length - 1 ? '1px solid var(--border-color)' : 'none' }}>
              <p style={{ fontWeight: 600, marginBottom: '0.75rem' }}>{idx + 1}. {q.text}</p>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                <span>Disgree</span>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  {[1, 2, 3, 4, 5].map((val) => (
                    <label key={val} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem', cursor: 'pointer' }}>
                      <input
                        type="radio"
                        name={`q_${q.id}`}
                        value={val}
                        checked={answers[idx] === val}
                        onChange={() => handleAnswerChange(idx, val)}
                      />
                      <span>{val}</span>
                    </label>
                  ))}
                </div>
                <span>Agree</span>
              </div>
            </div>
          ))}

          <button type="submit" className="btn btn-primary" style={{ marginTop: '1rem' }} disabled={loading}>
            {loading ? 'Calculating Traits...' : 'Submit & View Results'}
          </button>
        </form>
      )}
    </div>
  );
};
