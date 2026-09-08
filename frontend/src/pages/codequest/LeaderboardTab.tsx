import React, { useEffect, useState } from 'react';
import { Trophy } from 'lucide-react';
import api from '../../services/api';
import { EmptyState, Loading } from '../../components/codequest/ui';
import type { LeaderboardRow } from './types';

const MEDALS = ['#f59e0b', '#94a3b8', '#b45309'];

export const LeaderboardTab: React.FC<{
  notify: (message: string, tone?: 'success' | 'error') => void;
}> = ({ notify }) => {
  const [rows, setRows] = useState<LeaderboardRow[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    api
      .get<LeaderboardRow[]>('/codequest/leaderboard', { params: { limit: 50 } })
      .then(({ data }) => {
        if (!cancelled) setRows(data);
      })
      .catch(() => {
        if (!cancelled) {
          setRows([]);
          notify('Could not load the leaderboard.', 'error');
        }
      });
    return () => {
      cancelled = true;
    };
  }, [notify]);

  if (rows === null) return <Loading label="Loading leaderboard..." />;

  return (
    <div className="cq-card">
      <div className="cq-card-head">
        <div>
          <h3 className="cq-card-title">Leaderboard</h3>
          <div className="cq-card-sub">Ranked by total points earned across the platform</div>
        </div>
      </div>

      {rows.length === 0 ? (
        <EmptyState title="Nobody on the board yet" text="Solve a problem to claim the first spot." />
      ) : (
        <div className="cq-table-wrap">
          <table className="cq-table">
            <thead>
              <tr>
                <th style={{ width: 70 }}>Rank</th>
                <th>Name</th>
                <th style={{ width: 90 }}>Level</th>
                <th style={{ width: 110 }}>Solved</th>
                <th style={{ width: 110 }}>Points</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.user_id}>
                  <td>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', fontWeight: 700 }}>
                      {row.rank <= 3 && <Trophy size={14} color={MEDALS[row.rank - 1]} />}
                      {row.rank}
                    </span>
                  </td>
                  <td style={{ fontWeight: 600, color: '#1f2937' }}>{row.full_name}</td>
                  <td>{row.level}</td>
                  <td>{row.problems_solved}</td>
                  <td style={{ fontWeight: 700, color: '#d97a09' }}>{row.total_xp.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
