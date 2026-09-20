/**
 * AI Resume Builder — the full-screen editor for one resume.
 *
 * Three columns:
 *  - left   : template picker + section toggles (drives what the PDF renders)
 *  - centre : live HTML preview straight from the backend renderer
 *  - right  : Analyzer (scored categories) / Tailor to Job (match + suggestions)
 *
 * The preview, PDF and analyzer all read the same server-side snapshot, so what
 * you see here is exactly what downloads.
 */
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ArrowLeft,
  Briefcase,
  Check,
  ChevronDown,
  Download,
  Layout,
  List,
  Loader2,
  Phone,
  RefreshCw,
  SpellCheck2,
  Sparkles,
  Target,
  TrendingUp,
  X,
} from 'lucide-react';
import api from '../../services/api';
import '../../styles/resume-builder.css';
import { Loading } from '../../components/profile/ui';
import { errorMessage } from './useProfileData';
import type {
  AnalyzerCategory,
  ResumeAnalysis,
  ResumeDetail,
  TailorSuggestion,
  TailoringRun,
} from './types';

type Props = {
  resumeId: string;
  onBack: () => void;
  notify: (message: string, tone?: 'success' | 'error') => void;
  /** Called after anything that changes the library (new tailored copy, score change). */
  onChanged: () => void;
  /** Which right-hand pane to land on. */
  initialPane?: 'analyzer' | 'tailor';
};

type JobOption = { id: string; title: string; company: string };

const CATEGORY_ICON: Record<string, React.ComponentType<{ size?: number }>> = {
  layout: Layout,
  briefcase: Briefcase,
  phone: Phone,
  'trending-up': TrendingUp,
  list: List,
  'spell-check': SpellCheck2,
};

const scoreTone = (pct: number) => (pct >= 0.75 ? 'good' : pct >= 0.45 ? 'warn' : 'bad');

/** Categories use different scales, so normalise before colouring. */
const categoryPct = (category: AnalyzerCategory) => {
  if (category.score !== null && category.total) return category.score / category.total;
  return category.count ? category.passed / category.count : 0;
};

const saveBlob = (blob: Blob, filename: string) => {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
};

