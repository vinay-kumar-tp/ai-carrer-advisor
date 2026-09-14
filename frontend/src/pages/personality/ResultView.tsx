
import { CheckCircle2, AlertTriangle, Users, FileDown, RotateCw, ShieldCheck, ShieldAlert } from 'lucide-react';
import type { AssessmentResult } from './types';
import { TRAIT_ORDER, TRAIT_TINT, LEVEL_COLOR } from './types';
import { openReport } from './report';
import { useAuth } from '../../context/AuthContext';

interface Props {
  result: AssessmentResult;
  onRetake: () => void;
}

export const ResultView: React.FC<Props> = ({ result, onRetake }) => {
  const { user } = useAuth();
  const meta = result.assessment_metadata;
  const insights = result.workplace_behavioral_insights || {};
  const flagged = result.compliance?.status === 'Flagged';

  const downloadReport = () => {
    openReport(result, user?.full_name || user?.email);
  };

  const timeLabel = meta.completion_time_seconds != null
    ? `${Math.floor(meta.completion_time_seconds / 60)}m ${meta.completion_time_seconds % 60}s`
    : null;

  return (
    <div className="pt-result">
      <div className="pt-result-head">
        <div>
          <span style={{ color: 'var(--accent-purple)', fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
            Big Five personality profile
          </span>
          <h2>Your OCEAN Profile</h2>
          <div className="pt-meta-row">
            <span>{meta.form === 'ipip120' ? 'IPIP-NEO-120' : meta.form === 'bfi44' ? 'BFI-44' : 'Assessment'}</span>
            <span>{meta.completed_questions}/{meta.total_questions} answered</span>
            {timeLabel && <span>{timeLabel}</span>}
            {result.completed_at && <span>{new Date(result.completed_at).toLocaleDateString()}</span>}
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
          <span className={`pt-compliance ${flagged ? 'flag' : 'pass'}`}>
            {flagged ? <ShieldAlert size={14} /> : <ShieldCheck size={14} />}
            Compliance: {result.compliance?.status || 'Passed'}
          </span>
        </div>
      </div>

      {flagged && result.compliance?.notes && (
        <div className="glass-card" style={{ borderLeft: '3px solid #ef4444', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          <strong style={{ color: '#fca5a5' }}>Response pattern flagged:</strong> {result.compliance.notes} Results may
          be less reliable — consider retaking with more varied, considered answers.
        </div>
      )}

      {/* Trait scores */}
      <div className="glass-card">
        <h3 style={{ marginTop: 0 }}>Trait scores</h3>
        {TRAIT_ORDER.map((t) => {
          const s = result.scores[t];
          if (!s) return null;
          return (
            <div className="pt-trait" key={t}>
              <div className="pt-trait-head">
                <span className="pt-trait-name">
                  <span className="pt-trait-dot" style={{ background: TRAIT_TINT[t] }} />
                  {s.label}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <span className="pt-level" style={{ background: `${LEVEL_COLOR[s.level]}22`, color: LEVEL_COLOR[s.level] }}>
                    {s.level}
                  </span>
                  <strong>{s.percentage}%</strong>
                </span>
              </div>
              <div className="pt-trait-bar">
                <div className="pt-trait-fill" style={{ width: `${s.percentage}%`, background: TRAIT_TINT[t] }} />
              </div>
              <div className="pt-trait-raw">Raw {s.raw_score} · range {s.min_score}–{s.max_score}</div>
            </div>
          );
        })}
      </div>

      {/* Workplace insights */}
      <div className="pt-insights">
        <div className="pt-insight-card good">
          <h4><CheckCircle2 size={15} color="#34d399" /> Key strengths</h4>
          <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
            {(insights.key_strengths || []).map((s, i) => <li key={i}>{s}</li>)}
            {(!insights.key_strengths || insights.key_strengths.length === 0) && (
              <li style={{ color: 'var(--text-muted)' }}>No standout strengths flagged.</li>
            )}
          </ul>
        </div>
        <div className="pt-insight-card warn">
          <h4><AlertTriangle size={15} color="#f59e0b" /> Potential challenges</h4>
          <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
            {(insights.potential_challenges || []).map((s, i) => <li key={i}>{s}</li>)}
          </ul>
        </div>
      </div>

      {insights.team_collaboration_style && (
        <div className="pt-team">
          <strong style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.35rem' }}>
            <Users size={15} color="var(--accent-secondary)" /> Team collaboration style
          </strong>
          {insights.team_collaboration_style}
        </div>
      )}

      <div style={{ display: 'flex', gap: '0.75rem' }}>
        <button className="btn btn-secondary" onClick={downloadReport}>
          <FileDown size={15} /> Download report
        </button>
        <button className="btn btn-primary" onClick={onRetake}>
          <RotateCw size={15} /> Retake assessment
        </button>
      </div>
    </div>
  );
};
