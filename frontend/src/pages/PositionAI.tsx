import React, { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { Briefcase, Clock, MessageSquare, Sparkles } from 'lucide-react';
import '../styles/positionai.css';
import { ToastHost, useToasts } from '../components/profile/ui';
import { MainTab } from './positionai/MainTab';
import { HistoryTab } from './positionai/HistoryTab';
import { FeedbackTab } from './positionai/FeedbackTab';

type TabKey = 'main' | 'history' | 'feedback';

const TABS: { key: TabKey; label: string; icon: React.ComponentType<{ size?: number }> }[] = [
  { key: 'main', label: 'Main', icon: Briefcase },
  { key: 'history', label: 'History', icon: Clock },
  { key: 'feedback', label: 'Feedback', icon: MessageSquare },
];

const isTab = (value: string | null | undefined): value is TabKey =>
  value === 'main' || value === 'history' || value === 'feedback';

export const PositionAIPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { toasts, push, dismiss } = useToasts();

  // Supports both ?tab=history and the #history form used in the spec.
  const hashTab = location.hash.replace('#', '');
  const initial = isTab(searchParams.get('tab')) ? searchParams.get('tab') : isTab(hashTab) ? hashTab : 'main';
  const [tab, setTab] = useState<TabKey>(initial as TabKey);

  // Latest saved analysis — lets Feedback attach itself to a concrete run and
  // tells History to refetch.
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [historyKey, setHistoryKey] = useState(0);

  useEffect(() => {
    const param = searchParams.get('tab');
    if (isTab(param) && param !== tab) setTab(param);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const selectTab = (next: TabKey) => {
    setTab(next);
    const params = new URLSearchParams(searchParams);
    params.set('tab', next);
    setSearchParams(params, { replace: true });
    if (location.hash) navigate({ hash: '' }, { replace: true });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const onAnalysisSaved = useCallback((id: string | null) => {
    setAnalysisId(id);
    setHistoryKey((k) => k + 1);
  }, []);

  return (
    <div className="pai">
      <header className="pai-hero">
        <div className="pai-hero-kicker">Foundation for Excellence</div>
        <div className="pai-hero-title">
          <span className="pai-hero-mark">
            <Sparkles size={18} />
          </span>
          <h1>Position AI</h1>
        </div>
        <p className="pai-hero-sub">Your assistant to a successful career</p>

        <nav className="pai-tabs" role="tablist" aria-label="Position AI sections">
          {TABS.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.key}
                role="tab"
                aria-selected={tab === item.key}
                className={`pai-tab${tab === item.key ? ' is-active' : ''}`}
                onClick={() => selectTab(item.key)}
              >
                <Icon size={14} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </header>

      <div className="pai-body">
        {tab === 'main' && <MainTab notify={push} onAnalysisSaved={onAnalysisSaved} />}
        {tab === 'history' && <HistoryTab notify={push} refreshKey={historyKey} />}
        {tab === 'feedback' && <FeedbackTab notify={push} analysisId={analysisId} />}
      </div>

      <ToastHost toasts={toasts} onDismiss={dismiss} />
    </div>
  );
};

export default PositionAIPage;
