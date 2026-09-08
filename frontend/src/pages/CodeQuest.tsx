import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { BarChart3, Code2, ListChecks, Trophy } from 'lucide-react';
import api from '../services/api';
import '../styles/codequest.css';
import { ToastHost, useToasts } from '../components/codequest/ui';
import { ProblemsTab } from './codequest/ProblemsTab';
import { ProblemWorkspace } from './codequest/ProblemWorkspace';
import { ProgressTab } from './codequest/ProgressTab';
import { LeaderboardTab } from './codequest/LeaderboardTab';
import { EMPTY_FILTERS } from './codequest/types';
import type { Facets, Filters, Stats } from './codequest/types';

type TabKey = 'problems' | 'progress' | 'leaderboard';

const TABS: { key: TabKey; label: string; icon: React.ReactNode }[] = [
  { key: 'problems', label: 'Problems', icon: <ListChecks size={14} /> },
  { key: 'progress', label: 'My Progress', icon: <BarChart3 size={14} /> },
  { key: 'leaderboard', label: 'Leaderboard', icon: <Trophy size={14} /> },
];

const isTab = (value: string | null): value is TabKey =>
  value === 'problems' || value === 'progress' || value === 'leaderboard';

/** Filters live in the URL so a refresh (or a shared link) restores the view. */
const readFilters = (params: URLSearchParams): Filters => ({
  q: params.get('q') ?? '',
  difficulty: (params.get('difficulty') as Filters['difficulty']) || 'all',
  status: (params.get('status') as Filters['status']) || 'all',
  topic: params.get('topic') ?? '',
  pattern: params.get('pattern') ?? '',
  company: params.get('company') ?? '',
  sheet: params.get('sheet') ?? '',
});

export const CodeQuestPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const tabParam = searchParams.get('tab');
  const slug = searchParams.get('problem');
  const pageParam = Number(searchParams.get('page') || '1');

  const [tab, setTab] = useState<TabKey>(isTab(tabParam) ? tabParam : 'problems');
  const filters = useMemo(() => readFilters(searchParams), [searchParams]);
  const page = Number.isFinite(pageParam) && pageParam > 0 ? pageParam : 1;

  const [stats, setStats] = useState<Stats | null>(null);
  const [facets, setFacets] = useState<Facets | null>(null);
  const { toasts, push, dismiss } = useToasts();

  useEffect(() => {
    if (isTab(tabParam) && tabParam !== tab) setTab(tabParam);
  }, [tabParam]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadStats = useCallback(async () => {
    try {
      const { data } = await api.get<Stats>('/codequest/stats');
      setStats(data);
    } catch {
      // The tiles simply stay at zero; the list below still works.
    }
  }, []);

  useEffect(() => {
    loadStats();
    api
      .get<Facets>('/codequest/facets')
      .then(({ data }) => setFacets(data))
      .catch(() => undefined);
  }, [loadStats]);

  /** Writes a patch into the query string, dropping empty values. */
  const updateParams = useCallback(
    (patch: Record<string, string | number | null>) => {
      const next = new URLSearchParams(searchParams);
      Object.entries(patch).forEach(([key, value]) => {
        if (value === null || value === '' || value === 'all') next.delete(key);
        else next.set(key, String(value));
      });
      setSearchParams(next, { replace: true });
    },
    [searchParams, setSearchParams],
  );

  const selectTab = (next: TabKey) => {
    setTab(next);
    updateParams({ tab: next === 'problems' ? null : next, problem: null });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const openProblem = (nextSlug: string) => updateParams({ problem: nextSlug });
  const closeProblem = () => updateParams({ problem: null });

  return (
    <div className="cq">
      <header className="cq-hero">
        <div className="cq-hero-inner">
          <div className="cq-hero-head">
            <span className="cq-hero-badge">
              <Code2 size={20} />
            </span>
            <div>
              <h1>Code Quest</h1>
              <p>
                Sharpen your coding skills — solve problems, build streaks, and climb the leaderboard.
              </p>
            </div>
          </div>

          <nav className="cq-tabs" role="tablist" aria-label="Code Quest sections">
            {TABS.map((item) => (
              <button
                key={item.key}
                role="tab"
                aria-selected={tab === item.key}
                className={`cq-tab${tab === item.key ? ' is-active' : ''}`}
                onClick={() => selectTab(item.key)}
              >
                {item.icon}
                {item.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <div className="cq-body">
        {tab === 'problems' &&
          (slug ? (
            <ProblemWorkspace
              slug={slug}
              filters={filters}
              onBack={closeProblem}
              onOpenProblem={openProblem}
              onSolved={loadStats}
              notify={push}
            />
          ) : (
            <ProblemsTab
              stats={stats}
              facets={facets}
              filters={filters}
              onFiltersChange={(next) =>
                updateParams({
                  q: next.q,
                  difficulty: next.difficulty,
                  status: next.status,
                  topic: next.topic,
                  pattern: next.pattern,
                  company: next.company,
                  sheet: next.sheet,
                })
              }
              page={page}
              onPageChange={(next) => updateParams({ page: next === 1 ? null : next })}
              onOpenProblem={openProblem}
              notify={push}
            />
          ))}

        {tab === 'progress' && <ProgressTab notify={push} />}
        {tab === 'leaderboard' && <LeaderboardTab notify={push} />}
      </div>

      <ToastHost toasts={toasts} onDismiss={dismiss} />
    </div>
  );
};

export default CodeQuestPage;
