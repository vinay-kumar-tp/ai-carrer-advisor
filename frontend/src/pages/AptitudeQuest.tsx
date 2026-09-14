import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Brain, BarChart3, Trophy, ListChecks } from 'lucide-react';
import '../styles/aptitude.css';
import { ToastHost, useToasts } from '../components/codequest/ui';
import { PracticeTab } from './aptitude/PracticeTab';
import { ProgressTab } from './aptitude/ProgressTab';
import { LeaderboardTab } from './aptitude/LeaderboardTab';

type TabKey = 'practice' | 'progress' | 'leaderboard';

const TABS: { key: TabKey; label: string; icon: React.ReactNode }[] = [
  { key: 'practice', label: 'Practice', icon: <ListChecks size={14} /> },
  { key: 'progress', label: 'My Progress', icon: <BarChart3 size={14} /> },
  { key: 'leaderboard', label: 'Leaderboard', icon: <Trophy size={14} /> },
];

const isTab = (v: string | null): v is TabKey =>
  v === 'practice' || v === 'progress' || v === 'leaderboard';

export const AptitudeQuestPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get('tab');
  const topic = searchParams.get('topic');
  const tab: TabKey = isTab(tabParam) ? tabParam : 'practice';
  const { toasts, push, dismiss } = useToasts();

  const [, force] = useState(0);

  const updateParams = (patch: Record<string, string | null>) => {
    const next = new URLSearchParams(searchParams);
    Object.entries(patch).forEach(([k, v]) => {
      if (v === null || v === '') next.delete(k);
      else next.set(k, v);
    });
    setSearchParams(next, { replace: true });
    force((n) => n + 1);
  };

  const selectTab = (next: TabKey) => {
    updateParams({ tab: next === 'practice' ? null : next, topic: null });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="aq">
      <header className="aq-hero">
        <div className="aq-hero-head">
          <span className="aq-hero-badge">
            <Brain size={22} />
          </span>
          <div>
            <h1>Aptitude Quest</h1>
            <p>Learn it, practise it, prove it — quant, logical, verbal, and technical MCQs with instant feedback.</p>
          </div>
        </div>

        <nav className="aq-tabs" role="tablist" aria-label="Aptitude Quest sections">
          {TABS.map((item) => (
            <button
              key={item.key}
              role="tab"
              aria-selected={tab === item.key}
              className={`aq-tab${tab === item.key ? ' is-active' : ''}`}
              onClick={() => selectTab(item.key)}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </nav>
      </header>

      {tab === 'practice' && (
        <PracticeTab
          notify={push}
          activeTopic={topic}
          onOpenTopic={(slug) => updateParams({ topic: slug })}
        />
      )}
      {tab === 'progress' && <ProgressTab />}
      {tab === 'leaderboard' && <LeaderboardTab />}

      <ToastHost toasts={toasts} onDismiss={dismiss} />
    </div>
  );
};

export default AptitudeQuestPage;
