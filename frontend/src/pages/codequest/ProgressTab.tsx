import React, { useEffect, useState } from 'react';
import { Flame, ListChecks, Star, TrendingUp } from 'lucide-react';
import api from '../../services/api';
import { EmptyState, Loading } from '../../components/codequest/ui';
import { VERDICT_LABEL } from './types';
import type { Progress } from './types';

const LEVELS = ['easy', 'medium', 'hard'] as const;

export const ProgressTab: React.FC<{ notify: (m: string, t?: 'success' | 'error') => void }> = ({
  notify,
}) => {
  const [data, setData] = useState<Progress | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api
      .get<Progress>('/codequest/progress')
      .then(({ data: payload }) => {
        if (!cancelled) setData(payload);
      })
      .catch(() => {
        if (!cancelled) notify('Could not load your progress.', 'error');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [notify]);

  if (loading) return <Loading label="Loading your progress..." />;
  if (!data) return null;

  const overall = data.total_problems ? Math.round((data.solved / data.total_problems) * 100) : 0;

  return (
    <>
      <div className="cq-stats">
        <div className="cq-stat">
          <div className="cq-stat-icon tone-green">
            <ListChecks size={18} />
          </div>
          <div>
            <div className="cq-stat-value">
              {data.solved}
              <span style={{ fontSize: '0.9rem', color: '#94a3b8', fontWeight: 600 }}>
                /{data.total_problems}
              </span>
            </div>
            <div className="cq-stat-label">Problems solved ({overall}%)</div>
          </div>
        </div>
        <div className="cq-stat">
          <div className="cq-stat-icon tone-amber">
            <Star size={18} />
          </div>
          <div>
            <div className="cq-stat-value">{data.points.toLocaleString()}</div>
            <div className="cq-stat-label">Points earned</div>
          </div>
        </div>
        <div className="cq-stat">
          <div className="cq-stat-icon tone-blue">
            <TrendingUp size={18} />
          </div>
          <div>
            <div className="cq-stat-value">{data.level}</div>
            <div className="cq-stat-label">Level</div>
          </div>
        </div>
        <div className="cq-stat">
          <div className="cq-stat-icon tone-red">
            <Flame size={18} />
          </div>
          <div>
            <div className="cq-stat-value">{data.streak_days}d</div>
            <div className="cq-stat-label">Current streak</div>
          </div>
        </div>
      </div>

      <div className="cq-card">
        <div className="cq-card-head">
          <h3 className="cq-card-title">By difficulty</h3>
          <span className="cq-card-sub">{data.attempted} problems attempted overall</span>
        </div>
        <div className="cq-table-wrap">
          <table className="cq-table">
            <thead>
              <tr>
                <th>Difficulty</th>
                <th style={{ width: 110 }}>Solved</th>
                <th>Progress</th>
              </tr>
            </thead>
            <tbody>
              {LEVELS.map((level) => {
                const bucket = data.by_difficulty[level] ?? { total: 0, solved: 0 };
                const percent = bucket.total ? Math.round((bucket.solved / bucket.total) * 100) : 0;
                return (
                  <tr key={level}>
                    <td style={{ fontWeight: 700, textTransform: 'capitalize', color: '#1f2937' }}>
                      {level}
                    </td>
                    <td>
                      {bucket.solved}/{bucket.total}
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <div className="cq-bar" style={{ flex: 1 }}>
                          <div
                            className={`cq-bar-fill ${level === 'easy' ? '' : level}`}
                            style={{ width: `${percent}%` }}
                          />
                        </div>
                        <span style={{ fontSize: '0.76rem', color: '#94a3b8', minWidth: 34 }}>
                          {percent}%
                        </span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="cq-card">
        <div className="cq-card-head">
          <h3 className="cq-card-title">By topic</h3>
          <span className="cq-card-sub">Where your practice is concentrated</span>
        </div>
        {data.by_topic.length === 0 ? (
          <EmptyState title="Nothing tracked yet" text="Solve a problem to start building this view." />
        ) : (
          <div className="cq-table-wrap">
            <table className="cq-table">
              <thead>
                <tr>
                  <th>Topic</th>
                  <th style={{ width: 110 }}>Solved</th>
                  <th>Progress</th>
                </tr>
              </thead>
              <tbody>
                {data.by_topic.slice(0, 25).map((row) => {
                  const percent = row.total ? Math.round((row.solved / row.total) * 100) : 0;
                  return (
                    <tr key={row.topic}>
                      <td style={{ fontWeight: 600, color: '#1f2937' }}>{row.topic}</td>
                      <td>
                        {row.solved}/{row.total}
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                          <div className="cq-bar" style={{ flex: 1 }}>
                            <div className="cq-bar-fill" style={{ width: `${percent}%` }} />
                          </div>
                          <span style={{ fontSize: '0.76rem', color: '#94a3b8', minWidth: 34 }}>
                            {percent}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="cq-card">
        <div className="cq-card-head">
          <h3 className="cq-card-title">Recent submissions</h3>
        </div>
        {data.recent.length === 0 ? (
          <EmptyState
            title="No submissions yet"
            text="Pick a problem from the Problems tab and hit Submit to see your history here."
          />
        ) : (
          <div className="cq-table-wrap">
            <table className="cq-table">
              <thead>
                <tr>
                  <th>Problem</th>
                  <th>Language</th>
                  <th>Verdict</th>
                  <th>Tests</th>
                  <th>When</th>
                </tr>
              </thead>
              <tbody>
                {data.recent.map((row) => (
                  <tr key={row.id}>
                    {/* The API reuses `code` to carry the problem title on this endpoint. */}
                    <td style={{ fontWeight: 600, color: '#1f2937' }}>{row.code || '--'}</td>
                    <td>{row.language}</td>
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
                    <td>{row.created_at ? new Date(row.created_at).toLocaleString() : '--'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
};
