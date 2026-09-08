import React, { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Download, RefreshCw } from 'lucide-react';
import api from '../services/api';
import '../styles/profile.css';
import { Loading, ToastHost, useToasts } from '../components/profile/ui';
import { ProfileTab } from './profile/ProfileTab';
import { ResumeTab } from './profile/ResumeTab';
import { ScorecardTab } from './profile/ScorecardTab';
import { DocumentsTab } from './profile/DocumentsTab';
import { errorMessage, useProfileData } from './profile/useProfileData';

type TabKey = 'profile' | 'resume' | 'scorecard' | 'documents';

const TABS: { key: TabKey; label: string; hint: string }[] = [
  { key: 'profile', label: 'Profile', hint: 'Here, you can view & edit your profile' },
  { key: 'resume', label: 'Resume', hint: 'Generate, upload and optimise your resumes' },
  { key: 'scorecard', label: 'Scorecard', hint: 'Here, you can view your scorecard' },
  { key: 'documents', label: 'Documents', hint: 'Here you can view your documents' },
];

const isTab = (value: string | null): value is TabKey =>
  value === 'profile' || value === 'resume' || value === 'scorecard' || value === 'documents';

export const ProfilePage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get('tab');
  const [tab, setTab] = useState<TabKey>(isTab(tabParam) ? tabParam : 'profile');

  const { profile, loading, loadError, reload, save } = useProfileData();
  const { toasts, push, dismiss } = useToasts();
  const [exporting, setExporting] = useState(false);

  // Keep the tab in the URL so a refresh (or a shared link) lands in place.
  useEffect(() => {
    if (isTab(tabParam) && tabParam !== tab) setTab(tabParam);
  }, [tabParam]); // eslint-disable-line react-hooks/exhaustive-deps

  const selectTab = useCallback(
    (next: TabKey) => {
      setTab(next);
      const params = new URLSearchParams(searchParams);
      params.set('tab', next);
      setSearchParams(params, { replace: true });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    [searchParams, setSearchParams],
  );

  const exportPdf = async () => {
    setExporting(true);
    try {
      const { data } = await api.get('/profile/export/pdf', { responseType: 'blob' });
      const url = URL.createObjectURL(data as Blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `${profile?.full_name || 'profile'} - Profile.pdf`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      push('Profile PDF downloaded');
    } catch (error) {
      push(errorMessage(error, 'Could not export your profile.'), 'error');
    } finally {
      setExporting(false);
    }
  };

  const activeTab = TABS.find((t) => t.key === tab)!;

  return (
    <div className="mp">
      <div className="mp-topbar">
        <h1>My Profile</h1>
        <button className="mp-btn mp-btn-outline mp-btn-sm" onClick={exportPdf} disabled={exporting || !profile}>
          <Download size={13} /> {exporting ? 'Preparing...' : 'Download Profile As PDF'}
        </button>
      </div>

      <nav className="mp-tabs" role="tablist" aria-label="Profile sections">
        {TABS.map((item) => (
          <button
            key={item.key}
            role="tab"
            aria-selected={tab === item.key}
            className={`mp-tab${tab === item.key ? ' is-active' : ''}`}
            onClick={() => selectTab(item.key)}
          >
            {item.label}
            {item.key === 'resume' && profile && profile.resume_count > 0 && (
              <span className="mp-tab-count">{String(profile.resume_count).padStart(2, '0')}</span>
            )}
          </button>
        ))}
      </nav>

      <div className="mp-tabhint">{activeTab.hint}</div>

      {tab === 'profile' && <div className="mp-banner" aria-hidden="true" />}

      {loading && !profile && <Loading />}

      {loadError && !profile && (
        <div className="mp-card" style={{ marginTop: '1rem' }}>
          <div className="mp-modal-error">{loadError}</div>
          <button className="mp-btn mp-btn-primary mp-btn-sm" style={{ marginTop: '0.8rem' }} onClick={reload}>
            <RefreshCw size={13} /> Try again
          </button>
        </div>
      )}

      {profile && (
        <>
          {tab === 'profile' && (
            <ProfileTab
              profile={profile}
              save={save}
              notify={push}
              onGoToTab={(next) => selectTab(next)}
            />
          )}
          {tab === 'resume' && <ResumeTab notify={push} onChanged={reload} />}
          {tab === 'scorecard' && <ScorecardTab notify={push} />}
          {tab === 'documents' && <DocumentsTab notify={push} onChanged={reload} />}
        </>
      )}

      <ToastHost toasts={toasts} onDismiss={dismiss} />
    </div>
  );
};

export default ProfilePage;
