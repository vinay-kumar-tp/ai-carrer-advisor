import React from 'react';
import { Info, CheckCircle2, AlertCircle, GraduationCap, MessageSquare, ArrowRight, RotateCw } from 'lucide-react';
import type { InterviewReport } from './types';

interface Props {
  report: InterviewReport;
  onPracticeAgain: () => void;
  onStartSame: () => void;
}

const scoreColor = (pct: number) => (pct >= 70 ? '#34d399' : pct >= 40 ? '#f59e0b' : '#ef4444');

const Bar: React.FC<{ label: string; value: number; max: number }> = ({ label, value, max }) => {
  const pct = max ? (value / max) * 100 : 0;
  return (
    <div className="iv-bar-row">
      <div className="iv-bar-label">
        <span>{label}</span>
        <span>{value}/{max}</span>
      </div>
      <div className="iv-bar-track">
        <div className="iv-bar-fill" style={{ width: `${pct}%`, background: scoreColor(pct) }} />
      </div>
    </div>
  );
};

const DIM_LABELS: Record<string, string> = {
  relevance: 'Relevance',
  domain_knowledge: 'Domain knowledge',
  articulation: 'Articulation',
  problem_solving: 'Problem solving',
  attitude: 'Attitude',
  learning_agility: 'Learning agility',
  analytical_thinking: 'Analytical thinking',
  confidence: 'Confidence',
  filler_control: 'Filler control',
  pace: 'Pace',
};

