import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  Building2,
  Code2,
  Dices,
  Flame,
  Layers,
  ListChecks,
  RotateCcw,
  Search,
  Star,
  Target,
} from 'lucide-react';
import api from '../../services/api';
import {
  Chip,
  DifficultyBadge,
  EmptyState,
  FacetDropdown,
  Loading,
  Pager,
  PointsBadge,
  StatusBadge,
} from '../../components/codequest/ui';
import {
  EMPTY_FILTERS,
  filtersToParams,
} from './types';
import type {
  Difficulty,
  Facets,
  Filters,
  ProblemListResponse,
  Stats,
} from './types';

const PAGE_SIZE = 40;

/** Curated sets are surfaced above the raw competitive archives, like the reference. */
const PREP_SETS = [
  'Amazon OA', 'Blind 75', 'Coding Ninjas 400', 'GfG SDE Sheet', 'Google Interview', 'Grind 75',
  'HackWithInfy', 'LeetCode Top 100 Liked', 'LeetCode Top Interview 150', 'Love Babbar 450',
  'Microsoft Interview', 'NeetCode 150', 'TCS NQT', 'Wipro NLTH',
];

type Props = {
  stats: Stats | null;
  facets: Facets | null;
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
  page: number;
  onPageChange: (page: number) => void;
  onOpenProblem: (slug: string) => void;
  notify: (message: string, tone?: 'success' | 'error') => void;
};

