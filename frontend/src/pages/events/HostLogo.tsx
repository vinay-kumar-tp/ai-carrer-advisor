import React, { useState } from 'react';

type Props = {
  company: string;
  domain?: string;
  fallback?: string;
  className?: string;
};

/**
 * Host brand mark with a graceful fallback chain:
 *   real logo (by domain) → initials avatar → the seeded emoji.
 */
export const HostLogo: React.FC<Props> = ({ company, domain, fallback, className = 'ev-logo' }) => {
  const [stage, setStage] = useState<0 | 1 | 2>(domain ? 0 : 1);

  if (stage === 2 || !company) {
    return (
      <div className={className} aria-hidden="true">
        {fallback || '📅'}
      </div>
    );
  }

  const src =
    stage === 0
      ? `https://logo.clearbit.com/${domain}`
      : `https://ui-avatars.com/api/?name=${encodeURIComponent(company)}&background=7c6bd6&color=fff&bold=true&size=128&length=2&font-size=0.4`;

  return (
    <div className={className}>
      <img
        src={src}
        alt={`${company} logo`}
        loading="lazy"
        onError={() => setStage((s) => (s === 0 ? 1 : 2))}
        style={{ width: '100%', height: '100%', objectFit: 'contain' }}
      />
    </div>
  );
};
