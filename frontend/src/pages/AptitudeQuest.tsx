import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Brain, CheckCircle2, Clock, Award } from 'lucide-react';

export const AptitudeQuestPage: React.FC = () => {
  const [questions, setQuestions] = useState<any[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<number[]>([]);
  const [result, setResult] = useState<any>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchQuestions();
  }, []);

  const fetchQuestions = async () => {
    try {
      const res = await api.get('/aptitude/questions');
      setQuestions(res.data);
      setSelectedAnswers(new Array(res.data.length).fill(-1));
    } catch (err) {
      console.error(err);
    }
  };

  const handleSelectOption = (optIdx: number) => {
    const updated = [...selectedAnswers];
    updated[currentIdx] = optIdx;
    setSelectedAnswers(updated);
  };

  const handleSubmitQuiz = async () => {
    setSubmitting(true);
    try {
      const res = await api.post('/aptitude/submit', {
        question_ids: questions.map((q) => q.id),
        answers: selectedAnswers,
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (questions.length === 0) return <div style={{ color: 'var(--text-muted)' }}>Loading questions...</div>;

  const currentQ = questions[currentIdx];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '800px', margin: '0 auto' }}>
      <div>
        <h2>Aptitude Quest — MCQ & Reasoning Studio</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Timed practice quizzes covering quantitative aptitude, logical reasoning, and verbal fluency.</p>
      </div>

      {result ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: 'rgba(16,185,129,0.15)', color: '#34d399', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
            <Award size={32} />
          </div>
          <h2>Quiz Completed!</h2>
          <p style={{ fontSize: '1.25rem', margin: '0.5rem 0 1rem' }}>
            Score: <strong style={{ color: '#34d399' }}>{result.score} / {result.total} ({result.percentage}%)</strong>
          </p>

          <div className="badge badge-emerald" style={{ fontSize: '0.9rem', padding: '0.4rem 1rem' }}>
            +{result.score * 5} XP Awarded
          </div>

          <button onClick={() => { setResult(null); setCurrentIdx(0); fetchQuestions(); }} className="btn btn-primary" style={{ marginTop: '2rem' }}>
            Retake Practice Quiz
          </button>
        </div>
      ) : (
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-color)' }}>
            <span className="badge badge-indigo">{currentQ.topic}</span>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Clock size={14} /> Question {currentIdx + 1} of {questions.length}
            </span>
          </div>

          <h3 style={{ fontSize: '1.15rem', marginBottom: '1.5rem', lineHeight: '1.6' }}>{currentQ.question_text}</h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '2rem' }}>
            {currentQ.options?.map((opt: string, i: number) => (
              <div
                key={i}
                onClick={() => handleSelectOption(i)}
                style={{
                  padding: '1rem',
                  borderRadius: '8px',
                  background: selectedAnswers[currentIdx] === i ? 'rgba(99,102,241,0.2)' : 'rgba(10,13,20,0.5)',
                  border: selectedAnswers[currentIdx] === i ? '1px solid var(--accent-primary)' : '1px solid var(--border-color)',
                  cursor: 'pointer',
                  fontSize: '0.95rem',
                  transition: 'all 0.15s ease'
                }}
              >
                <strong>{String.fromCharCode(65 + i)}.</strong> {opt}
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <button className="btn btn-secondary" disabled={currentIdx === 0} onClick={() => setCurrentIdx((c) => c - 1)}>
              Previous
            </button>
            {currentIdx < questions.length - 1 ? (
              <button className="btn btn-primary" onClick={() => setCurrentIdx((c) => c + 1)}>
                Next Question
              </button>
            ) : (
              <button className="btn btn-primary" onClick={handleSubmitQuiz} disabled={submitting}>
                {submitting ? 'Submitting...' : 'Submit Quiz'}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
