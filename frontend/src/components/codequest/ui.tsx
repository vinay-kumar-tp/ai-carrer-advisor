/** Small presentational pieces shared across the Code Quest tabs. */
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertCircle,
  Check,
  ChevronDown,
  CircleDashed,
  CircleDot,
  Loader2,
  Search,
  Star,
  X,
} from 'lucide-react';
import type { Difficulty, FacetValue, ProblemStatus } from '../../pages/codequest/types';

/* ── Toasts ─────────────────────────────────────────────── */

export type Toast = { id: number; message: string; tone: 'success' | 'error' };

export const useToasts = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const counter = useRef(0);

  const push = useCallback((message: string, tone: 'success' | 'error' = 'success') => {
    const id = ++counter.current;
    setToasts((current) => [...current, { id, message, tone }]);
    window.setTimeout(() => setToasts((current) => current.filter((t) => t.id !== id)), 4000);
  }, []);

  const dismiss = useCallback(
    (id: number) => setToasts((current) => current.filter((t) => t.id !== id)),
    [],
  );

  return { toasts, push, dismiss };
};

export const ToastHost: React.FC<{ toasts: Toast[]; onDismiss: (id: number) => void }> = ({
  toasts,
  onDismiss,
}) => {
  if (!toasts.length) return null;
  return (
    <div className="cq-toasts" role="status" aria-live="polite">
      {toasts.map((toast) => (
        <div key={toast.id} className={`cq-toast is-${toast.tone}`}>
          {toast.tone === 'success' ? <Check size={15} /> : <AlertCircle size={15} />}
          <span style={{ flex: 1 }}>{toast.message}</span>
          <button
            onClick={() => onDismiss(toast.id)}
            aria-label="Dismiss"
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', padding: 0 }}
          >
            <X size={13} />
          </button>
        </div>
      ))}
    </div>
  );
};

/* ── Badges ─────────────────────────────────────────────── */

export const DifficultyBadge: React.FC<{ level: Difficulty }> = ({ level }) => (
  <span className={`cq-diff ${level}`}>
    <span className="cq-diff-dot" />
    {level.charAt(0).toUpperCase() + level.slice(1)}
  </span>
);

export const StatusBadge: React.FC<{ status: ProblemStatus }> = ({ status }) => {
  if (status === 'solved') {
    return (
      <span className="cq-status is-solved">
        <Check size={13} /> Solved
      </span>
    );
  }
  if (status === 'attempted') {
    return (
      <span className="cq-status is-attempted">
        <CircleDot size={13} /> Attempted
      </span>
    );
  }
  return (
    <span className="cq-status">
      <CircleDashed size={13} /> Not attempted
    </span>
  );
};

export const PointsBadge: React.FC<{ points: number }> = ({ points }) => (
  <span className="cq-points">
    <Star size={12} /> {points} pts
  </span>
);

export const Chip: React.FC<{ children: React.ReactNode; tone?: 'blue' | 'accent' | 'plain' }> = ({
  children,
  tone = 'blue',
}) => <span className={`cq-chip${tone === 'accent' ? ' is-accent' : tone === 'plain' ? ' is-plain' : ''}`}>{children}</span>;

/* ── Loading / empty ────────────────────────────────────── */

export const Loading: React.FC<{ label?: string }> = ({ label = 'Loading...' }) => (
  <div className="cq-loading">
    <Loader2 size={18} className="cq-spin" /> {label}
  </div>
);

export const EmptyState: React.FC<{
  title: string;
  text?: string;
  actionLabel?: string;
  onAction?: () => void;
}> = ({ title, text, actionLabel, onAction }) => (
  <div className="cq-empty">
    <div className="cq-empty-title">{title}</div>
    {text && <div className="cq-empty-text">{text}</div>}
    {actionLabel && onAction && (
      <button className="cq-btn cq-btn-outline" onClick={onAction}>
        {actionLabel}
      </button>
    )}
  </div>
);

/* ── Facet dropdown ─────────────────────────────────────── */

type FacetDropdownProps = {
  label: string;
  icon?: React.ReactNode;
  options: FacetValue[];
  value: string;
  onChange: (value: string) => void;
  allLabel?: string;
  /** Optional highlighted group shown above the plain list. */
  groupLabel?: string;
  groupNames?: string[];
};

