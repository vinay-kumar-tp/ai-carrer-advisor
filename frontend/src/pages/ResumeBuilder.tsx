import React, { useState } from 'react';
import api from '../services/api';
import { FileCheck2, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';

export const ResumeBuilderPage: React.FC = () => {
  const [resumeText, setResumeText] = useState(
    'Alex Johnson\nFull Stack Developer | Python, React, SQL\n\nExperience:\n- Developed REST APIs using Python FastAPI and PostgreSQL\n- Built interactive UI components in React and TypeScript\n- Optimized database queries for high throughput'
  );
  const [scoring, setScoring] = useState(false);
  const [atsResult, setAtsResult] = useState<any>(null);

  const handleScoreResume = async (e: React.FormEvent) => {
    e.preventDefault();
    setScoring(true);
    try {
      const formData = new FormData();
      formData.append('resume_text', resumeText);
      const res = await api.post('/documents/ats-score', formData);
      setAtsResult(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setScoring(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '900px', margin: '0 auto' }}>
      <div>
        <h2>AI Resume Builder & ATS Optimizer</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Format your resume and run automated ATS keyword compatibility scoring against technical standards.</p>
      </div>

      <div className="grid-2">
        {/* Editor */}
        <div className="glass-card">
          <form onSubmit={handleScoreResume} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <label className="label">Resume Plain Text Content</label>
            <textarea
              className="input-field"
              rows={14}
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}
            />
            <button type="submit" className="btn btn-primary" disabled={scoring}>
              <Sparkles size={16} /> {scoring ? 'Scanning ATS Compatibility...' : 'Calculate ATS Score'}
            </button>
          </form>
        </div>

        {/* ATS Results Panel */}
        <div className="glass-card">
          <h3 style={{ marginBottom: '1rem' }}>ATS Scoring Breakdown</h3>

          {atsResult ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div style={{ textAlign: 'center', padding: '1.5rem', background: 'rgba(10,13,20,0.6)', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>ATS Readability Score</span>
                <h1 style={{ fontSize: '3rem', color: atsResult.ats_score > 70 ? '#34d399' : '#f59e0b', margin: '0.25rem 0' }}>{atsResult.ats_score}%</h1>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>High Recruiter Visibility</span>
              </div>

              <div>
                <h4 style={{ fontSize: '0.9rem', marginBottom: '0.5rem', color: '#34d399' }}>Matched Keywords</h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                  {atsResult.matched_keywords?.map((k: string) => (
                    <span key={k} className="badge badge-emerald" style={{ fontSize: '0.75rem' }}>{k}</span>
                  ))}
                </div>
              </div>

              <div>
                <h4 style={{ fontSize: '0.9rem', marginBottom: '0.5rem', color: '#f87171' }}>Missing Critical Keywords</h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                  {atsResult.missing_keywords?.map((k: string) => (
                    <span key={k} style={{ background: 'rgba(239,68,68,0.15)', color: '#f87171', border: '1px solid rgba(239,68,68,0.3)', padding: '0.15rem 0.5rem', borderRadius: '12px', fontSize: '0.75rem' }}>{k}</span>
                  ))}
                </div>
              </div>

              <div>
                <h4 style={{ fontSize: '0.9rem', marginBottom: '0.5rem' }}>AI Formatting Recommendations</h4>
                <ul style={{ paddingLeft: '1.25rem', color: 'var(--text-muted)', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                  {atsResult.suggestions?.map((s: string, i: number) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div style={{ padding: '4rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              Click "Calculate ATS Score" to evaluate your resume structure against industry benchmarks.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
