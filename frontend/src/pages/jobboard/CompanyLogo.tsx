import React, { useState } from 'react';
import { companyLogoUrl } from './types';

type Props = {
  company: string;
  /** Emoji fallback (from the seed's company_logo) shown if the image fails. */
  fallback?: string;
  className?: string;
};

/** Renders a mock "real" company logo (initials brand mark) with graceful fallback. */
export const CompanyLogo: React.FC<Props> = ({ company, fallback, className = 'jb-logo' }) => {
  const [failed, setFailed] = useState(false);

  if (failed || !company) {
    return <div className={className}>{fallback || '🏢'}</div>;
  }

  return (
    <div className={className} style={{ padding: 0, overflow: 'hidden', background: 'transparent' }}>
      <img
        src={companyLogoUrl(company)}
        alt={`${company} logo`}
        loading="lazy"
        onError={() => setFailed(true)}
        style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
      />
    </div>
  );
};