export const ReportStage: React.FC<Props> = ({ report, onPracticeAgain, onStartSame }) => {
  const b = report.breakdown;
  const meta = b.speech_quality.meta || {};

  return (
    <div className="iv-wrap iv-report">
      {/* Head */}
      <div className="iv-report-head">
        <div>
          <span className="iv-eyebrow">Mock interview performance report</span>
          <h2>{report.title}</h2>
          <div className="iv-report-meta">
            <span>{report.context_label}</span>
            {report.difficulty && <span>{report.difficulty} difficulty</span>}
            {report.created_at && <span>{new Date(report.created_at).toLocaleDateString()}</span>}
            {report.duration_min != null && <span>{report.duration_min} min</span>}
            {report.questions_spoken != null && <span>{report.questions_spoken} spoken</span>}
            <span>{report.questions_reviewed} questions reviewed</span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.6rem' }}>
          <button className="btn" onClick={onPracticeAgain}>Practice again <ArrowRight size={15} /></button>
        </div>
      </div>

      {/* Overview grid */}
      <div className="iv-report-grid">
        <div className="glass-card">
          <div className="iv-score-hero">
            <div className="iv-score-num" style={{ color: scoreColor(report.overall_score) }}>
              {report.overall_score}
            </div>
            <div className="iv-score-den">/100</div>
            <div className="iv-score-band">{report.band}</div>
          </div>
          <div className="iv-breakdown-mini">
            <h4>Score breakdown</h4>
            <Bar label="Response quality" value={b.response_quality.score} max={50} />
            <Bar label="Behavioural competency" value={b.behavioural_competency.score} max={30} />
            <Bar label="Speech quality" value={b.speech_quality.score} max={20} />
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <h3 style={{ marginTop: 0 }}>Overview</h3>
            <div className="iv-recruiter">
              <Info size={18} color="var(--accent-secondary)" style={{ flexShrink: 0, marginTop: 2 }} />
              <div>
                <strong style={{ display: 'block', marginBottom: '0.25rem' }}>Recruiter&apos;s perspective</strong>
                <span style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>{report.recruiter_perspective}</span>
              </div>
            </div>
          </div>

          <div className="iv-panel good">
            <div className="iv-panel-title"><CheckCircle2 size={16} color="#34d399" /> Strengths in progress</div>
            {report.strengths.map((s, i) => (
              <div key={i} style={{ fontSize: '0.86rem', padding: '0.35rem 0' }}>• {s}</div>
            ))}
          </div>

          <div className="iv-panel warn">
            <div className="iv-panel-title"><AlertCircle size={16} color="#ef4444" /> Areas for improvement</div>
            {report.areas_for_improvement.length === 0 && (
              <div style={{ fontSize: '0.86rem', color: 'var(--text-muted)' }}>No major gaps flagged. Keep practising.</div>
            )}
            {report.areas_for_improvement.map((a, i) => (
              <div className="iv-item" key={i}>
                <div className="iv-item-topic">{a.topic}</div>
                <div className="iv-item-detail">{a.detail}</div>
                {a.evidence_q && <span className="iv-evidence-tag">Evidence from Q{a.evidence_q}</span>}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Priorities */}
      {report.priorities.length > 0 && (
        <div className="glass-card">
          <div className="iv-panel-title"><GraduationCap size={18} color="var(--accent-purple)" /> Your next priorities</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 0 }}>
            Start with priority one. Open the rest when you&apos;re ready for more detail.
          </p>
          {report.priorities.map((p, i) => (
            <div className="iv-priority" key={i}>
              <div className="iv-priority-num">{i + 1}</div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong>{p.topic}</strong>
                  {p.evidence_q && <span className="iv-evidence-tag">Q{p.evidence_q}</span>}
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0.35rem 0' }}>{p.summary}</div>
                {p.what_to_study?.length > 0 && (
                  <>
                    <span className="iv-hint" style={{ fontWeight: 700 }}>WHAT TO STUDY</span>
                    <ul className="iv-study-list">
                      {p.what_to_study.map((w, j) => <li key={j}>{w}</li>)}
                    </ul>
                  </>
                )}
                {p.practice_drill && <div className="iv-drill">💡 Practice drill — {p.practice_drill}</div>}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detailed score analysis */}
      <div className="glass-card">
        <div className="iv-panel-title"><MessageSquare size={18} color="var(--accent-purple)" /> Detailed score analysis</div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 0 }}>
          Your response, behavioural, and speech parameters.
        </p>
        <div className="iv-dims">
          <div className="iv-dim-group">
            <h4>Response quality <span style={{ color: scoreColor((b.response_quality.score / 50) * 100) }}>{b.response_quality.score}/50</span></h4>
            {Object.entries(b.response_quality.dimensions).map(([k, v]) => (
              <Bar key={k} label={DIM_LABELS[k] || k} value={v} max={10} />
            ))}
          </div>
          <div className="iv-dim-group">
            <h4>Behavioural competency <span style={{ color: scoreColor((b.behavioural_competency.score / 30) * 100) }}>{b.behavioural_competency.score}/30</span></h4>
            {Object.entries(b.behavioural_competency.dimensions).map(([k, v]) => (
              <Bar key={k} label={DIM_LABELS[k] || k} value={v} max={10} />
            ))}
          </div>
          <div className="iv-dim-group">
            <h4>Speech quality <span style={{ color: scoreColor((b.speech_quality.score / 20) * 100) }}>{b.speech_quality.score}/20</span></h4>
            {Object.entries(b.speech_quality.dimensions).map(([k, v]) => (
              <Bar key={k} label={DIM_LABELS[k] || k} value={v} max={10} />
            ))}
            {(meta.filler_pct != null || meta.words_per_min != null) && (
              <div className="iv-hint" style={{ marginTop: '0.5rem' }}>
                {meta.filler_pct != null && <>Fillers: {meta.filler_pct}% · </>}
                {meta.words_per_min != null && <>{meta.words_per_min} words/min</>}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Question-by-question evidence */}
      <div className="glass-card">
        <div className="iv-panel-title"><MessageSquare size={18} color="var(--accent-purple)" /> Question-by-question evidence</div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 0 }}>
          Your answers, dimension scores, and coaching evidence for each prompt.
        </p>
        {report.questions.map((q) => (
          <div className="iv-qbq-item" key={q.index}>
            <div className="iv-qbq-q">
              <span className="iv-qbq-badge">Q{q.index}</span>
              <span style={{ fontSize: '0.9rem' }}>{q.question}</span>
              <span className={`iv-qbq-score ${q.is_warmup ? 'warmup' : q.score >= 20 ? 'good' : ''}`}>
                {q.is_warmup ? 'Warm-up · Not scored' : `${q.score}/30`}
              </span>
            </div>
            <div className="iv-qbq-answer">
              <span className="lbl">YOUR ANSWER</span>
              <p>{q.answer ? q.answer : <em style={{ color: 'var(--text-muted)' }}>No answer was captured for this question.</em>}</p>
              {q.evidence && <div className="iv-qbq-evidence">{q.evidence}</div>}
            </div>
          </div>
        ))}
      </div>

      {/* Next practice CTA */}
      <div className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
        <div>
          <span className="iv-eyebrow">Next practice</span>
          <div style={{ fontWeight: 700, marginTop: '0.25rem' }}>
            {report.priorities[0] ? `Apply your first priority: ${report.priorities[0].topic}` : 'Run another attempt while the feedback is fresh'}
          </div>
          <div style={{ fontSize: '0.83rem', color: 'var(--text-muted)' }}>
            Use the drills above, then run another attempt while the feedback is fresh.
          </div>
        </div>
        <button className="btn btn-primary" onClick={onStartSame}>
          <RotateCw size={15} /> Start same interview
        </button>
      </div>
    </div>
  );
};
