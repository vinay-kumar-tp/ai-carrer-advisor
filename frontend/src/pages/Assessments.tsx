import React from 'react';
import { BarChart3, Award, CheckCircle2, Zap } from 'lucide-react';

export const AssessmentsPage: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h2>Assessments & Learning Readiness Analytics</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Aggregate report of coding submissions, aptitude benchmarks, personality profiles, and mock interview feedback.</p>
      </div>

      <div className="grid-3">
        <div className="glass-card">
          <h3 style={{ marginBottom: '1rem', color: '#818cf8', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <BarChart3 size={20} /> Code Quest Proficiency
          </h3>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '0.25rem' }}>85%</h1>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Solved 3/3 easy problems with 100% acceptance score.</p>
        </div>

        <div className="glass-card">
          <h3 style={{ marginBottom: '1rem', color: '#34d399', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Award size={20} /> Aptitude Readiness
          </h3>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '0.25rem' }}>92%</h1>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Top percentile in Quantitative & Logical reasoning.</p>
        </div>

        <div className="glass-card">
          <h3 style={{ marginBottom: '1rem', color: '#a78bfa', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Zap size={20} /> Interview Communication
          </h3>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '0.25rem' }}>84%</h1>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Rated high in technical depth and confidence.</p>
        </div>
      </div>

      <div className="glass-card">
        <h3 style={{ marginBottom: '1rem' }}>Overall Career Readiness Certificate</h3>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1.25rem', background: 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(16,185,129,0.15))', borderRadius: '10px', border: '1px solid rgba(16,185,129,0.3)' }}>
          <div>
            <span style={{ fontSize: '1.1rem', fontWeight: 700, color: 'white', display: 'block' }}>Verified Full-Stack AI Engineer Standard</span>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Issued by Carrerpulse Ai Platform • Certified Ready for Hiring</span>
          </div>
          <button className="btn btn-primary">
            Download Credential PDF
          </button>
        </div>
      </div>
    </div>
  );
};