export const ResumeBuilderPanel: React.FC<Props> = ({
  resumeId,
  onBack,
  notify,
  onChanged,
  initialPane = 'analyzer',
}) => {
  const [detail, setDetail] = useState<ResumeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [previewHtml, setPreviewHtml] = useState('');
  const [previewBusy, setPreviewBusy] = useState(false);
  const [savingDesign, setSavingDesign] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const [pane, setPane] = useState<'analyzer' | 'tailor'>(initialPane);
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [openCategory, setOpenCategory] = useState<string | null>('structure');

  const [jobs, setJobs] = useState<JobOption[]>([]);
  const [jobMode, setJobMode] = useState<'board' | 'paste'>('board');
  const [jobId, setJobId] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [run, setRun] = useState<TailoringRun | null>(null);
  const [tailorBusy, setTailorBusy] = useState(false);
  const [tailorError, setTailorError] = useState<string | null>(null);

  const [decisions, setDecisions] = useState<Record<string, boolean>>({});
  const [details, setDetails] = useState<Record<string, string>>({});
  const [applyBusy, setApplyBusy] = useState(false);
  const [asCopy, setAsCopy] = useState(true);

  /* ── Load ─────────────────────────────────────────────── */

  const loadDetail = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get<ResumeDetail>(`/profile/resumes/${resumeId}`);
      setDetail(data);
      setAnalysis(data.analysis ?? null);
      if (data.tailoring?.suggestions) {
        setRun({
          job: { title: data.tailoring.title, description: data.tailoring.description },
          match: data.tailoring.match,
          suggestions: data.tailoring.suggestions,
        });
        setJobId(data.tailoring.job_id ?? '');
      }
    } catch (error) {
      notify(errorMessage(error, 'Could not open this resume.'), 'error');
    } finally {
      setLoading(false);
    }
  }, [resumeId, notify]);

  useEffect(() => {
    loadDetail();
  }, [loadDetail]);

  const loadPreview = useCallback(
    async (template?: string) => {
      setPreviewBusy(true);
      try {
        const { data } = await api.get(`/profile/resumes/${resumeId}/preview`, {
          params: template ? { template } : undefined,
          responseType: 'text',
          transformResponse: [(raw) => raw],
        });
        setPreviewHtml(typeof data === 'string' ? data : String(data));
      } catch (error) {
        notify(errorMessage(error, 'Preview failed to render.'), 'error');
      } finally {
        setPreviewBusy(false);
      }
    },
    [resumeId, notify],
  );

  useEffect(() => {
    if (detail) loadPreview();
    // Re-render whenever the persisted design changes.
  }, [detail?.template, detail?.sections?.join(','), loadPreview, detail]);

  useEffect(() => {
    api
      .get('/jobs/')
      .then(({ data }) =>
        setJobs((data || []).map((job: any) => ({ id: job.id, title: job.title, company: job.company }))),
      )
      .catch(() => setJobs([]));
  }, []);

  /* ── Design (template + sections) ─────────────────────── */

  const saveDesign = async (patch: { template?: string; sections?: string[] }) => {
    if (!detail) return;
    setSavingDesign(true);
    try {
      const { data } = await api.put(`/profile/resumes/${resumeId}/design`, patch);
      setDetail((current) =>
        current
          ? { ...current, template: data.template, sections: data.sections, ats_score: data.ats_score }
          : current,
      );
      setAnalysis(data.analysis ?? null);
      onChanged();
    } catch (error) {
      notify(errorMessage(error, 'Could not save that change.'), 'error');
    } finally {
      setSavingDesign(false);
    }
  };

  const activeSections = useMemo(() => new Set(detail?.sections ?? []), [detail?.sections]);

  const toggleSection = (key: string) => {
    if (!detail) return;
    const next = new Set(activeSections);
    if (next.has(key)) next.delete(key);
    else next.add(key);
    saveDesign({ sections: Array.from(next) });
  };

  /* ── Actions ──────────────────────────────────────────── */

  const runAnalyzer = async () => {
    setAnalyzing(true);
    try {
      const { data } = await api.post(`/profile/resumes/${resumeId}/analyze`);
      setAnalysis({ overall_score: data.overall_score, categories: data.categories });
      setDetail((current) => (current ? { ...current, ats_score: data.resume.ats_score } : current));
      notify('Resume analyzed');
      onChanged();
    } catch (error) {
      notify(errorMessage(error, 'Analysis failed.'), 'error');
    } finally {
      setAnalyzing(false);
    }
  };

  const refreshFromProfile = async () => {
    setRefreshing(true);
    try {
      const { data } = await api.post(`/profile/resumes/${resumeId}/refresh`);
      setDetail((current) => (current ? { ...current, content: data.content, ats_score: data.ats_score } : current));
      setAnalysis(data.analysis ?? null);
      await loadPreview();
      notify('Pulled the latest data from your profile');
      onChanged();
    } catch (error) {
      notify(errorMessage(error, 'Refresh failed.'), 'error');
    } finally {
      setRefreshing(false);
    }
  };

  const download = async () => {
    setDownloading(true);
    try {
      const { data } = await api.get(`/profile/resumes/${resumeId}/download`, { responseType: 'blob' });
      const name = detail?.name || 'resume';
      saveBlob(data as Blob, /\.\w{2,4}$/.test(name) ? name : `${name}.pdf`);
    } catch (error) {
      notify(errorMessage(error, 'Download failed.'), 'error');
    } finally {
      setDownloading(false);
    }
  };

  const runTailoring = async () => {
    setTailorError(null);
    if (jobMode === 'board' && !jobId) {
      setTailorError('Pick a job from the board, or paste a description instead.');
      return;
    }
    if (jobMode === 'paste' && !jobTitle.trim() && !jobDescription.trim()) {
      setTailorError('Add a job title or paste the job description.');
      return;
    }
    setTailorBusy(true);
    try {
      const body =
        jobMode === 'board'
          ? { job_id: jobId }
          : { job_title: jobTitle.trim(), job_description: jobDescription.trim() };
      const { data } = await api.post<TailoringRun>(`/profile/resumes/${resumeId}/tailor-preview`, body);
      setRun({ job: data.job, match: data.match, suggestions: data.suggestions });
      // Default every suggestion to accepted so the common path is one click.
      setDecisions(Object.fromEntries(data.suggestions.map((s) => [s.id, true])));
      setDetails({});
      notify(`${data.suggestions.length} suggestion${data.suggestions.length === 1 ? '' : 's'} ready to review`);
    } catch (error) {
      setTailorError(errorMessage(error, 'Tailoring failed.'));
    } finally {
      setTailorBusy(false);
    }
  };

  const applySuggestions = async () => {
    if (!run) return;
    const payload = run.suggestions.map((s) => ({
      suggestion_id: s.id,
      accepted: decisions[s.id] ?? false,
      user_detail: details[s.id]?.trim() || null,
    }));
    if (!payload.some((d) => d.accepted)) {
      setTailorError('Accept at least one suggestion to apply.');
      return;
    }
    setApplyBusy(true);
    setTailorError(null);
    try {
      const { data } = await api.post(`/profile/resumes/${resumeId}/apply-suggestions`, {
        decisions: payload,
        as_copy: asCopy,
      });
      notify(
        asCopy
          ? `Applied ${data.applied} change(s) to a new tailored copy`
          : `Applied ${data.applied} change(s) to this resume`,
      );
      onChanged();
      if (asCopy) {
        onBack();
      } else {
        await loadDetail();
        await loadPreview();
      }
    } catch (error) {
      setTailorError(errorMessage(error, 'Could not apply the suggestions.'));
    } finally {
      setApplyBusy(false);
    }
  };

  if (loading) return <Loading label="Opening the resume builder..." />;
  if (!detail) return null;

  const acceptedCount = run ? run.suggestions.filter((s) => decisions[s.id]).length : 0;

  return (
    <div className="rb">
      {/* ── Top bar ── */}
      <header className="rb-top">
        <button className="mp-btn mp-btn-ghost mp-btn-sm" onClick={onBack}>
          <ArrowLeft size={13} /> Back to library
        </button>
        <div className="rb-top-title">
          <h3>{detail.name}</h3>
          <span className="rb-top-meta">
            {detail.template || 'Template'} · {detail.sections.length} section
            {detail.sections.length === 1 ? '' : 's'}
            {detail.analysis_score !== null && ` · score ${detail.analysis_score}/100`}
          </span>
        </div>
        <div className="rb-top-actions">
          <button className="mp-btn mp-btn-ghost mp-btn-sm" onClick={refreshFromProfile} disabled={refreshing}>
            {refreshing ? <Loader2 size={13} className="mp-spin" /> : <RefreshCw size={13} />} Sync profile
          </button>
          <button className="mp-btn mp-btn-primary mp-btn-sm" onClick={download} disabled={downloading}>
            {downloading ? <Loader2 size={13} className="mp-spin" /> : <Download size={13} />} Download PDF
          </button>
        </div>
      </header>

      <div className="rb-grid">
        {/* ── Left: design ── */}
        <aside className="rb-side">
          <div className="rb-side-block">
            <div className="rb-side-title">Template</div>
            <div className="rb-templates">
              {detail.templates.map((tpl) => (
                <button
                  key={tpl.id}
                  className={`rb-tpl${detail.template === tpl.id ? ' is-active' : ''}`}
                  onClick={() => saveDesign({ template: tpl.id })}
                  disabled={savingDesign}
                  aria-pressed={detail.template === tpl.id}
                  title={`${tpl.id} — ${tpl.layout} layout`}
                >
                  <span className="rb-tpl-art" style={{ ['--tpl-accent' as string]: tpl.accent }}>
                    <span className="rb-tpl-bar" />
                    <span className="rb-tpl-line" />
                    <span className="rb-tpl-line short" />
                    <span className="rb-tpl-line" />
                  </span>
                  <span className="rb-tpl-name">{tpl.id}</span>
                  {detail.template === tpl.id && (
                    <span className="rb-tpl-check">
                      <Check size={11} />
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>

          <div className="rb-side-block">
            <div className="rb-side-title">Sections</div>
            <p className="rb-side-hint">
              Toggle what appears in the PDF. Empty sections are disabled — add the data in your profile first.
            </p>
            <ul className="rb-sections">
              {detail.section_catalogue.map((section) => {
                const count = detail.section_counts[section.key] ?? 0;
                const on = activeSections.has(section.key);
                const empty = count === 0;
                return (
                  <li key={section.key}>
                    <button
                      className={`rb-section${on ? ' is-on' : ''}${empty ? ' is-empty' : ''}`}
                      onClick={() => !empty && toggleSection(section.key)}
                      disabled={empty || savingDesign}
                      aria-pressed={on}
                    >
                      <span className={`rb-switch${on ? ' is-on' : ''}`} aria-hidden="true">
                        <span className="rb-switch-dot" />
                      </span>
                      <span className="rb-section-label">{section.label}</span>
                      <span className="rb-section-count">{empty ? '--' : String(count).padStart(2, '0')}</span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        </aside>

        {/* ── Centre: preview ── */}
        <main className="rb-preview-wrap">
          <div className="rb-preview-head">
            <span>Live preview</span>
            {previewBusy && (
              <span className="rb-preview-busy">
                <Loader2 size={12} className="mp-spin" /> rendering
              </span>
            )}
          </div>
          <div className="rb-preview">
            <iframe title={`Preview of ${detail.name}`} srcDoc={previewHtml} />
          </div>
        </main>

        {/* ── Right: analyzer / tailor ── */}
        <aside className="rb-panel">
          <div className="rb-tabs" role="tablist">
            <button
              role="tab"
              aria-selected={pane === 'analyzer'}
              className={`rb-tab${pane === 'analyzer' ? ' is-active' : ''}`}
              onClick={() => setPane('analyzer')}
            >
              <Sparkles size={13} /> AI Analyzer
            </button>
            <button
              role="tab"
              aria-selected={pane === 'tailor'}
              className={`rb-tab${pane === 'tailor' ? ' is-active' : ''}`}
              onClick={() => setPane('tailor')}
            >
              <Target size={13} /> Tailor to Job
            </button>
          </div>

          {pane === 'analyzer' ? (
            <div className="rb-pane">
              {analysis ? (
                <>
                  <div className={`rb-score tone-${scoreTone(analysis.overall_score / 100)}`}>
                    <div className="rb-score-num">{analysis.overall_score}</div>
                    <div className="rb-score-of">/ 100 overall</div>
                    <div className="mp-progress-track" style={{ marginTop: '0.5rem' }}>
                      <div className="mp-progress-fill" style={{ width: `${analysis.overall_score}%` }} />
                    </div>
                  </div>

                  <div className="rb-cats">
                    {analysis.categories.map((category) => {
                      const Icon = CATEGORY_ICON[category.icon] ?? Layout;
                      const pct = categoryPct(category);
                      const open = openCategory === category.key;
                      return (
                        <div key={category.key} className={`rb-cat tone-${scoreTone(pct)}`}>
                          <button
                            className="rb-cat-head"
                            onClick={() => setOpenCategory(open ? null : category.key)}
                            aria-expanded={open}
                          >
                            <span className="rb-cat-icon">
                              <Icon size={13} />
                            </span>
                            <span className="rb-cat-label">{category.label}</span>
                            <span className="rb-cat-score">
                              {category.score !== null && category.total
                                ? `${category.score}/${category.total}`
                                : `${category.passed}/${category.count}`}
                            </span>
                            <ChevronDown size={13} className={`rb-cat-chev${open ? ' is-open' : ''}`} />
                          </button>
                          {open && (
                            <ul className="rb-checks">
                              {category.checks.map((check, index) => (
                                <li key={index} className={`rb-check is-${check.status}`}>
                                  <span className="rb-check-mark">
                                    {check.status === 'pass' ? <Check size={11} /> : <X size={11} />}
                                  </span>
                                  <span>{check.message || 'Looks good.'}</span>
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  <button className="mp-btn mp-btn-outline mp-btn-sm rb-wide" onClick={runAnalyzer} disabled={analyzing}>
                    {analyzing ? <Loader2 size={13} className="mp-spin" /> : <RefreshCw size={13} />} Re-run analysis
                  </button>
                </>
              ) : (
                <div className="rb-empty">
                  <Sparkles size={22} />
                  <p>Run the analyzer to score structure, contact info, chronology, bullets and spelling.</p>
                  <button className="mp-btn mp-btn-primary mp-btn-sm" onClick={runAnalyzer} disabled={analyzing}>
                    {analyzing ? <Loader2 size={13} className="mp-spin" /> : <Sparkles size={13} />} Analyze resume
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="rb-pane">
              {/* Job source */}
              <div className="rb-jobpick">
                <div className="rb-seg">
                  <button
                    className={`rb-seg-btn${jobMode === 'board' ? ' is-active' : ''}`}
                    onClick={() => setJobMode('board')}
                  >
                    From job board
                  </button>
                  <button
                    className={`rb-seg-btn${jobMode === 'paste' ? ' is-active' : ''}`}
                    onClick={() => setJobMode('paste')}
                  >
                    Paste a JD
                  </button>
                </div>

                {jobMode === 'board' ? (
                  jobs.length ? (
                    <select className="mp-select" value={jobId} onChange={(e) => setJobId(e.target.value)}>
                      <option value="">Select a job...</option>
                      {jobs.map((job) => (
                        <option key={job.id} value={job.id}>
                          {job.title} — {job.company}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <p className="rb-side-hint">No jobs on the board yet. Paste a description instead.</p>
                  )
                ) : (
                  <>
                    <input
                      className="mp-input"
                      placeholder="Job title (e.g. Senior Python Engineer)"
                      value={jobTitle}
                      onChange={(e) => setJobTitle(e.target.value)}
                      aria-label="Job title"
                    />
                    <textarea
                      className="mp-input rb-jd"
                      rows={5}
                      placeholder="Paste the job description here..."
                      value={jobDescription}
                      onChange={(e) => setJobDescription(e.target.value)}
                      aria-label="Job description"
                    />
                  </>
                )}

                <button className="mp-btn mp-btn-primary mp-btn-sm rb-wide" onClick={runTailoring} disabled={tailorBusy}>
                  {tailorBusy ? <Loader2 size={13} className="mp-spin" /> : <Target size={13} />}
                  {tailorBusy ? 'Analyzing the match...' : 'Analyze match'}
                </button>
                {tailorError && <div className="rb-error">{tailorError}</div>}
              </div>

              {run && (
                <>
                  <div className="rb-match">
                    <div className={`rb-score tone-${scoreTone(run.match.overall / 100)}`}>
                      <div className="rb-score-num">{run.match.overall}%</div>
                      <div className="rb-score-of">match{run.job.title ? ` · ${run.job.title}` : ''}</div>
                    </div>
                    <div className="rb-bars">
                      {([
                        ['Hard skills', run.match.hard_skills],
                        ['Soft skills', run.match.soft_skills],
                        ['Title match', run.match.title_match],
                      ] as const).map(([label, value]) => (
                        <div key={label} className="rb-bar">
                          <span className="rb-bar-label">{label}</span>
                          <div className="mp-progress-track">
                            <div
                              className="mp-progress-fill"
                              style={{
                                width: `${value}%`,
                                background: value >= 75 ? '#22c55e' : value >= 45 ? '#f0921f' : '#ef4444',
                              }}
                            />
                          </div>
                          <span className="rb-bar-val">{value}%</span>
                        </div>
                      ))}
                    </div>

                    {run.match.keyword_gaps.hard_skills.length > 0 && (
                      <div className="rb-gaps">
                        <div className="mp-field-label">Missing keywords</div>
                        <div className="mp-chips">
                          {run.match.keyword_gaps.hard_skills.map((word) => (
                            <span className="mp-chip is-accent" key={word}>
                              {word}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {run.match.matched.length > 0 && (
                      <div className="rb-gaps">
                        <div className="mp-field-label">Already matched</div>
                        <div className="mp-chips">
                          {run.match.matched.map((word) => (
                            <span className="mp-chip" key={word}>
                              {word}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="rb-sugg-head">
                    <span className="mp-field-label">
                      Suggestions ({acceptedCount}/{run.suggestions.length} accepted)
                    </span>
                    <div className="rb-sugg-bulk">
                      <button
                        className="mp-btn-link"
                        onClick={() => setDecisions(Object.fromEntries(run.suggestions.map((s) => [s.id, true])))}
                      >
                        Accept all
                      </button>
                      <button
                        className="mp-btn-link"
                        onClick={() => setDecisions(Object.fromEntries(run.suggestions.map((s) => [s.id, false])))}
                      >
                        Reject all
                      </button>
                    </div>
                  </div>

                  <div className="rb-suggs">
                    {run.suggestions.map((suggestion) => (
                      <SuggestionCard
                        key={suggestion.id}
                        suggestion={suggestion}
                        accepted={decisions[suggestion.id] ?? false}
                        detailValue={details[suggestion.id] ?? ''}
                        onToggle={(value) => setDecisions((d) => ({ ...d, [suggestion.id]: value }))}
                        onDetail={(value) => setDetails((d) => ({ ...d, [suggestion.id]: value }))}
                      />
                    ))}
                  </div>

                  <label className="rb-copy">
                    <input type="checkbox" checked={asCopy} onChange={(e) => setAsCopy(e.target.checked)} />
                    <span>
                      Save as a new tailored copy
                      <em>{asCopy ? ' — this resume stays untouched' : ' — edits this resume in place'}</em>
                    </span>
                  </label>

                  <button
                    className="mp-btn mp-btn-primary mp-btn-sm rb-wide"
                    onClick={applySuggestions}
                    disabled={applyBusy || acceptedCount === 0}
                  >
                    {applyBusy ? <Loader2 size={13} className="mp-spin" /> : <Check size={13} />}
                    {applyBusy ? 'Applying...' : `Apply ${acceptedCount} change${acceptedCount === 1 ? '' : 's'}`}
                  </button>
                </>
              )}
            </div>
          )}
        </aside>
      </div>
    </div>
  );
};

/* ── Suggestion card ──────────────────────────────────────── */

const SuggestionCard: React.FC<{
  suggestion: TailorSuggestion;
  accepted: boolean;
  detailValue: string;
  onToggle: (value: boolean) => void;
  onDetail: (value: string) => void;
}> = ({ suggestion, accepted, detailValue, onToggle, onDetail }) => {
  const isKeywords = suggestion.type === 'skills';
  return (
    <div className={`rb-sugg${accepted ? ' is-accepted' : ''}`}>
      <div className="rb-sugg-top">
        <span className="rb-sugg-tag">{suggestion.section}</span>
        <span className="rb-sugg-kind">{suggestion.kind}</span>
        <div className="rb-sugg-acts">
          <button
            className={`rb-sugg-btn is-yes${accepted ? ' is-on' : ''}`}
            onClick={() => onToggle(true)}
            aria-pressed={accepted}
            title="Accept"
          >
            <Check size={12} /> Accept
          </button>
          <button
            className={`rb-sugg-btn is-no${!accepted ? ' is-on' : ''}`}
            onClick={() => onToggle(false)}
            aria-pressed={!accepted}
            title="Reject"
          >
            <X size={12} /> Reject
          </button>
        </div>
      </div>

      {suggestion.original && suggestion.original !== 'empty' && (
        <div className="rb-sugg-block">
          <span className="rb-sugg-lbl">Current</span>
          <p className="rb-sugg-old">{suggestion.original}</p>
        </div>
      )}

      <div className="rb-sugg-block">
        <span className="rb-sugg-lbl">Suggested</span>
        {isKeywords ? (
          <div className="mp-chips">
            {(suggestion.proposed_add ?? []).map((word) => (
              <span className="mp-chip is-accent" key={word}>
                {word}
              </span>
            ))}
          </div>
        ) : (
          <p className="rb-sugg-new">
            {suggestion.proposed && suggestion.proposed !== 'empty'
              ? suggestion.proposed
              : 'Needs your input below.'}
          </p>
        )}
      </div>

      {suggestion.needs_detail && (
        <div className="rb-sugg-block">
          <span className="rb-sugg-lbl">{suggestion.detail_prompt || 'Add the missing detail'}</span>
          <textarea
            className="mp-input"
            rows={2}
            value={detailValue}
            placeholder="Only include things you can genuinely back up."
            onChange={(e) => onDetail(e.target.value)}
            aria-label={suggestion.detail_prompt || 'Additional detail'}
          />
        </div>
      )}

      {suggestion.rationale && <p className="rb-sugg-why">{suggestion.rationale}</p>}
    </div>
  );
};
