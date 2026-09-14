import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Search, BellRing, BellOff } from 'lucide-react';
import api from '../services/api';
import '../styles/jobboard.css';
import { Loading, EmptyState, Pager, ToastHost, useToasts } from '../components/codequest/ui';
import { FilterSidebar } from './jobboard/FilterSidebar';
import { JobCardItem } from './jobboard/JobCard';
import { JobDetailDrawer } from './jobboard/JobDetailDrawer';
import { ApplyModal } from './jobboard/ApplyModal';
import { NotificationBell } from './jobboard/NotificationBell';
import type { Facets, Filters, JobCard, JobDetail } from './jobboard/types';
import { EMPTY_FILTERS } from './jobboard/types';

const PAGE_SIZE = 8;

const TABS = [
  { key: 'all', label: 'All Roles' },
  { key: 'internship', label: 'Internships' },
  { key: 'full-time', label: 'Full Time' },
  { key: 'contract', label: 'Contract' },
];

export const JobBoardPage: React.FC = () => {
  const { toasts, push, dismiss } = useToasts();

  const [jobs, setJobs] = useState<JobCard[]>([]);
  const [total, setTotal] = useState(0);
  const [facets, setFacets] = useState<Facets | null>(null);
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [tab, setTab] = useState('all');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const [alertsOn, setAlertsOn] = useState(true);
  const [notifKey, setNotifKey] = useState(0);

  const [activeId, setActiveId] = useState<string | null>(null);
  const [detail, setDetail] = useState<JobDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [showApply, setShowApply] = useState(false);

  const params = useMemo(() => {
    const p: Record<string, any> = { skip: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE, sort: filters.sort };
    if (filters.keyword) p.keyword = filters.keyword;
    if (tab !== 'all') p.job_type = tab;
    else if (filters.job_type) p.job_type = filters.job_type;
    if (filters.role) p.role = filters.role;
    if (filters.location) p.location = filters.location;
    if (filters.industry) p.industry = filters.industry;
    if (filters.employer) p.employer = filters.employer;
    if (filters.employment_mode) p.employment_mode = filters.employment_mode;
    if (filters.source_portal) p.source_portal = filters.source_portal;
    if (filters.status) p.status = filters.status;
    if (filters.min_experience) p.min_experience = filters.min_experience;
    if (filters.max_experience) p.max_experience = filters.max_experience;
    if (filters.posted_in) p.posted_in = filters.posted_in;
    if (filters.min_ctc) p.min_ctc = filters.min_ctc;
    if (filters.max_ctc) p.max_ctc = filters.max_ctc;
    if (filters.min_stipend) p.min_stipend = filters.min_stipend;
    if (filters.max_stipend) p.max_stipend = filters.max_stipend;
    return p;
  }, [filters, tab, page]);

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/jobs/', { params });
      setJobs(res.data.items);
      setTotal(res.data.total);
    } catch {
      push('Could not load jobs', 'error');
    } finally {
      setLoading(false);
    }
  }, [params, push]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  useEffect(() => {
    api.get('/jobs/facets').then((r) => setFacets(r.data)).catch(() => {});
    api.get('/jobs/alerts/status').then((r) => setAlertsOn(r.data.enabled)).catch(() => {});
  }, []);

  const patchFilters = (patch: Partial<Filters>) => {
    setPage(1);
    setFilters((f) => ({ ...f, ...patch }));
  };

  const clearFilters = () => {
    setPage(1);
    setFilters((f) => ({ ...EMPTY_FILTERS, keyword: f.keyword, sort: f.sort }));
  };

  const toggleAlerts = async () => {
    try {
      const res = await api.put('/jobs/alerts', { enabled: !alertsOn });
      setAlertsOn(res.data.enabled);
      setNotifKey((k) => k + 1);
      push(res.data.enabled ? 'Job alerts turned ON' : 'Job alerts turned OFF');
    } catch {
      push('Could not update alerts', 'error');
    }
  };

  const openJob = async (id: string) => {
    setActiveId(id);
    setDetail(null);
    setDetailLoading(true);
    try {
      const res = await api.get(`/jobs/${id}`);
      setDetail(res.data);
    } catch {
      push('Could not load job', 'error');
      setActiveId(null);
    } finally {
      setDetailLoading(false);
    }
  };

  const closeJob = () => {
    setActiveId(null);
    setDetail(null);
    setShowApply(false);
  };

  const submitApplication = async (answers: Record<string, any>) => {
    if (!detail) return;
    await api.post(`/jobs/${detail.id}/apply`, { answers });
    push('Application submitted', 'success');
    setShowApply(false);
    setNotifKey((k) => k + 1);
    // Refresh detail + list applied state.
    const res = await api.get(`/jobs/${detail.id}`);
    setDetail(res.data);
    fetchJobs();
  };

  const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="jb-wrap">
      <ToastHost toasts={toasts} onDismiss={dismiss} />

      <div className="jb-head">
        <div>
          <h2>Job Board</h2>
          <p>Openings posted by companies across 20 leading portals. Eligibility is checked automatically against your profile.</p>
        </div>
        <div className="jb-head-actions">
          <button className={`jb-alert-toggle${alertsOn ? ' on' : ''}`} onClick={toggleAlerts} title="Toggle job alerts">
            {alertsOn ? <BellRing size={15} /> : <BellOff size={15} />}
            Job alerts {alertsOn ? 'ON' : 'OFF'}
            <span className="jb-switch" />
          </button>
          <NotificationBell refreshKey={notifKey} />
        </div>
      </div>

      <div className="jb-tabs">
        {TABS.map((t) => (
          <button
            key={t.key}
            className={`jb-tab${tab === t.key ? ' active' : ''}`}
            onClick={() => {
              setTab(t.key);
              setPage(1);
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="glass-card jb-searchbar">
        <div className="jb-search-input">
          <Search size={18} />
          <input
            className="input-field"
            placeholder="Search by title, company or skill..."
            value={filters.keyword}
            onChange={(e) => patchFilters({ keyword: e.target.value })}
          />
        </div>
        <select
          className="jb-select jb-sort"
          value={filters.sort}
          onChange={(e) => patchFilters({ sort: e.target.value })}
        >
          <option value="recent">Sort: Date posted</option>
          <option value="ctc_high">Sort: CTC (high to low)</option>
          <option value="ctc_low">Sort: CTC (low to high)</option>
        </select>
      </div>

      <div className="jb-body">
        <FilterSidebar facets={facets} filters={filters} onChange={patchFilters} onClear={clearFilters} />

        <div>
          <div className="jb-result-meta">
            <span>{total} job{total !== 1 ? 's' : ''} found</span>
            <span>
              Page {page} of {pageCount}
            </span>
          </div>

          {loading ? (
            <Loading label="Loading jobs..." />
          ) : jobs.length === 0 ? (
            <EmptyState
              title="No jobs match your filters"
              text="Try clearing some filters or widening your search."
              actionLabel="Clear filters"
              onAction={clearFilters}
            />
          ) : (
            <>
              <div className="jb-list">
                {jobs.map((j) => (
                  <JobCardItem key={j.id} job={j} onOpen={openJob} />
                ))}
              </div>
              <div style={{ marginTop: '1rem' }}>
                <Pager page={page} pageCount={pageCount} onPage={setPage} />
              </div>
            </>
          )}
        </div>
      </div>

      {activeId && (
        <JobDetailDrawer
          job={detail}
          loading={detailLoading}
          onClose={closeJob}
          onApply={() => setShowApply(true)}
        />
      )}

      {showApply && detail && (
        <ApplyModal job={detail} onClose={() => setShowApply(false)} onSubmit={submitApplication} />
      )}
    </div>
  );
};
