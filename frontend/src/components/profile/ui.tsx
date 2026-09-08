/**
 * Presentational primitives for the My Profile screen.
 * Nothing here talks to the API — each piece takes data and callbacks.
 */
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertCircle,
  Check,
  ChevronLeft,
  ChevronRight,
  FolderOpen,
  Loader2,
  Pencil,
  Plus,
  Trash2,
  X,
} from 'lucide-react';

export const EMPTY = '--';

/** Renders `--` for blank values, exactly like the reference layout. */
export const display = (value: unknown): string => {
  if (value === null || value === undefined) return EMPTY;
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (Array.isArray(value)) return value.length ? value.join(', ') : EMPTY;
  const text = String(value).trim();
  return text === '' ? EMPTY : text;
};

export const joinParts = (parts: unknown[], separator = ' • '): string =>
  parts
    .map((p) => (p === null || p === undefined ? '' : String(p).trim()))
    .filter(Boolean)
    .join(separator);

export const dateRange = (start?: string, end?: string, ongoing?: boolean): string => {
  if (ongoing) return start ? `${start} - Present` : 'Present';
  if (start && end) return `${start} - ${end}`;
  return start || end || '';
};

/* ── Toasts ─────────────────────────────────────────────── */

export type Toast = { id: number; message: string; tone: 'success' | 'error' };

export const useToasts = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const counter = useRef(0);

  const push = useCallback((message: string, tone: 'success' | 'error' = 'success') => {
    const id = ++counter.current;
    setToasts((current) => [...current, { id, message, tone }]);
    window.setTimeout(() => setToasts((current) => current.filter((t) => t.id !== id)), 3600);
  }, []);

  const dismiss = useCallback((id: number) => {
    setToasts((current) => current.filter((t) => t.id !== id));
  }, []);

  return { toasts, push, dismiss };
};

export const ToastHost: React.FC<{ toasts: Toast[]; onDismiss: (id: number) => void }> = ({ toasts, onDismiss }) => {
  if (!toasts.length) return null;
  return (
    <div className="mp-toasts" role="status" aria-live="polite">
      {toasts.map((toast) => (
        <div key={toast.id} className={`mp-toast is-${toast.tone}`}>
          {toast.tone === 'success' ? <Check size={15} /> : <AlertCircle size={15} />}
          <span style={{ flex: 1 }}>{toast.message}</span>
          <button className="mp-chip-x" onClick={() => onDismiss(toast.id)} aria-label="Dismiss notification">
            <X size={13} />
          </button>
        </div>
      ))}
    </div>
  );
};

/* ── Buttons ────────────────────────────────────────────── */

type IconButtonProps = {
  icon: 'pencil' | 'plus' | 'trash';
  label: string;
  onClick: () => void;
  variant?: 'outline' | 'solid' | 'danger' | 'plain';
};

export const IconButton: React.FC<IconButtonProps> = ({ icon, label, onClick, variant = 'outline' }) => {
  const Glyph = icon === 'pencil' ? Pencil : icon === 'plus' ? Plus : Trash2;
  const variantClass =
    variant === 'solid' ? ' is-solid' : variant === 'danger' ? ' is-danger' : variant === 'plain' ? ' is-plain' : '';
  return (
    <button type="button" className={`mp-iconbtn${variantClass}`} onClick={onClick} title={label} aria-label={label}>
      <Glyph size={13} />
    </button>
  );
};

/* ── Card ───────────────────────────────────────────────── */

type CardProps = {
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
  onEdit?: () => void;
  onAdd?: () => void;
  editLabel?: string;
  addLabel?: string;
  children: React.ReactNode;
  id?: string;
};

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  actions,
  onEdit,
  onAdd,
  editLabel,
  addLabel,
  children,
  id,
}) => (
  <section className="mp-card" id={id}>
    {(title || actions || onEdit || onAdd) && (
      <header className="mp-card-head">
        <div style={{ minWidth: 0 }}>
          {title && <h3 className="mp-card-title">{title}</h3>}
          {subtitle && <div className="mp-card-sub">{subtitle}</div>}
        </div>
        <div className="mp-card-actions">
          {actions}
          {onAdd && <IconButton icon="plus" label={addLabel || `Add ${title || 'item'}`} onClick={onAdd} />}
          {onEdit && <IconButton icon="pencil" label={editLabel || `Edit ${title || 'section'}`} onClick={onEdit} />}
        </div>
      </header>
    )}
    {children}
  </section>
);

/* ── Read-only field ────────────────────────────────────── */

