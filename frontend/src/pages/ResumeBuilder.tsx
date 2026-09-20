/**
 * Standalone "AI Resume Builder" page (sidebar route /resume-builder).
 *
 * This is the SAME feature as My Profile → Resume tab. It renders the resume
 * library + full builder (template picker, live preview, analyzer, tailor-to-job)
 * so the sidebar entry and the profile tab stay in lockstep — one implementation,
 * two entry points.
 */
import React from 'react';
import '../styles/profile.css';
import { ToastHost, useToasts } from '../components/profile/ui';
import { ResumeTab } from './profile/ResumeTab';

export const ResumeBuilderPage: React.FC = () => {
  const { toasts, push, dismiss } = useToasts();

  return (
    <div className="mp">
      <div className="mp-topbar">
        <h1>AI Resume Builder</h1>
      </div>
      <div className="mp-tabhint">
        Generate a resume from your profile, pick a template, run the AI analyzer and tailor it to any job.
      </div>

      {/* onChanged is a no-op refresh hook here; the tab reloads its own library. */}
      <ResumeTab notify={push} onChanged={() => undefined} />

      <ToastHost toasts={toasts} onDismiss={dismiss} />
    </div>
  );
};

export default ResumeBuilderPage;
