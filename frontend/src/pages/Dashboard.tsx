import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { Award, Code2, Brain, Briefcase, Bot, ArrowRight, Zap, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({ xp: 150, level: 2, streak: 5, problemsSolved: 3, quizzesPassed: 2 });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Welcome Banner */}
      <div className="glass-card" style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.25), rgba(6,182,212,0.15))', border: '1px solid rgba(99,102,241,0.3)', padding: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Welcome back, {user?.full_name || 'Student'}! 👋</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>Your Carrerpulse Ai Career Readiness Score is currently at <strong style={{ color: '#34d399' }}>82% (Job Ready)</strong></p>
          </div>
          <Link to="/position-ai" className="btn btn-primary">
            Run Skill Gap Analysis <ArrowRight size={16} />
          </Link>
        </div>
      </div>

      {/* Progress Cards */}
      <div className="grid-4">
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <Zap color="#f59e0b" size={24} />
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Total Experience</span>
          </div>
          <h2 style={{ fontSize: '1.8rem' }}>{stats.xp} XP</h2>
          <div className="badge badge-amber" style={{ marginTop: '0.5rem' }}>Level {stats.level} Careerist</div>
        </div>

        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <Code2 color="#6366f1" size={24} />
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Problems Solved</span>
          </div>
          <h2 style={{ fontSize: '1.8rem' }}>{stats.problemsSolved}</h2>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>+2 solved this week</span>
        </div>

        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <Brain color="#06b6d4" size={24} />
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Quizzes Passed</span>
          </div>
          <h2 style={{ fontSize: '1.8rem' }}>{stats.quizzesPassed}</h2>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Average accuracy 88%</span>
        </div>

        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <Award color="#ec4899" size={24} />
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Day Streak</span>
          </div>
          <h2 style={{ fontSize: '1.8rem' }}>{stats.streak} Days</h2>
          <span style={{ fontSize: '0.8rem', color: '#ec4899' }}>🔥 Keep it up!</span>
        </div>
      </div>

      {/* Quick Launch Modules */}
      <div>
        <h2 style={{ marginBottom: '1rem', fontSize: '1.4rem' }}>Quick Launch Modules</h2>
        <div className="grid-3">
          <Link to="/code-quest" className="glass-card glass-card-interactive">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
              <div style={{ padding: '0.75rem', borderRadius: '10px', background: 'rgba(99,102,241,0.15)', color: '#818cf8' }}>
                <Code2 size={24} />
              </div>
              <div>
                <h3>Code Quest</h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Algorithmic & practical challenges</span>
              </div>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Solve problems in Python/JS, get instant auto-graded feedback & earn XP.</p>
          </Link>

          <Link to="/interview-coach" className="glass-card glass-card-interactive">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
              <div style={{ padding: '0.75rem', borderRadius: '10px', background: 'rgba(139,92,246,0.15)', color: '#a78bfa' }}>
                <Bot size={24} />
              </div>
              <div>
                <h3>AI Interview Coach</h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Structured & Adaptive Mock Interviews</span>
              </div>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Practice technical and behavioral interview questions with real-time AI feedback.</p>
          </Link>

          <Link to="/resume-builder" className="glass-card glass-card-interactive">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
              <div style={{ padding: '0.75rem', borderRadius: '10px', background: 'rgba(6,182,212,0.15)', color: '#22d3ee' }}>
                <Briefcase size={24} />
              </div>
              <div>
                <h3>AI Resume Builder</h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>ATS Scoring & Keyword Optimization</span>
              </div>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Scan your resume against target Job Descriptions to maximize recruiter callbacks.</p>
          </Link>
        </div>
      </div>
    </div>
  );
};
