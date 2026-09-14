import { useEffect, useState } from 'react';
import { Sparkles, X, Copy, CheckCircle2, AlertTriangle, Wand2, Lightbulb } from 'lucide-react';
import api from '../../services/api';
import { Loading } from '../../components/codequest/ui';

interface Job {
  id: string;
  title: string;
  company: string;
  required_skills: string[];
}

interface OptimizeReport {
  match_score: number;
  matched_keywords: string[];
  missing_keywords: string[];
  summary: string;
  strengths: string[];
  gaps: string[];
  tailored_summary: string;
  rewritten_bullets: string[];
  section_suggestions: string[];
  engine: string;
  job?: { title: string };
}

interface Props {
  docId: string;
  docLabel: string;
  onClose: () => void;
  notify: (msg: string, tone?: 'success' | 'error') => void;
}

export const OptimizeModal: React.FC<Props> = ({ docId, docLabel, onClose, notify }) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<string | null>(null);
  const [title, setTitle] = useState('');
  const [jd, setJd] = useState('');
  const [running, setRunning] = useState(false);
  const [report, setReport] = useState<OptimizeReport | null>(null);

  useEffect(() => {
    api.get<Job[]>('/jobs/').then(({ data }) => setJobs(data)).catch(() => setJobs([]));
  }, []);

  const run = async () => {
    const body: any = {};
    if (selectedJob) body.job_id = selectedJob;
    else if (title.trim() || jd.trim()) {
      body.job_title = title.trim();
      body.job_description = jd.trim();
    } else {
      notify('Pick a job or enter a title / description first.', 'error');
      return;
    }
    setRunning(true);
    try {
      const { data } = await api.post<OptimizeReport>(`/documents/${docId}/optimize`, body);
      setReport(data);
    } catch (e: any) {
      notify(e?.response?.data?.detail || 'Optimization failed.', 'error');
    } finally {
      setRunning(false);
    }
  };

  const copy = (text: string) => {
    navigator.clipboard?.writeText(text).then(
      () => notify('Copied to clipboard'),
      () => notify('Copy failed', 'error'),
    );
  };

  const R = 40;
  const C = 2 * Math.PI * R;
  const scoreColor = (s: number) => (s >= 70 ? '#34d399' : s >= 45 ? '#f59e0b' : '#ef4444');

  return (
    <div className="iv-modal-overlay" onClick={onClose}>
      <div className="iv-modal" style={{ maxWidth: 620 }} onClick={(e) => e.stopPropagation()}>
        <button className="iv-modal-close" onClick={onClose}><X size={16} /></button>
        <span className="iv-eyebrow" style={{ color: '#a855f7' }}><Sparkles size={12} /> Optimize for a job</span>
        <h2 style={{ margin: '0.35rem 0 0.25rem', fontSize: '1.25rem' }}>Tailor “{docLabel}”</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.86rem', marginTop: 0 }}>
          Pick a job from the board, or paste a title and description. AI analyzes your resume against it.
        </p>

        {!report ? (
          <>
            {jobs.length > 0 && (
              <>
                <label className="label" style={{ fontSize: '0.8rem', fontWeight: 600 }}>Choose a job</label>
                <div className="dv-opt-jobs">
                  {jobs.map((j) => (
                    <div
                      key={j.id}
                      className={`dv-job-row ${selectedJob === j.id ? 'sel' : ''}`}
                      onClick={() => { setSelectedJob(j.id); setTitle(''); setJd(''); }}
                    >
                      <div>
                        <div>{j.title}</div>
                        <div className="dv-job-company">{j.company}</div>
                      </div>
                      {selectedJob === j.id && <CheckCircle2 size={16} color="var(--accent-primary)" />}
                    </div>
                  ))}
                </div>
                <div className="dv-or">— or enter one manually —</div>
              </>
            )}

            <label className="label" style={{ fontSize: '0.8rem', fontWeight: 600 }}>Job title</label>
            <input
              className="input-field"
              placeholder="e.g. Backend Python Engineer"
              value={title}
              onChange={(e) => { setTitle(e.target.value); setSelectedJob(null); }}
              style={{ marginBottom: '0.6rem' }}
            />
            <label className="label" style={{ fontSize: '0.8rem', fontWeight: 600 }}>Job description <span style={{ color: 'var(--text-muted)' }}>(optional)</span></label>
            <textarea
              className="input-field"
              rows={4}
              placeholder="Paste the job description for a sharper analysis…"
              value={jd}
              onChange={(e) => { setJd(e.target.value); setSelectedJob(null); }}
            />

            <div className="iv-modal-actions" style={{ marginTop: '1rem' }}>
              <button className="btn" onClick={onClose}>Cancel</button>
              <button className="btn btn-primary" onClick={run} disabled={running}>
                {running ? 'Analyzing…' : (<><Wand2 size={15} /> Optimize</>)}
              </button>
            </div>
            {running && <Loading label="AI is analyzing your resume…" />}
          </>
        ) : (
          <div className="dv-opt-result">
            <div className="dv-opt-head">
              <div className="dv-ring">
                <svg width="96" height="96">
                  <circle cx="48" cy="48" r={R} fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="8" />
                  <circle cx="48" cy="48" r={R} fill="none" stroke={scoreColor(report.match_score)}
                    strokeWidth="8" strokeLinecap="round"
                    strokeDasharray={`${(report.match_score / 100) * C} ${C}`} />
                </svg>
                <div className="dv-ring-num" style={{ color: scoreColor(report.match_score) }}>
                  {report.match_score}%
                </div>
              </div>
              <div>
                <strong>Match score</strong>
                <div className="dv-opt-summary">{report.summary}</div>
              </div>
            </div>

            {(report.matched_keywords.length > 0 || report.missing_keywords.length > 0) && (
              <div>
                <strong style={{ fontSize: '0.82rem' }}>Keywords</strong>
                <div className="dv-kw">
                  {report.matched_keywords.map((k) => <span key={k} className="dv-chip match">✓ {k}</span>)}
                  {report.missing_keywords.map((k) => <span key={k} className="dv-chip miss">+ {k}</span>)}
                </div>
              </div>
            )}

            {report.tailored_summary && (
              <div>
                <strong style={{ fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.4rem' }}>
                  <Wand2 size={14} color="#a855f7" /> Tailored summary
                  <button className="dv-copy-btn" onClick={() => copy(report.tailored_summary)}><Copy size={12} /></button>
                </strong>
                <div className="dv-tailored">{report.tailored_summary}</div>
              </div>
            )}

            {report.rewritten_bullets.length > 0 && (
              <div className="dv-opt-section">
                <h4><Wand2 size={14} color="#a855f7" /> Suggested bullet points</h4>
                {report.rewritten_bullets.map((b, i) => (
                  <div className="dv-copy-row" key={i}>
                    <p>{b}</p>
                    <button className="dv-copy-btn" onClick={() => copy(b)}><Copy size={12} /></button>
                  </div>
                ))}
              </div>
            )}

            {report.strengths.length > 0 && (
              <div className="dv-opt-section">
                <h4><CheckCircle2 size={14} color="#34d399" /> Strengths</h4>
                <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
                  {report.strengths.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}

            {report.gaps.length > 0 && (
              <div className="dv-opt-section">
                <h4><AlertTriangle size={14} color="#f59e0b" /> Gaps to close</h4>
                <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
                  {report.gaps.map((g, i) => <li key={i}>{g}</li>)}
                </ul>
              </div>
            )}

            {report.section_suggestions.length > 0 && (
              <div className="dv-opt-section">
                <h4><Lightbulb size={14} color="#60a5fa" /> Structure suggestions</h4>
                <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
                  {report.section_suggestions.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}

            <div className="dv-engine-note">
              {report.engine === 'ai' ? 'Generated with AI analysis.' : 'Generated with keyword/ATS analysis (add an AI key for deeper insight).'}
            </div>

            <div className="iv-modal-actions">
              <button className="btn" onClick={() => setReport(null)}>Try another job</button>
              <button className="btn btn-primary" onClick={onClose}>Done</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
