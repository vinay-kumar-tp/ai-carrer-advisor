import React, { useEffect, useRef, useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import type { JdOption } from './types';

type Props = {
  options: JdOption[];
  selectedIds: string[];
  max?: number;
  onToggle: (id: string) => void;
};

/** "Select up to 3 job descriptions" multi-select from the design. */
export const JdSelect: React.FC<Props> = ({ options, selectedIds, max = 3, onToggle }) => {
  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement>(null);

  // Close on outside click / Escape so it behaves like a native select.
  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('mousedown', onDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  const atLimit = selectedIds.length >= max;
  const summary =
    selectedIds.length === 0
      ? `Select up to ${max} job descriptions`
      : `${selectedIds.length} job description${selectedIds.length > 1 ? 's' : ''} selected`;

  return (
    <div className="pai-select" ref={wrapRef}>
      <button
        type="button"
        className={`pai-select-control${open ? ' is-open' : ''}`}
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <span className={selectedIds.length === 0 ? 'pai-select-placeholder' : undefined}>{summary}</span>
        {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {open && (
        <div className="pai-select-menu" role="listbox" aria-multiselectable="true">
          {options.length === 0 && <div className="pai-select-empty">No job descriptions available yet.</div>}
          {options.map((opt) => {
            const selected = selectedIds.includes(opt.id);
            const meta = [opt.company, opt.location, `${opt.required_skills_count} required skills`]
              .filter(Boolean)
              .join(' · ');
            return (
              <button
                key={opt.id}
                type="button"
                role="option"
                aria-selected={selected}
                disabled={!selected && atLimit}
                className={`pai-option${selected ? ' is-selected' : ''}`}
                onClick={() => onToggle(opt.id)}
              >
                <div className="pai-option-title">{opt.title}</div>
                <div className="pai-option-meta">{meta}</div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
