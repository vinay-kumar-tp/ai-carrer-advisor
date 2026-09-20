import React, { useEffect, useState } from 'react';
import { Lightbulb, Sparkles } from 'lucide-react';
import api from '../../services/api';
import { errorMessage } from '../profile/useProfileData';
import type { HistoryResponse } from './types';
import { formatAnalyzedAt } from './types';

type Props = {
  notify: (message: string, tone?: 'success' | 'error') => void;
  refreshKey: number;
};

const MAX_CHIPS = 5;

export const HistoryTab: React.FC<Props> = ({ notify, refreshKey }) => {
  const [data, setData] = useState<HistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      try {
        const res = await api.get<HistoryResponse>('/position-ai/history');
        if (alive) setData(res.data);
      } catch (error) {
        if (alive) notify(errorMessage(error, 'Could not load your analysis history.'), 'error');
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, [notify, refreshKey]);

  if (loading) return <div className="pai-loading">Loading your saved analyses…</div>;

  const items = data?.items ?? [];

  return (
    <div>
      <section className="pai-card pai-hist-intro">
        <h3>
          <Sparkles size={16} color="#f59e0b" /> Your Skill Evolution
        </h3>
        <p>
          Saved analyses capture the selected JDs and your profile skills at the time of comparison, so History
          reflects the exact scope you picked.
        </p>

        <div className="pai-hist-banner">
          <div className="pai-hist-banner-title">
            <Lightbulb size={14} /> Latest skills to consider adding:
          </div>
          <div className="pai-chips">
            {(data?.latest_missing_skills ?? []).length === 0 ? (
              <span className="pai-empty-text">Run an analysis to see suggestions here.</span>
            ) : (
              data!.latest_missing_skills.map((s) => (
                <span key={s} className="pai-chip">
                  {s}
                </span>
              ))
            )}
          </div>
        </div>
      </section>

      <h3 className="pai-section-title">Saved Gap Analyses</h3>

      {items.length === 0 ? (
        <div className="pai-card">
          <div className="pai-empty-box">
            <div className="pai-empty-title">No saved analyses yet</div>
            <div className="pai-empty-text">
              Pick job descriptions on the Main tab and hit “Analyze Job Fit” to log a run here.
            </div>
          </div>
        </div>
      ) : (
        <div className="pai-table-wrap">
          <table className="pai-table">
            <thead>
              <tr>
                <th>Analyzed</th>
                <th>Selected JDs</th>
                <th>Missing Skills</th>
                <th>Profile Skills</th>
                <th>Readiness</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => {
                const shown = item.missing_skills.slice(0, MAX_CHIPS);
                const extra = item.missing_skills.length - shown.length;
                return (
                  <tr key={item.id}>
                    <td className="pai-td-date">{formatAnalyzedAt(item.analyzed_at)}</td>
                    <td>
                      {item.jd_snapshots.map((jd, i) => (
                        <div key={`${item.id}-${i}`} className="pai-hist-jd">
                          <div className="pai-hist-jd-title">{jd.title}</div>
                          {(jd.company || '') && (
                            <div className="pai-hist-jd-meta">{jd.company}</div>
                          )}
                        </div>
                      ))}
                    </td>
                    <td>
                      <div className="pai-chips">
                        {shown.map((m) => (
                          <span key={m.skill} className="pai-chip">
                            {m.skill} ({m.jd_count}/{m.total_jds} JDs)
                          </span>
                        ))}
                      </div>
                      {extra > 0 && <div className="pai-more">+{extra} more</div>}
                    </td>
                    <td className="pai-td-skills">{item.profile_skill_count} skills</td>
                    <td className="pai-td-skills">{item.match_percentage}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
