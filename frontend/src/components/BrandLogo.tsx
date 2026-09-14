import React from 'react';

/**
 * Carrerpulse Ai brand assets — an original SVG mark + wordmark.
 *
 * The mark evokes a rising "A" path with a graduation cap at its base, a curving
 * road leading upward, and an "i" figure crowned by a spark — the visual story of
 * "explore · learn · prepare · grow". Rendered as crisp gradient SVG so it scales
 * on the sidebar, login screen and the intro animation without raster artifacts.
 */

let _idSeq = 0;

export const BrandMark: React.FC<{ size?: number; className?: string; glow?: boolean }> = ({
  size = 40,
  className,
  glow = true,
}) => {
  // Unique gradient ids so multiple marks on one page don't collide.
  const uid = React.useMemo(() => `bm${++_idSeq}`, []);

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      className={className}
      role="img"
      aria-label="Carrerpulse Ai logo"
      style={glow ? { filter: 'drop-shadow(0 4px 14px rgba(37,99,235,0.45))' } : undefined}
    >
      <defs>
        <linearGradient id={`${uid}-a`} x1="15" y1="15" x2="80" y2="90" gradientUnits="userSpaceOnUse">
          <stop stopColor="#38bdf8" />
          <stop offset="0.5" stopColor="#2563eb" />
          <stop offset="1" stopColor="#1e3a8a" />
        </linearGradient>
        <linearGradient id={`${uid}-i`} x1="60" y1="25" x2="90" y2="90" gradientUnits="userSpaceOnUse">
          <stop stopColor="#818cf8" />
          <stop offset="1" stopColor="#6d28d9" />
        </linearGradient>
        <linearGradient id={`${uid}-road`} x1="20" y1="80" x2="70" y2="30" gradientUnits="userSpaceOnUse">
          <stop stopColor="#0ea5e9" />
          <stop offset="1" stopColor="#60a5fa" />
        </linearGradient>
        <radialGradient id={`${uid}-spark`} cx="0.5" cy="0.5" r="0.5">
          <stop stopColor="#fde68a" />
          <stop offset="1" stopColor="#f59e0b" />
        </radialGradient>
      </defs>

      {/* Left leg of the "A" */}
      <path
        d="M40 88 L12 88 Q9 88 11 84 L34 22 Q37 14 45 20 L52 30 Q46 32 44 40 L28 80 L40 80 Z"
        fill={`url(#${uid}-a)`}
      />

      {/* Right stroke sweeping up toward the "i" */}
      <path
        d="M50 30 Q64 12 74 34 Q84 58 66 88 L54 88 Q72 60 60 40 Q54 30 46 44 Z"
        fill={`url(#${uid}-i)`}
      />

      {/* Rising road inside the A */}
      <path
        d="M22 80 Q30 58 46 46 Q58 37 66 30"
        stroke={`url(#${uid}-road)`}
        strokeWidth="5"
        strokeLinecap="round"
        fill="none"
        opacity="0.9"
      />

      {/* Graduation cap at the base of the road */}
      <g fill="#e2e8f0">
        <path d="M22 66 L36 60 L50 66 L36 72 Z" />
        <path d="M32 70 L32 77 Q36 80 40 77 L40 70 L36 72 Z" opacity="0.85" />
      </g>

      {/* "i" head */}
      <circle cx="72" cy="34" r="7" fill={`url(#${uid}-i)`} />

      {/* Spark / star */}
      <path
        d="M84 16 L86.5 22 L92 24.5 L86.5 27 L84 33 L81.5 27 L76 24.5 L81.5 22 Z"
        fill={`url(#${uid}-spark)`}
      />
    </svg>
  );
};

type WordmarkProps = {
  /** 'full' shows the tagline row, 'compact' is just the wordmark. */
  variant?: 'full' | 'compact';
  markSize?: number;
  className?: string;
  /** Light background contexts (login card) flip the wordmark to dark ink. */
  tone?: 'light' | 'dark';
};

export const BrandLogo: React.FC<WordmarkProps> = ({
  variant = 'compact',
  markSize = 40,
  className,
  tone = 'light',
}) => (
  <div className={`brand-logo ${tone === 'dark' ? 'is-dark' : ''} ${className || ''}`}>
    <BrandMark size={markSize} />
    <div className="brand-logo-text">
      <span className="brand-word">
        Carrerpulse <span className="brand-word-ai">Ai</span>
      </span>
      {variant === 'full' && <span className="brand-tagline">A Brighter You, Ahead</span>}
    </div>
  </div>
);