export const FacetDropdown: React.FC<FacetDropdownProps> = ({
  label,
  icon,
  options,
  value,
  onChange,
  allLabel,
  groupLabel,
  groupNames,
}) => {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDocumentDown = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false);
    };
    document.addEventListener('mousedown', onDocumentDown);
    document.addEventListener('keydown', onKey);
    inputRef.current?.focus();
    return () => {
      document.removeEventListener('mousedown', onDocumentDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  const needle = query.trim().toLowerCase();
  const filtered = useMemo(
    () => (needle ? options.filter((option) => option.name.toLowerCase().includes(needle)) : options),
    [options, needle],
  );

  const grouped = useMemo(() => {
    if (!groupNames?.length) return { featured: [] as FacetValue[], rest: filtered };
    const featuredSet = new Set(groupNames);
    return {
      featured: filtered.filter((option) => featuredSet.has(option.name)),
      rest: filtered.filter((option) => !featuredSet.has(option.name)),
    };
  }, [filtered, groupNames]);

  const pick = (next: string) => {
    onChange(next);
    setOpen(false);
    setQuery('');
  };

  return (
    <div className="cq-facet" ref={containerRef}>
      <button
        type="button"
        className={`cq-facet-trigger${value ? ' is-set' : ''}`}
        onClick={() => setOpen((current) => !current)}
        aria-expanded={open}
        aria-haspopup="listbox"
      >
        {icon}
        {value || label}
        <ChevronDown size={13} />
      </button>

      {open && (
        <div className="cq-facet-menu" role="listbox" aria-label={label}>
          <div className="cq-facet-search">
            <Search size={14} color="#94a3b8" />
            <input
              ref={inputRef}
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={`Search ${label.toLowerCase()}...`}
              aria-label={`Search ${label}`}
            />
          </div>

          <div className="cq-facet-list">
            <button
              type="button"
              className={`cq-facet-option${value === '' ? ' is-selected' : ''}`}
              onClick={() => pick('')}
            >
              <span>
                {value === '' && <Check size={13} style={{ marginRight: 4, verticalAlign: -2 }} />}
                {allLabel || `All ${label.toLowerCase()}`}
              </span>
            </button>

            {grouped.featured.length > 0 && (
              <>
                <div className="cq-facet-group">{groupLabel}</div>
                {grouped.featured.map((option) => (
                  <button
                    key={option.name}
                    type="button"
                    className={`cq-facet-option${value === option.name ? ' is-selected' : ''}`}
                    onClick={() => pick(option.name)}
                  >
                    <span>{option.name}</span>
                    <span className="cq-facet-count">{option.count.toLocaleString()}</span>
                  </button>
                ))}
              </>
            )}

            {grouped.rest.map((option) => (
              <button
                key={option.name}
                type="button"
                className={`cq-facet-option${value === option.name ? ' is-selected' : ''}`}
                onClick={() => pick(option.name)}
              >
                <span>{option.name}</span>
                <span className="cq-facet-count">{option.count.toLocaleString()}</span>
              </button>
            ))}

            {filtered.length === 0 && <div className="cq-facet-empty">No match for "{query}"</div>}
          </div>
        </div>
      )}
    </div>
  );
};

/* ── Pagination ─────────────────────────────────────────── */

export const Pager: React.FC<{
  page: number;
  pageCount: number;
  onPage: (page: number) => void;
}> = ({ page, pageCount, onPage }) => {
  if (pageCount <= 1) return null;

  // Show a compact window of pages around the current one.
  const numbers: number[] = [];
  const start = Math.max(1, Math.min(page - 2, pageCount - 4));
  const end = Math.min(pageCount, start + 4);
  for (let value = start; value <= end; value += 1) numbers.push(value);

  return (
    <div className="cq-pager">
      <button className="cq-pager-btn" onClick={() => onPage(1)} disabled={page === 1} aria-label="First page">
        {'<<'}
      </button>
      <button
        className="cq-pager-btn"
        onClick={() => onPage(page - 1)}
        disabled={page === 1}
        aria-label="Previous page"
      >
        {'<'}
      </button>
      {numbers.map((value) => (
        <button
          key={value}
          className={`cq-pager-btn${value === page ? ' is-current' : ''}`}
          onClick={() => onPage(value)}
          aria-current={value === page ? 'page' : undefined}
        >
          {value}
        </button>
      ))}
      <button
        className="cq-pager-btn"
        onClick={() => onPage(page + 1)}
        disabled={page >= pageCount}
        aria-label="Next page"
      >
        {'>'}
      </button>
      <button
        className="cq-pager-btn"
        onClick={() => onPage(pageCount)}
        disabled={page >= pageCount}
        aria-label="Last page"
      >
        {'>>'}
      </button>
    </div>
  );
};

/** Renders `text with `code` spans` as inline code without a markdown dependency. */
export const InlineMarkdown: React.FC<{ text: string }> = ({ text }) => {
  const parts = text.split(/(`[^`]+`)/g);
  return (
    <>
      {parts.map((part, index) =>
        part.startsWith('`') && part.endsWith('`') && part.length > 2 ? (
          <code key={index}>{part.slice(1, -1)}</code>
        ) : (
          <React.Fragment key={index}>{part}</React.Fragment>
        ),
      )}
    </>
  );
};

/** Splits a statement on blank lines and renders each paragraph. */
export const Prose: React.FC<{ text: string }> = ({ text }) => (
  <div className="cq-prose">
    {text
      .split(/\n\s*\n/)
      .filter((block) => block.trim())
      .map((block, index) => (
        <p key={index}>
          <InlineMarkdown text={block.trim()} />
        </p>
      ))}
  </div>
);
