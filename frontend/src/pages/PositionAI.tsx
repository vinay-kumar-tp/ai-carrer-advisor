import React, { useState } from 'react';
import api from '../services/api';
import { Target, CheckCircle2, AlertCircle, ArrowRight } from 'lucide-react';

export const PositionAIPage: React.FC = () => {
  const [jobDescription, setJobDescription] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobDescription.trim()) return;
    setAnalyzing(true);
    try {
      // Simulate Position AI RAG skill gap algorithm
      setTimeout(() => {
        setAnalysis({
          fitScore: 78,
          matchedSkills: ['Python', 'React', 'FastAPI', 'Git', 'SQL'],
          missingSkills: ['Docker', 'Kubernetes', 'Redis Caching'],
          recommendedCourses: [
            { title: 'Docker & Kubernetes Mastery for Developers', provider: 'Coursera', duration: '6 hours' },
            { title: 'Redis In-Memory Caching & Architecture', provider: 'LeetCode Learn', duration: '4 hours' }
          ]
        });
        setAnalyzing(false);
      }, 1500);
    } catch (err) {
      setAnalyzing(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '900px', margin: '0 auto' }}>
      <div>
        <h2>Position AI — Skill Gap & Fit Analyzer</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Paste a target Job Description to compare required skills against your profile and get an instant readiness match.</p>
      </div>

      <div className="glass-card">
        <form onSubmit={handleAnalyze} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <label className="label">Target Job Description (JD)</label>
          <textarea
            className="input-field"
            rows={6}
            placeholder="Paste Job Description here (e.g. 'We are hiring a Full Stack Developer proficient in Python, React, Docker, and Redis...')"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            required
          />
          <button type="submit" className="btn btn-primary" style={{ alignSelf: 'flex-start' }} disabled={analyzing}>
            <Target size={16} /> {analyzing ? 'Analyzing Skill Vectors...' : 'Analyze Job Fit'}
          </button>
        </form>
      </div>

      {analysis && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Fit Score Badge */}
          <div className="glass-card" style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(6,182,212,0.1))', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.5rem 2rem' }}>
            <div>
              <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Position Fit Score</span>
              <h2 style={{ fontSize: '2.5rem', color: '#34d399' }}>{analysis.fitScore}% Match</h2>
            </div>
            <div className="badge badge-emerald" style={{ fontSize: '1rem', padding: '0.5rem 1.25rem' }}>
              Strong Alignment
            </div>
          </div>

          <div className="grid-2">
            {/* Matched Skills */}
            <div className="glass-card">
              <h3 style={{ marginBottom: '1rem', color: '#34d399', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle2 size={20} /> Skills You Have ({analysis.matchedSkills.length})
              </h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {analysis.matchedSkills.map((s: string) => (
                  <span key={s} className="badge badge-emerald" style={{ fontSize: '0.85rem' }}>{s}</span>
                ))}
              </div>
            </div>

            {/* Missing Skills */}
            <div className="glass-card">
              <h3 style={{ marginBottom: '1rem', color: '#f87171', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertCircle size={20} /> Skill Gaps Identified ({analysis.missingSkills.length})
              </h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {analysis.missingSkills.map((s: string) => (
                  <span key={s} style={{ background: 'rgba(239,68,68,0.15)', color: '#f87171', border: '1px solid rgba(239,68,68,0.3)', padding: '0.25rem 0.6rem', borderRadius: '20px', fontSize: '0.85rem', fontWeight: 600 }}>{s}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Recommended Learning Path */}
          <div className="glass-card">
            <h3 style={{ marginBottom: '1rem' }}>Targeted Learning Recommendations</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {analysis.recommendedCourses.map((c: any, i: number) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 1rem', background: 'rgba(10,13,20,0.5)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div>
                    <span style={{ fontWeight: 600 }}>{c.title}</span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block' }}>{c.provider} • {c.duration}</span>
                  </div>
                  <button className="btn btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}>
                    Start Course <ArrowRight size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