export const ProblemsTab: React.FC<Props> = ({
  stats,
  facets,
  filters,
  onFiltersChange,
  page,
  onPageChange,
  onOpenProblem,
  notify,
}) => {
  const [data, setData] = useState<ProblemListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchDraft, setSearchDraft] = useState(filters.q);
  const [picking, setPicking] = useState(false);
  const requestId = useRef(0);

  // Keep the local input in sync when filters are reset from outside.
  useEffect(() => {
    setSearchDraft(filters.q);
  }, [filters.q]);

  // Debounce the search box so typing does not fire a request per keystroke.
  useEffect(() => {
    if (searchDraft === filters.q) return;
    const handle = window.setTimeout(() => {
      onFiltersChange({ ...filters, q: searchDraft });
      onPageChange(1);
    }, 350);
    return () => window.clearTimeout(handle);
  }, [searchDraft]); // eslint-disable-line react-hooks/exhaustive-deps

  const load = useCallback(async () => {
    const ticket = ++requestId.current;
    setLoading(true);
    setError(null);
    try {
      const { data: payload } = await api.get<ProblemListResponse>('/codequest/problems', {
        params: { ...filtersToParams(filters), page, page_size: PAGE_SIZE },
      });
      if (ticket === requestId.current) setData(payload);
    } catch (err: any) {
      if (ticket === requestId.current) {
        setError(err?.response?.data?.detail || 'Could not load problems.');
      }
    } finally {
      if (ticket === requestId.current) setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => {
    load();
  }, [load]);

  const pageCount = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  const setFilter = (patch: Partial<Filters>) => {
    onFiltersChange({ ...filters, ...patch });
    onPageChange(1);
  };

  const activeCount = useMemo(
    () =>
      [
        filters.difficulty !== 'all',
        filters.status !== 'all',
        !!filters.topic,
        !!filters.pattern,
        !!filters.company,
        !!filters.sheet,
        !!filters.q.trim(),
      ].filter(Boolean).length,
    [filters],
  );

  const pickRandom = async () => {
    setPicking(true);
    try {
      const { data: payload } = await api.get<{ slug: string }>('/codequest/problems/random', {
        params: filtersToParams(filters),
      });
      onOpenProblem(payload.slug);
    } catch (err: any) {
      notify(
        err?.response?.status === 404
          ? 'No problem matches the current filters.'
          : 'Could not pick a problem.',
        'error',
      );
    } finally {
      setPicking(false);
    }
  };

  return (
    <>
      {/* ── Stat tiles ── */}
      <div className="cq-stats">
        <div className="cq-stat">
          <div className="cq-stat-icon tone-blue">
            <Code2 size={18} />
          </div>
          <div>
            <div className="cq-stat-value">{(stats?.total_problems ?? 0).toLocaleString()}</div>
            <div className="cq-stat-label">Total problems</div>
          </div>
        </div>
        <div className="cq-stat">
          <div className="cq-stat-icon tone-green">
            <ListChecks size={18} />
          </div>
          <div>
            <div className="cq-stat-value">{(stats?.solved ?? 0).toLocaleString()}</div>
            <div className="cq-stat-label">Solved</div>
          </div>
        </div>
        <div className="cq-stat">
          <div className="cq-stat-icon tone-amber">
            <Star size={18} />
          </div>
          <div>
            <div className="cq-stat-value">{(stats?.points ?? 0).toLocaleString()}</div>
            <div className="cq-stat-label">Points</div>
          </div>
        </div>
        <div className="cq-stat">
          <div className="cq-stat-icon tone-red">
            <Flame size={18} />
          </div>
          <div>
            <div className="cq-stat-value">{stats?.streak_days ?? 0}d</div>
            <div className="cq-stat-label">Current streak</div>
          </div>
        </div>
      </div>

      {/* ── Filters ── */}
      <div className="cq-card">
        <div className="cq-card-head">
          <div>
            <h3 className="cq-card-title">Problem Set</h3>
            <div className="cq-card-sub">
              {(data?.total ?? stats?.total_problems ?? 0).toLocaleString()} problems to practice
              {activeCount > 0 && ` · ${activeCount} filter${activeCount === 1 ? '' : 's'} active`}
            </div>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {activeCount > 0 && (
              <button
                className="cq-btn cq-btn-ghost cq-btn-sm"
                onClick={() => {
                  onFiltersChange({ ...EMPTY_FILTERS });
                  onPageChange(1);
                }}
              >
                <RotateCcw size={13} /> Clear filters
              </button>
            )}
            <button className="cq-btn cq-btn-outline cq-btn-sm" onClick={pickRandom} disabled={picking}>
              <Dices size={14} /> {picking ? 'Picking...' : 'Pick One'}
            </button>
          </div>
        </div>

        <div className="cq-filters">
          <div className="cq-search">
            <Search size={16} color="#94a3b8" />
            <input
              value={searchDraft}
              onChange={(event) => setSearchDraft(event.target.value)}
              placeholder="Search problems by title..."
              aria-label="Search problems by title"
            />
            {searchDraft && (
              <button
                className="cq-btn-link"
                onClick={() => setSearchDraft('')}
                aria-label="Clear search"
              >
                Clear
              </button>
            )}
          </div>

          <div className="cq-filter-row">
            <div className="cq-pill-group">
              {(['all', 'easy', 'medium', 'hard'] as const).map((level) => (
                <button
                  key={level}
                  className={`cq-pill${filters.difficulty === level ? ' is-active' : ''}`}
                  onClick={() => setFilter({ difficulty: level })}
                >
                  {level !== 'all' && (
                    <span
                      className="cq-pill-dot"
                      style={{
                        background:
                          level === 'easy' ? '#16a34a' : level === 'medium' ? '#d97706' : '#dc2626',
                      }}
                    />
                  )}
                  {level === 'all' ? 'All' : level.charAt(0).toUpperCase() + level.slice(1)}
                </button>
              ))}
            </div>

            <div className="cq-divider-v" />

            <div className="cq-pill-group">
              {(['all', 'solved', 'unsolved'] as const).map((value) => (
                <button
                  key={value}
                  className={`cq-pill${filters.status === value ? ' is-active' : ''}`}
                  onClick={() => setFilter({ status: value })}
                >
                  {value === 'all' ? 'All' : value.charAt(0).toUpperCase() + value.slice(1)}
                </button>
              ))}
            </div>

            <div className="cq-divider-v" />

            <FacetDropdown
              label="Topic"
              icon={<Target size={13} />}
              options={facets?.topics ?? []}
              value={filters.topic}
              onChange={(topic) => setFilter({ topic })}
              allLabel="All topics"
            />
            <FacetDropdown
              label="Pattern"
              icon={<Layers size={13} />}
              options={facets?.patterns ?? []}
              value={filters.pattern}
              onChange={(pattern) => setFilter({ pattern })}
              allLabel="All patterns"
            />
            <FacetDropdown
              label="Company"
              icon={<Building2 size={13} />}
              options={facets?.companies ?? []}
              value={filters.company}
              onChange={(company) => setFilter({ company })}
              allLabel="All companies"
            />
            <FacetDropdown
              label="Sheet / Set"
              icon={<ListChecks size={13} />}
              options={facets?.sheets ?? []}
              value={filters.sheet}
              onChange={(sheet) => setFilter({ sheet })}
              allLabel="All sheets & sets"
              groupLabel="Prep sheets & company sets"
              groupNames={PREP_SETS}
            />
          </div>
        </div>
      </div>

      {/* ── Results ── */}
      <div className="cq-card">
        {error && <div className="cq-alert">{error}</div>}

        {loading && !data ? (
          <Loading label="Loading problems..." />
        ) : !data || data.items.length === 0 ? (
          <EmptyState
            title="No problems match these filters"
            text="Try clearing a filter or searching for a different title."
            actionLabel="Clear filters"
            onAction={() => {
              onFiltersChange({ ...EMPTY_FILTERS });
              onPageChange(1);
            }}
          />
        ) : (
          <>
            <div className="cq-list" style={loading ? { opacity: 0.55 } : undefined}>
              {data.items.map((item, index) => (
                <button
                  key={item.slug}
                  className="cq-row"
                  onClick={() => onOpenProblem(item.slug)}
                  aria-label={`Open ${item.title}`}
                >
                  <span className="cq-row-index">{data.showing_from + index}</span>

                  <span style={{ minWidth: 0 }}>
                    <span className="cq-row-title">
                      {item.title}
                      <DifficultyBadge level={item.difficulty as Difficulty} />
                    </span>
                    <span className="cq-row-tags">
                      {item.topics.slice(0, 2).map((topic) => (
                        <Chip key={topic}>{topic}</Chip>
                      ))}
                      {item.patterns.slice(0, 1).map((pattern) => (
                        <Chip key={pattern} tone="accent">
                          {pattern}
                        </Chip>
                      ))}
                      {item.companies.slice(0, 3).map((company) => (
                        <Chip key={company} tone="plain">
                          {company}
                        </Chip>
                      ))}
                      {item.companies.length > 3 && (
                        <Chip tone="plain">+{item.companies.length - 3} more</Chip>
                      )}
                    </span>
                  </span>

                  <span className="cq-row-right">
                    {item.acceptance !== null && (
                      <span style={{ fontSize: '0.76rem', color: '#94a3b8', fontWeight: 600 }}>
                        {item.acceptance}%
                      </span>
                    )}
                    <StatusBadge status={item.status} />
                    <PointsBadge points={item.points} />
                  </span>
                </button>
              ))}
            </div>

            <div className="cq-showing">
              <span>
                Showing <strong>{data.showing_from}</strong>–<strong>{data.showing_to}</strong> of{' '}
                <strong>{data.total.toLocaleString()}</strong>
              </span>
              <Pager page={data.page} pageCount={pageCount} onPage={onPageChange} />
            </div>
          </>
        )}
      </div>
    </>
  );
};
