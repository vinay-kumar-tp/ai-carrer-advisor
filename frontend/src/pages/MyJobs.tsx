import React, { useEffect, useMemo, useState } from 'react';
import { MapPin, Briefcase, Clock, ExternalLink } from 'lucide-react';
import api from '../services/api';
import '../styles/jobboard.css';
import { Loading, EmptyState } from '../components/codequest/ui';
import type { MyApplication } from './jobboard/types';
import { formatCTC, formatStipend, timeAgo } from './jobboard/types';
import { CompanyLogo } from './jobboard/CompanyLogo';

const STATUS_ORDER = ['applied', 'screening', 'interview', 'offered', 'rejected', 'withdrawn'];

export const MyJobsPage: React.FC = () => {
  const [apps, setApps] = useState<MyApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get('/jobs/applications/mine');
        setApps(res.data);
      } catch {
        /* silent */
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const stats = useMemo(() => {
    const s: Record<string, number> = { total: apps.length };
    for (const key of STATUS_ORDER) s[key] = 0;
    for (const a of apps) s[a.status] = (s[a.status] || 0) + 1;
    return s;
  }, [apps]);

  const visible = filter === 'all' ? apps : apps.filter((a) => a.status === filter);

  return (
    <div className="jb-wrap">
      <div className="jb-head">
        <div>
          <h2>My Applications & Job Tracker</h2>
          <p>Track every application, its status and the answers you submitted.</p>
        </div>
      </div>

      {loading ? (
        <Loading label="Loading your applications..." />
      ) : apps.length === 0 ? (
        <EmptyState
          title="No applications yet"
          text="Head to the Job Board to find roles you're eligible for and apply."
        />
      ) : (
        <>
          <div className="mj-stats">
            <div className="mj-stat">
              <div className="n">{stats.total}</div>
              <div className="l">Total</div>
            </div>
            <div className="mj-stat">
              <div className="n" style={{ color: '#a5b4fc' }}>{stats.applied}</div>
              <div className="l">Applied</div>
            </div>
            <div className="mj-stat">
              <div className="n" style={{ color: '#67e8f9' }}>{stats.interview}</div>
              <div className="l">Interview</div>
            </div>
            <div className="mj-stat">
              <div className="n" style={{ color: '#6ee7b7' }}>{stats.offered}</div>
              <div className="l">Offered</div>
            </div>
            <div className="mj-stat">
              <div className="n" style={{ color: '#fca5a5' }}>{stats.rejected}</div>
              <div className="l">Rejected</div>
            </div>
          </div>

          <div className="jb-tabs">
            {['all', ...STATUS_ORDER].map((s) => (
              <button
                key={s}
                className={`jb-tab${filter === s ? ' active' : ''}`}
                onClick={() => setFilter(s)}
                style={{ textTransform: 'capitalize' }}
              >
                {s === 'all' ? 'All' : s} {s !== 'all' && stats[s] ? `(${stats[s]})` : ''}
              </button>
            ))}
          </div>

          <div className="jb-list">
            {visible.map((a) => {
              const job = a.job;
              const pay = job
                ? job.job_type === 'internship'
                  ? formatStipend(job.stipend_min, job.stipend_max)
                  : formatCTC(job.ctc_min, job.ctc_max)
                : '';
              return (
                <div key={a.id} className="glass-card mj-item">
                  <CompanyLogo company={job?.company || ''} fallback={job?.company_logo} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '0.75rem', alignItems: 'flex-start' }}>
                      <div>
                        <h3 className="jb-card-title">{job?.title || 'Job'}</h3>
                        <div className="jb-card-company">{job?.company || '—'}</div>
                        {job && (
                          <div className="jb-portal">
                            via <b>{job.source_portal}</b>
                          </div>
                        )}
                      </div>
                      <span className={`mj-status ${a.status}`}>{a.status}</span>
                    </div>
                    <div className="jb-meta-row">
                      {job && <span><MapPin size={14} /> {job.location || job.employment_mode}</span>}
                      {job && <span><Briefcase size={14} /> {job.employment_mode}</span>}
                      {pay && <span>{pay}</span>}
                      <span><Clock size={14} /> Applied {timeAgo(a.applied_at)}</span>
                    </div>
                    {Object.keys(a.answers || {}).length > 0 && (
                      <details style={{ marginTop: '0.4rem' }}>
                        <summary style={{ cursor: 'pointer', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          View submitted answers
                        </summary>
                        <div style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                          {Object.entries(a.answers).map(([k, v]) => (
                            <div key={k} style={{ fontSize: '0.8rem' }}>
                              <span style={{ color: 'var(--text-muted)' }}>{k}:</span>{' '}
                              <b>{Array.isArray(v) ? v.join(', ') : String(v)}</b>
                            </div>
                          ))}
                        </div>
                      </details>
                    )}
                  </div>
                </div>
              );
            })}
            {visible.length === 0 && (
              <EmptyState title="No applications in this stage" />
            )}
          </div>
        </>
      )}
    </div>
  );
};
