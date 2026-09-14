import React, { useEffect, useState } from 'react';
import { Loading } from '../../components/codequest/ui';
import api from '../../services/api';
import type { ProgressData } from './types';
import { SECTION_TINT } from './types';

const band = (score: number | null) => {
  if (score === null) return 'Not enough evidence';
  if (score >= 75) return 'Drive-ready';
  if (score >= 60) return 'Strong';
  if (score >= 40) return 'Developing';
  return 'Needs foundation';
};

const color = (score: number | null) => {
  if (score === null) return 'var(--text-muted)';
  if (score >= 60) return '#34d399';
  if (score >= 40) return '#f59e0b';
  return '#ef4444';
};

export const ProgressTab: React.FC = () => {
  const [data, setData] = useState<ProgressData | null>(null);

  useEffect(() => {
    api.get<ProgressData>('/aptitude/progress').then(({ data }) => setData(data)).catch(() => setData(null));
  }, []);

  if (!data) return <Loading label="Loading progress…" />;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div className="aq-prog-grid">
        <div className="glass-card">
          <div className="aq-gauge">
            <div className="aq-gauge-num" style={{ color: color(data.overall_score) }}>
              {data.overall_score ?? '—'}
            </div>
            <div className="aq-gauge-den">/ 100</div>
            <div className="aq-gauge-label">{band(data.overall_score)}</div>
          </div>
          <div className="aq-stat-row" style={{ justifyContent: 'space-around' }}>
            <div className="aq-stat"><b>{data.total_solved}</b><span>solved</span></div>
            <div className="aq-stat"><b>{data.assessments_taken}</b><span>attempts</span></div>
            <div className="aq-stat"><b>{data.total_questions}</b><span>in bank</span></div>
          </div>
        </div>

        <div className="glass-card">
          <h3 style={{ marginTop: 0 }}>Where you stand</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 0 }}>
            Four sections on one 0–100 scale. A section with too little evidence says so rather than
            showing a number we can&apos;t defend.
          </p>
          {data.sections.map((s) => (
            <div className="aq-sec-bar" key={s.key}>
              <div className="aq-sec-bar-head">
                <span className="aq-sec-bar-name">
                  <span className="aq-section-dot" style={{ background: SECTION_TINT[s.key] }} />
                  {s.label}
                </span>
                <span style={{ color: color(s.score), fontWeight: 700, fontSize: '0.9rem' }}>
                  {s.enough_evidence ? s.score : 'Not enough evidence'}
                </span>
              </div>
              <div className="aq-bar-track">
                <div className="aq-bar-fill" style={{ width: `${s.score ?? 0}%`, background: color(s.score) }} />
              </div>
              <div className="aq-sec-sub">
                {s.attempted > 0
                  ? `${s.accuracy}% accuracy · ${s.coverage}% coverage · ${s.topics_touched}/${s.total_topics} topics`
                  : 'No questions answered yet'}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-card" style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
        Section score blends first-attempt accuracy (70%) and coverage (30%). Answer at least 5
        questions in a section to unlock its score — this keeps the number honest.
      </div>
    </div>
  );
};
