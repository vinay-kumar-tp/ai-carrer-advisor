import React, { useEffect, useState } from 'react';
import { Trophy } from 'lucide-react';
import { Loading, EmptyState } from '../../components/codequest/ui';
import api from '../../services/api';
import type { LeaderRow } from './types';

export const LeaderboardTab: React.FC = () => {
  const [rows, setRows] = useState<LeaderRow[] | null>(null);

  useEffect(() => {
    api.get<LeaderRow[]>('/aptitude/leaderboard').then(({ data }) => setRows(data)).catch(() => setRows([]));
  }, []);

  if (rows === null) return <Loading label="Loading leaderboard…" />;
  if (rows.length === 0) {
    return <EmptyState title="No rankings yet" text="Answer questions to earn XP and climb the board." />;
  }

  return (
    <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '1rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
        <Trophy size={18} color="#fbbf24" />
        <strong>Aptitude Leaderboard</strong>
      </div>
      {rows.map((r) => (
        <div className="aq-lb-row" key={r.user_id}>
          <span className={`aq-lb-rank ${r.rank <= 3 ? 'top' : ''}`}>{r.rank}</span>
          <span className="aq-lb-name">{r.full_name}</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Lvl {r.level}</span>
          <span className="aq-lb-xp">{r.total_xp} XP</span>
        </div>
      ))}
    </div>
  );
};
