import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Clock,
  History,
  Play,
  RotateCcw,
  Send,
  Terminal,
} from 'lucide-react';
import api from '../../services/api';
import { CodeEditor } from '../../components/codequest/CodeEditor';
import { JudgeResults } from '../../components/codequest/JudgeResults';
import { ProblemStatement } from '../../components/codequest/ProblemStatement';
import {
  Chip,
  DifficultyBadge,
  Loading,
  PointsBadge,
  StatusBadge,
} from '../../components/codequest/ui';
import { VERDICT_LABEL, filtersToParams } from './types';
import type {
  Filters,
  Language,
  ProblemDetail,
  RunResult,
  SubmissionItem,
  SubmitResult,
} from './types';

type Props = {
  slug: string;
  filters: Filters;
  onBack: () => void;
  onOpenProblem: (slug: string) => void;
  onSolved: () => void;
  notify: (message: string, tone?: 'success' | 'error') => void;
};

const LANGUAGE_LABELS: Record<Language, string> = {
  python: 'Python',
  javascript: 'JavaScript',
  cpp: 'C++',
  java: 'Java',
};

export const ProblemWorkspace: React.FC<Props> = ({
  slug,
  filters,
  onBack,
  onOpenProblem,
  onSolved,
  notify,
}) => {
  const [problem, setProblem] = useState<ProblemDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [language, setLanguage] = useState<Language>('python');
  const [code, setCode] = useState('');
  const [customInput, setCustomInput] = useState('');

  const [running, setRunning] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [submitResult, setSubmitResult] = useState<SubmitResult | null>(null);

  const [hints, setHints] = useState<string[]>([]);
  const [hintCount, setHintCount] = useState(0);
  const [revealing, setRevealing] = useState(false);

  const [history, setHistory] = useState<SubmissionItem[] | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  // Per-language buffers so switching language does not discard work.
  const buffers = useRef<Record<string, string>>({});
  const saveTimer = useRef<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    setRunResult(null);
    setSubmitResult(null);
    setShowHistory(false);
    setHistory(null);
    buffers.current = {};
    try {
      const { data } = await api.get<ProblemDetail>(`/codequest/problems/${slug}`, {
        params: filtersToParams(filters),
      });
      setProblem(data);
      setHints(data.revealed_hints);
      setHintCount(data.hint_count);

      const initialLanguage = (data.last_language || 'python') as Language;
      const startFrom = data.draft ?? data.starter_code[initialLanguage] ?? '';
      setLanguage(initialLanguage);
      setCode(startFrom);
      buffers.current[initialLanguage] = startFrom;
    } catch (err: any) {
      setLoadError(err?.response?.data?.detail || 'Could not load this problem.');
    } finally {
      setLoading(false);
    }
  }, [slug, filters]);

  useEffect(() => {
    load();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [load]);

  // Debounced draft save so a refresh keeps the work in progress.
  useEffect(() => {
    if (!problem || !code) return;
    if (saveTimer.current) window.clearTimeout(saveTimer.current);
    saveTimer.current = window.setTimeout(() => {
      api.put(`/codequest/problems/${problem.slug}/draft`, { code, language }).catch(() => undefined);
    }, 1200);
    return () => {
      if (saveTimer.current) window.clearTimeout(saveTimer.current);
    };
  }, [code, language, problem]);

  const switchLanguage = (next: Language) => {
    if (!problem) return;
    buffers.current[language] = code;
    setLanguage(next);
    setCode(buffers.current[next] ?? problem.starter_code[next] ?? '');
    setRunResult(null);
    setSubmitResult(null);
  };

  const resetToStarter = () => {
    if (!problem) return;
    const starter = problem.starter_code[language] ?? '';
    setCode(starter);
    buffers.current[language] = starter;
    notify('Editor reset to the starter template');
  };

  const run = async () => {
    if (!problem || running || submitting) return;
    setRunning(true);
    setSubmitResult(null);
    try {
      const { data } = await api.post<RunResult>(`/codequest/problems/${problem.slug}/run`, {
        code,
        language,
        custom_input: customInput.trim() ? customInput : null,
      });
      setRunResult(data);
    } catch (err: any) {
      notify(err?.response?.data?.detail || 'Run failed.', 'error');
    } finally {
      setRunning(false);
    }
  };

  const loadHistory = useCallback(async () => {
    if (!problem) return;
    try {
      const { data } = await api.get<SubmissionItem[]>(
        `/codequest/problems/${problem.slug}/submissions`,
      );
      setHistory(data);
    } catch {
      setHistory([]);
    }
  }, [problem]);

  const submit = async () => {
    if (!problem || running || submitting) return;
    setSubmitting(true);
    setRunResult(null);
    try {
      const { data } = await api.post<SubmitResult>(`/codequest/problems/${problem.slug}/submit`, {
        code,
        language,
      });
      setSubmitResult(data);
      if (data.verdict === 'accepted') {
        notify(
          data.first_solve
            ? `Accepted! +${data.points_awarded} points`
            : 'Accepted again — already counted',
        );
        setProblem((current) => (current ? { ...current, status: 'solved' } : current));
        onSolved();
      } else {
        notify(VERDICT_LABEL[data.verdict], 'error');
        setProblem((current) =>
          current && current.status !== 'solved' ? { ...current, status: 'attempted' } : current,
        );
      }
      if (showHistory) loadHistory();
    } catch (err: any) {
      notify(err?.response?.data?.detail || 'Submission failed.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const revealHint = async () => {
    if (!problem || revealing) return;
    setRevealing(true);
    try {
      const { data } = await api.post<{ revealed_hints: string[]; hint_count: number }>(
        `/codequest/problems/${problem.slug}/hint`,
      );
      setHints(data.revealed_hints);
      setHintCount(data.hint_count);
    } catch {
      notify('Could not reveal the hint.', 'error');
    } finally {
      setRevealing(false);
    }
  };

  if (loading) return <Loading label="Loading problem..." />;

  if (loadError || !problem) {
    return (
      <div className="cq-card">
        <div className="cq-alert">{loadError || 'Problem not found.'}</div>
        <button className="cq-btn cq-btn-ghost cq-btn-sm" onClick={onBack}>
          <ArrowLeft size={14} /> Back to problems
        </button>
      </div>
    );
  }

  return (
    <>
      <div className="cq-ws-top">
        <div className="cq-ws-title">
          <button className="cq-iconbtn" onClick={onBack} aria-label="Back to problem list">
            <ArrowLeft size={15} />
          </button>
          <h2>{problem.title}</h2>
          <DifficultyBadge level={problem.difficulty} />
          {problem.topics.slice(0, 1).map((topic) => (
            <Chip key={topic}>{topic}</Chip>
          ))}
          <PointsBadge points={problem.points} />
          <StatusBadge status={problem.status} />
        </div>

        <div className="cq-ws-nav">
          <button
            className="cq-btn cq-btn-ghost cq-btn-sm"
            onClick={() => problem.prev_slug && onOpenProblem(problem.prev_slug)}
            disabled={!problem.prev_slug}
          >
            <ChevronLeft size={13} /> Prev
          </button>
          {problem.position !== null && problem.total_in_filter ? (
            <span>
              {problem.position} of {problem.total_in_filter}
            </span>
          ) : null}
          <button
            className="cq-btn cq-btn-ghost cq-btn-sm"
            onClick={() => problem.next_slug && onOpenProblem(problem.next_slug)}
            disabled={!problem.next_slug}
          >
            Next <ChevronRight size={13} />
          </button>
        </div>
      </div>

      {problem.companies.length > 0 && (
        <div className="cq-askedat">
          <span className="cq-askedat-label">Asked at</span>
          {problem.companies.map((company) => (
            <Chip key={company} tone="plain">
              {company}
            </Chip>
          ))}
        </div>
      )}

      <div className="cq-ws-grid">
        <div>
          <ProblemStatement
            problem={problem}
            hints={hints}
            hintCount={hintCount}
            revealing={revealing}
            onRevealHint={revealHint}
          />

          {problem.related.length > 0 && (
            <div className="cq-card">
              <div className="cq-card-head" style={{ marginBottom: '0.6rem' }}>
                <h3 className="cq-card-title">Related problems</h3>
              </div>
              <div className="cq-related">
                {problem.related.map((related) => (
                  <button
                    key={related.slug}
                    className="cq-related-card"
                    onClick={() => onOpenProblem(related.slug)}
                  >
                    <span style={{ minWidth: 0 }}>
                      <span className="cq-related-name">{related.title}</span>
                      <span className="cq-related-meta">
                        <DifficultyBadge level={related.difficulty} />
                        {related.patterns.slice(0, 1).map((pattern) => (
                          <Chip key={pattern} tone="accent">
                            {pattern}
                          </Chip>
                        ))}
                      </span>
                    </span>
                    <ChevronRight size={15} color="#94a3b8" />
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        <div>
          <div className="cq-editor-panel">
            <div className="cq-editor-bar">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <select
                  className="cq-lang-select"
                  value={language}
                  onChange={(event) => switchLanguage(event.target.value as Language)}
                  aria-label="Language"
                >
                  {problem.languages.map((key) => (
                    <option key={key} value={key}>
                      {LANGUAGE_LABELS[key] ?? key}
                    </option>
                  ))}
                </select>
                <button
                  className="cq-btn cq-btn-sm"
                  style={{ background: '#1c2740', color: '#a9b6d6' }}
                  onClick={resetToStarter}
                  title="Reset to the starter template"
                  aria-label="Reset to the starter template"
                >
                  <RotateCcw size={13} />
                </button>
                <span
                  style={{
                    fontSize: '0.72rem',
                    color: '#6f7d9f',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.25rem',
                  }}
                >
                  <Clock size={11} /> {problem.time_limit_ms / 1000}s limit
                </span>
              </div>

              <div className="cq-editor-actions">
                <button
                  className="cq-btn cq-btn-run cq-btn-sm"
                  onClick={run}
                  disabled={running || submitting}
                >
                  <Play size={13} /> {running ? 'Running...' : 'Run'}
                </button>
                <button
                  className="cq-btn cq-btn-submit cq-btn-sm"
                  onClick={submit}
                  disabled={running || submitting}
                >
                  <Send size={13} /> {submitting ? 'Judging...' : 'Submit'}
                </button>
              </div>
            </div>

            <CodeEditor
              value={code}
              language={language}
              onChange={setCode}
              onRun={run}
              onSubmit={submit}
              readOnly={running || submitting}
            />

            <div className="cq-io">
              <div className="cq-io-label">
                <Terminal size={11} /> Custom input (optional)
              </div>
              <textarea
                value={customInput}
                onChange={(event) => setCustomInput(event.target.value)}
                placeholder="Enter custom test input here. Run uses this instead of the samples."
                aria-label="Custom input"
              />
            </div>

            <JudgeResults runResult={runResult} submitResult={submitResult} />
          </div>

          <div className="cq-card" style={{ marginTop: '1rem' }}>
            <div className="cq-card-head" style={{ marginBottom: showHistory ? '0.7rem' : 0 }}>
              <h3 className="cq-card-title">
                Your submissions {problem.attempts > 0 && `(${problem.attempts})`}
              </h3>
              <button
                className="cq-btn cq-btn-ghost cq-btn-sm"
                onClick={() => {
                  const next = !showHistory;
                  setShowHistory(next);
                  if (next && history === null) loadHistory();
                }}
              >
                <History size={13} /> {showHistory ? 'Hide' : 'Show'}
              </button>
            </div>

            {showHistory &&
              (history === null ? (
                <Loading label="Loading submissions..." />
              ) : history.length === 0 ? (
                <div className="cq-empty-text" style={{ padding: '0.5rem 0' }}>
                  No submissions yet for this problem.
                </div>
              ) : (
                <div className="cq-table-wrap">
                  <table className="cq-table">
                    <thead>
                      <tr>
                        <th>When</th>
                        <th>Language</th>
                        <th>Verdict</th>
                        <th>Tests</th>
                        <th>Runtime</th>
                      </tr>
                    </thead>
                    <tbody>
                      {history.map((row) => (
                        <tr key={row.id}>
                          <td>{row.created_at ? new Date(row.created_at).toLocaleString() : '--'}</td>
                          <td>{LANGUAGE_LABELS[row.language as Language] ?? row.language}</td>
                          <td
                            style={{
                              fontWeight: 700,
                              color: row.verdict === 'accepted' ? '#16a34a' : '#dc2626',
                            }}
                          >
                            {VERDICT_LABEL[row.verdict] ?? row.verdict}
                          </td>
                          <td>
                            {row.passed}/{row.total}
                          </td>
                          <td>{row.runtime_ms ?? '--'} ms</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}
          </div>
        </div>
      </div>
    </>
  );
};