export const Field: React.FC<{ label: string; value?: unknown; href?: string; children?: React.ReactNode }> = ({
  label,
  value,
  href,
  children,
}) => {
  const text = display(value);
  const isEmpty = text === EMPTY && !children;
  return (
    <div>
      <span className="mp-field-label">{label}</span>
      <div className={`mp-field-value${isEmpty ? ' is-empty' : ''}`}>
        {children ??
          (href && text !== EMPTY ? (
            <a href={href} target="_blank" rel="noreferrer noopener">
              {text}
            </a>
          ) : (
            text
          ))}
      </div>
    </div>
  );
};

export const FieldGrid: React.FC<{ cols?: 1 | 2 | 3; children: React.ReactNode }> = ({ cols = 2, children }) => (
  <div className={`mp-fields cols-${cols}`}>{children}</div>
);

/* ── Chips ──────────────────────────────────────────────── */

export const Chip: React.FC<{ children: React.ReactNode; accent?: boolean; onRemove?: () => void }> = ({
  children,
  accent,
  onRemove,
}) => (
  <span className={`mp-chip${accent ? ' is-accent' : ''}`}>
    {children}
    {onRemove && (
      <button type="button" className="mp-chip-x" onClick={onRemove} aria-label="Remove">
        <X size={12} />
      </button>
    )}
  </span>
);

export const Pill: React.FC<{ tone: 'primary' | 'ready' | 'draft' | 'info'; children: React.ReactNode }> = ({
  tone,
  children,
}) => <span className={`mp-pill is-${tone}`}>{children}</span>;

/* ── Empty state ────────────────────────────────────────── */

export const EmptyState: React.FC<{
  title?: string;
  text?: string;
  actionLabel?: string;
  onAction?: () => void;
}> = ({ title, text, actionLabel, onAction }) => (
  <div className="mp-empty">
    <div className="mp-empty-art">
      <FolderOpen size={26} />
    </div>
    {title && <div className="mp-empty-title">{title}</div>}
    {text && <div className="mp-empty-text">{text}</div>}
    {actionLabel && onAction && (
      <button type="button" className="mp-btn mp-btn-outline" onClick={onAction}>
        <Plus size={14} /> {actionLabel}
      </button>
    )}
  </div>
);

/* ── Collapsible ("See more") ───────────────────────────── */

export const SeeMore: React.FC<{ children: React.ReactNode; collapsedHeight?: number }> = ({
  children,
  collapsedHeight = 96,
}) => {
  const [open, setOpen] = useState(false);
  const [overflows, setOverflows] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const node = ref.current;
    if (node) setOverflows(node.scrollHeight > collapsedHeight + 8);
  }, [children, collapsedHeight]);

  return (
    <div>
      <div
        ref={ref}
        style={
          open || !overflows
            ? undefined
            : { maxHeight: collapsedHeight, overflow: 'hidden', maskImage: 'linear-gradient(#000 62%, transparent)' }
        }
      >
        {children}
      </div>
      {overflows && (
        <button type="button" className="mp-seemore" onClick={() => setOpen((v) => !v)}>
          {open ? 'See less' : 'See more'}
        </button>
      )}
    </div>
  );
};

/* ── Progress ───────────────────────────────────────────── */

export const ProgressBar: React.FC<{ percentage: number }> = ({ percentage }) => (
  <div
    className="mp-progress-track"
    role="progressbar"
    aria-valuenow={Math.round(percentage)}
    aria-valuemin={0}
    aria-valuemax={100}
    aria-label="Profile completion"
  >
    <div className="mp-progress-fill" style={{ width: `${Math.max(0, Math.min(100, percentage))}%` }} />
  </div>
);

/* ── Stat tile ──────────────────────────────────────────── */

export const StatTile: React.FC<{
  label: string;
  value: string;
  note?: string;
  tone?: 'violet' | 'blue' | 'green' | 'red' | 'amber';
}> = ({ label, value, note, tone = 'blue' }) => (
  <div className={`mp-stat tone-${tone}`}>
    <div className="mp-stat-label">{label}</div>
    <div className="mp-stat-value">{value}</div>
    {note && <div className="mp-stat-note">{note}</div>}
  </div>
);

/* ── Modal ──────────────────────────────────────────────── */

type ModalProps = {
  title: string;
  onClose: () => void;
  onSubmit?: () => void;
  submitLabel?: string;
  busy?: boolean;
  error?: string | null;
  wide?: boolean;
  extraFooter?: React.ReactNode;
  children: React.ReactNode;
};

