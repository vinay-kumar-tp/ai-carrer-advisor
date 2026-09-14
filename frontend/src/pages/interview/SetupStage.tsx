import React, { useState } from 'react';
import { Bot, ArrowRight } from 'lucide-react';
import type { InterviewConfig, StartPayload, SourceTab, JobSubSource } from './types';

interface Props {
  config: InterviewConfig;
  starting: boolean;
  error: string | null;
  onStart: (payload: StartPayload) => void;
  onViewAttempts: () => void;
}

const DIFFICULTY_LABELS: Record<string, string> = {
  mixed: 'Mixed',
  easy: 'Easy',
  medium: 'Medium',
  hard: 'Hard',
};
const MIX_LABELS: Record<string, string> = {
  technical_behavioral: 'Technical + Behavioral',
  behavioral: 'Behavioral',
};

export const SetupStage: React.FC<Props> = ({ config, starting, error, onStart, onViewAttempts }) => {
  const [tab, setTab] = useState<SourceTab>('job');
  const [jobSub, setJobSub] = useState<JobSubSource>('standard');
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [skill, setSkill] = useState('');
  const [resumeId, setResumeId] = useState('');
  const [difficulty, setDifficulty] = useState('mixed');
  const [mix, setMix] = useState('technical_behavioral');

  const canStart = (() => {
    if (tab === 'job') {
      if (jobSub === 'jd') return jobDescription.trim().length >= 50;
      return !!jobTitle;
    }
    if (tab === 'skill') return !!skill;
    if (tab === 'resume') return !!resumeId;
    return false;
  })();

  const handleStart = () => {
    const payload: StartPayload = { source: tab, difficulty, question_mix: mix };
    if (tab === 'job') {
      if (jobSub === 'jd') payload.job_description = jobDescription.trim();
      payload.job_title = jobTitle || undefined;
    } else if (tab === 'skill') {
      payload.skill = skill;
    } else if (tab === 'resume') {
      payload.resume_id = resumeId;
    }
    onStart(payload);
  };

  return (
    <div className="iv-wrap">
      <div className="iv-hero">
        <div>
          <h2>Become a smart applicant &amp; excel in placements with AI Mock Interviews</h2>
          <p>The more you practice, the closer you get to acing your dream job.</p>
        </div>
        <span className="iv-ready-pill">
          <Bot size={15} /> You&apos;re Job Ready!
        </span>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ margin: 0 }}>Start mock interview based on:</h3>
        <button className="btn" onClick={onViewAttempts} style={{ fontSize: '0.85rem' }}>
          View My Attempts →
        </button>
      </div>

      <div className="glass-card">
        <div className="iv-tabs">
          {(['job', 'skill', 'resume'] as SourceTab[]).map((t) => (
            <button key={t} className={`iv-tab ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>
              {t === 'job' ? 'Job' : t === 'skill' ? 'Skills' : 'Resume'}
            </button>
          ))}
        </div>

        {/* ── JOB TAB ── */}
        {tab === 'job' && (
          <div>
            <label className="label" style={{ display: 'block', marginBottom: '0.5rem' }}>Select Job from</label>
            <div className="iv-source-row">
              {([
                ['foundation', 'Featured Roles'],
                ['standard', 'Standard Job Titles'],
                ['jd', 'Add Job Description'],
              ] as [JobSubSource, string][]).map(([key, label]) => (
                <div
                  key={key}
                  className={`iv-source-chip ${jobSub === key ? 'active' : ''}`}
                  onClick={() => setJobSub(key)}
                >
                  <span className="iv-radio" /> {label}
                </div>
              ))}
            </div>

            {jobSub !== 'jd' ? (
              <div className="iv-field">
                <label className="label">Select Job Title</label>
                <select className="input-field" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)}>
                  <option value="">Select a job role</option>
                  {config.job_titles.map((jt) => (
                    <option key={jt} value={jt}>{jt}</option>
                  ))}
                </select>
              </div>
            ) : (
              <>
                <div className="iv-field">
                  <label className="label">Job Title <span className="iv-hint">(Optional)</span></label>
                  <input
                    className="input-field"
                    placeholder="e.g. Backend Engineer"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                  />
                </div>
                <div className="iv-field">
                  <label className="label">Job Description</label>
                  <textarea
                    className="input-field"
                    rows={5}
                    maxLength={50000}
                    placeholder="Paste at least 50 characters of the job description."
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                  />
                  <div className="iv-char-count">{jobDescription.length}/50,000 characters</div>
                </div>
              </>
            )}
          </div>
        )}

        {/* ── SKILLS TAB ── */}
        {tab === 'skill' && (
          <div className="iv-field">
            <label className="label" style={{ textAlign: 'center', display: 'block' }}>Select any one skill</label>
            <select className="input-field" value={skill} onChange={(e) => setSkill(e.target.value)}>
              <option value="">Select skill</option>
              {config.skills.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        )}

        {/* ── RESUME TAB ── */}
        {tab === 'resume' && (
          <div className="iv-field">
            <label className="label" style={{ textAlign: 'center', display: 'block' }}>Choose your resume</label>
            {config.resumes.length === 0 ? (
              <p className="iv-hint" style={{ textAlign: 'center' }}>
                No resumes found. Add one from the AI Resume Builder first.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {config.resumes.map((r) => (
                  <div
                    key={r.id}
                    className={`iv-source-chip ${resumeId === r.id ? 'active' : ''}`}
                    onClick={() => setResumeId(r.id)}
                  >
                    <span className="iv-radio" /> {r.name}
                    {r.is_primary && <span className="iv-hint" style={{ marginLeft: 'auto' }}>Primary</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Difficulty + mix ── */}
        <div className="iv-settings-row">
          <div className="iv-option-group">
            <span className="label">Difficulty level</span>
            <div className="iv-pills">
              {config.difficulty_levels.map((d) => (
                <button key={d} className={`iv-pill ${difficulty === d ? 'active' : ''}`} onClick={() => setDifficulty(d)}>
                  {DIFFICULTY_LABELS[d] || d}
                </button>
              ))}
            </div>
          </div>
          <div className="iv-option-group">
            <span className="label">Question mix</span>
            <div className="iv-pills">
              {config.question_mixes.map((m) => (
                <button key={m} className={`iv-pill ${mix === m ? 'active' : ''}`} onClick={() => setMix(m)}>
                  {MIX_LABELS[m] || m}
                </button>
              ))}
            </div>
          </div>
        </div>

        {error && <p style={{ color: '#fca5a5', fontSize: '0.85rem', marginTop: '1rem' }}>{error}</p>}

        <button
          className="btn btn-primary"
          style={{ marginTop: '1.5rem', width: '100%' }}
          disabled={!canStart || starting}
          onClick={handleStart}
        >
          {starting ? 'Preparing your interview…' : (<>Start mock interview <ArrowRight size={16} /></>)}
        </button>
      </div>
    </div>
  );
};