export const Modal: React.FC<ModalProps> = ({
  title,
  onClose,
  onSubmit,
  submitLabel = 'Save',
  busy,
  error,
  wide,
  extraFooter,
  children,
}) => {
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !busy) onClose();
    };
    document.addEventListener('keydown', onKey);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = previousOverflow;
    };
  }, [onClose, busy]);

  return (
    <div className="mp-modal-scrim" onMouseDown={(e) => e.target === e.currentTarget && !busy && onClose()}>
      <div
        className={`mp-modal${wide ? ' is-wide' : ''}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <header className="mp-modal-head">
          <h3>{title}</h3>
          <button className="mp-iconbtn is-plain" onClick={onClose} aria-label="Close dialog" disabled={busy}>
            <X size={14} />
          </button>
        </header>

        <form
          className="mp-modal-body"
          onSubmit={(event) => {
            event.preventDefault();
            onSubmit?.();
          }}
          id={`mp-form-${title.replace(/\s+/g, '-')}`}
        >
          {error && <div className="mp-modal-error">{error}</div>}
          {children}
        </form>

        <footer className="mp-modal-foot">
          {extraFooter}
          <button type="button" className="mp-btn mp-btn-ghost" onClick={onClose} disabled={busy}>
            Cancel
          </button>
          {onSubmit && (
            <button
              type="submit"
              form={`mp-form-${title.replace(/\s+/g, '-')}`}
              className="mp-btn mp-btn-primary"
              disabled={busy}
            >
              {busy ? <Loader2 size={14} className="mp-spin" /> : <Check size={14} />}
              {busy ? 'Saving...' : submitLabel}
            </button>
          )}
        </footer>
      </div>
    </div>
  );
};

/* ── Confirm dialog ─────────────────────────────────────── */

export const ConfirmDialog: React.FC<{
  title: string;
  message: string;
  confirmLabel?: string;
  busy?: boolean;
  onConfirm: () => void;
  onClose: () => void;
}> = ({ title, message, confirmLabel = 'Delete', busy, onConfirm, onClose }) => (
  <div className="mp-modal-scrim" onMouseDown={(e) => e.target === e.currentTarget && !busy && onClose()}>
    <div className="mp-modal" style={{ maxWidth: 420 }} role="dialog" aria-modal="true" aria-label={title}>
      <header className="mp-modal-head">
        <h3>{title}</h3>
      </header>
      <div className="mp-modal-body">
        <p style={{ margin: 0, fontSize: '0.86rem', color: '#475569' }}>{message}</p>
      </div>
      <footer className="mp-modal-foot">
        <button type="button" className="mp-btn mp-btn-ghost" onClick={onClose} disabled={busy}>
          Cancel
        </button>
        <button
          type="button"
          className="mp-btn mp-btn-primary"
          style={{ background: '#ef4444' }}
          onClick={onConfirm}
          disabled={busy}
        >
          {busy ? <Loader2 size={14} className="mp-spin" /> : <Trash2 size={14} />} {confirmLabel}
        </button>
      </footer>
    </div>
  </div>
);

/* ── Loading ────────────────────────────────────────────── */

export const Loading: React.FC<{ label?: string }> = ({ label = 'Loading your profile...' }) => (
  <div className="mp-loading">
    <Loader2 size={18} className="mp-spin" /> {label}
  </div>
);

/* ── Pagination ─────────────────────────────────────────── */

export const Pager: React.FC<{
  page: number;
  pageCount: number;
  pageSize: number;
  onPage: (page: number) => void;
  onPageSize: (size: number) => void;
}> = ({ page, pageCount, pageSize, onPage, onPageSize }) => (
  <div className="mp-pager">
    <span>Rows per page</span>
    <select
      value={pageSize}
      onChange={(e) => onPageSize(Number(e.target.value))}
      aria-label="Rows per page"
    >
      {[5, 10, 25, 50].map((size) => (
        <option key={size} value={size}>
          {size}
        </option>
      ))}
    </select>
    <button className="mp-pager-btn" onClick={() => onPage(page - 1)} disabled={page <= 1} aria-label="Previous page">
      <ChevronLeft size={14} />
    </button>
    <span className="mp-pager-btn is-current">{page}</span>
    <button
      className="mp-pager-btn"
      onClick={() => onPage(page + 1)}
      disabled={page >= pageCount}
      aria-label="Next page"
    >
      <ChevronRight size={14} />
    </button>
  </div>
);

/** Slices a list for the current page and keeps the page in range. */
export const usePaged = <T,>(items: T[], initialSize = 10) => {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialSize);
  const pageCount = Math.max(1, Math.ceil(items.length / pageSize));

  useEffect(() => {
    if (page > pageCount) setPage(pageCount);
  }, [page, pageCount]);

  const slice = useMemo(
    () => items.slice((page - 1) * pageSize, (page - 1) * pageSize + pageSize),
    [items, page, pageSize],
  );

  return {
    slice,
    page,
    pageCount,
    pageSize,
    setPage,
    setPageSize: (size: number) => {
      setPageSize(size);
      setPage(1);
    },
  };
};
