/**
 * Form controls used inside the profile edit dialogs.
 * All controlled, all keyboard accessible, no external form library.
 */
import React, { useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';

/* ── Layout ─────────────────────────────────────────────── */

export const FormGrid: React.FC<{ cols?: 1 | 2; children: React.ReactNode }> = ({ cols = 2, children }) => (
  <div className={`mp-form-grid${cols === 1 ? ' cols-1' : ''}`}>{children}</div>
);

export const Span2: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="span-2">{children}</div>
);

export const FieldsetTitle: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="mp-fieldset-title span-2">{children}</div>
);

/* ── Text / number / select / textarea ──────────────────── */

type BaseProps = {
  label: string;
  required?: boolean;
  hint?: string;
  span?: boolean;
};

export const TextField: React.FC<
  BaseProps & {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    type?: 'text' | 'url' | 'email' | 'tel' | 'date' | 'month';
    maxLength?: number;
  }
> = ({ label, value, onChange, placeholder, type = 'text', required, hint, span, maxLength }) => (
  <div className={span ? 'span-2' : undefined}>
    <label className="mp-input-label">
      {label} {required && <span className="mp-req">*</span>}
    </label>
    <input
      className="mp-input"
      type={type}
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      required={required}
      maxLength={maxLength}
    />
    {hint && <div className="mp-hint">{hint}</div>}
  </div>
);

export const NumberField: React.FC<
  BaseProps & {
    value: number | null | undefined;
    onChange: (value: number | null) => void;
    placeholder?: string;
    min?: number;
    max?: number;
    step?: number;
  }
> = ({ label, value, onChange, placeholder, min, max, step = 1, required, hint, span }) => (
  <div className={span ? 'span-2' : undefined}>
    <label className="mp-input-label">
      {label} {required && <span className="mp-req">*</span>}
    </label>
    <input
      className="mp-input"
      type="number"
      value={value === null || value === undefined ? '' : value}
      onChange={(e) => onChange(e.target.value === '' ? null : Number(e.target.value))}
      placeholder={placeholder}
      min={min}
      max={max}
      step={step}
      required={required}
    />
    {hint && <div className="mp-hint">{hint}</div>}
  </div>
);

export const TextAreaField: React.FC<
  BaseProps & { value: string; onChange: (value: string) => void; placeholder?: string; rows?: number; maxLength?: number }
> = ({ label, value, onChange, placeholder, rows = 4, required, hint, span = true, maxLength }) => (
  <div className={span ? 'span-2' : undefined}>
    <label className="mp-input-label">
      {label} {required && <span className="mp-req">*</span>}
    </label>
    <textarea
      className="mp-textarea"
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      rows={rows}
      required={required}
      maxLength={maxLength}
    />
    {hint && <div className="mp-hint">{hint}</div>}
  </div>
);

/** Options may be plain strings or `{value,label}` pairs when the stored value
 *  isn't what the student should read (e.g. `custom_event` -> "Custom event"). */
export type SelectOption = string | { value: string; label: string };

export const SelectField: React.FC<
  BaseProps & { value: string; onChange: (value: string) => void; options: SelectOption[]; allowBlank?: boolean }
> = ({ label, value, onChange, options, required, hint, span, allowBlank = true }) => (
  <div className={span ? 'span-2' : undefined}>
    <label className="mp-input-label">
      {label} {required && <span className="mp-req">*</span>}
    </label>
    <select className="mp-select" value={value ?? ''} onChange={(e) => onChange(e.target.value)} required={required}>
      {allowBlank && <option value="">Select...</option>}
      {options.map((option) => {
        const optionValue = typeof option === 'string' ? option : option.value;
        const optionLabel = typeof option === 'string' ? option : option.label;
        return (
          <option key={optionValue} value={optionValue}>
            {optionLabel}
          </option>
        );
      })}
    </select>
    {hint && <div className="mp-hint">{hint}</div>}
  </div>
);

export const CheckboxField: React.FC<{
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  span?: boolean;
}> = ({ label, checked, onChange, span }) => (
  <div className={span ? 'span-2' : undefined}>
    <label className="mp-check">
      <input type="checkbox" checked={!!checked} onChange={(e) => onChange(e.target.checked)} />
      {label}
    </label>
  </div>
);

/* ── Tag input ──────────────────────────────────────────── */

export const TagInput: React.FC<{
  label: string;
  values: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
  suggestions?: string[];
  hint?: string;
  span?: boolean;
}> = ({ label, values, onChange, placeholder = 'Type and press Enter', suggestions = [], hint, span = true }) => {
  const [draft, setDraft] = useState('');

  const add = (raw: string) => {
    const name = raw.trim();
    if (!name) return;
    if (values.some((v) => v.toLowerCase() === name.toLowerCase())) {
      setDraft('');
      return;
    }
    onChange([...values, name]);
    setDraft('');
  };

  const unused = suggestions.filter((s) => !values.some((v) => v.toLowerCase() === s.toLowerCase())).slice(0, 10);

  return (
    <div className={span ? 'span-2' : undefined}>
      <label className="mp-input-label">{label}</label>
      <div className="mp-taginput">
        {values.map((value) => (
          <span key={value} className="mp-chip">
            {value}
            <button
              type="button"
              className="mp-chip-x"
              onClick={() => onChange(values.filter((v) => v !== value))}
              aria-label={`Remove ${value}`}
            >
              <Trash2 size={11} />
            </button>
          </span>
        ))}
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ',') {
              e.preventDefault();
              add(draft);
            } else if (e.key === 'Backspace' && !draft && values.length) {
              onChange(values.slice(0, -1));
            }
          }}
          onBlur={() => add(draft)}
          placeholder={values.length ? '' : placeholder}
          aria-label={label}
        />
      </div>
      {hint && <div className="mp-hint">{hint}</div>}
      {unused.length > 0 && (
        <div className="mp-suggestions">
          {unused.map((s) => (
            <button key={s} type="button" className="mp-suggestion" onClick={() => add(s)}>
              + {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

/* ── Bullet list editor (string[]) ──────────────────────── */

export const BulletEditor: React.FC<{
  label: string;
  values: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
  addLabel?: string;
}> = ({ label, values, onChange, placeholder = 'Describe one achievement', addLabel = 'Add point' }) => {
  const update = (index: number, value: string) => onChange(values.map((v, i) => (i === index ? value : v)));

  return (
    <div className="span-2">
      <label className="mp-input-label">{label}</label>
      <div className="mp-repeat">
        {values.map((value, index) => (
          <div className="mp-repeat-row" key={index}>
            <input
              className="mp-input"
              value={value}
              onChange={(e) => update(index, e.target.value)}
              placeholder={placeholder}
            />
            <button
              type="button"
              className="mp-iconbtn is-danger"
              onClick={() => onChange(values.filter((_, i) => i !== index))}
              aria-label="Remove point"
            >
              <Trash2 size={13} />
            </button>
          </div>
        ))}
        <button type="button" className="mp-btn mp-btn-ghost mp-btn-sm" onClick={() => onChange([...values, ''])}>
          <Plus size={13} /> {addLabel}
        </button>
      </div>
    </div>
  );
};

/* ── Label/value pair editor ────────────────────────────── */

export type PairRow = { label: string; value: string };

export const PairEditor: React.FC<{
  label: string;
  rows: PairRow[];
  onChange: (rows: PairRow[]) => void;
  labelPlaceholder?: string;
  valuePlaceholder?: string;
  addLabel?: string;
}> = ({
  label,
  rows,
  onChange,
  labelPlaceholder = 'Label',
  valuePlaceholder = 'Value',
  addLabel = 'Add row',
}) => {
  const update = (index: number, patch: Partial<PairRow>) =>
    onChange(rows.map((row, i) => (i === index ? { ...row, ...patch } : row)));

  return (
    <div className="span-2">
      <label className="mp-input-label">{label}</label>
      <div className="mp-repeat">
        {rows.map((row, index) => (
          <div className="mp-repeat-row" key={index}>
            <div className="mp-repeat-grid" style={{ gridTemplateColumns: '1fr 1.4fr' }}>
              <input
                className="mp-input"
                value={row.label}
                onChange={(e) => update(index, { label: e.target.value })}
                placeholder={labelPlaceholder}
              />
              <input
                className="mp-input"
                value={row.value}
                onChange={(e) => update(index, { value: e.target.value })}
                placeholder={valuePlaceholder}
              />
            </div>
            <button
              type="button"
              className="mp-iconbtn is-danger"
              onClick={() => onChange(rows.filter((_, i) => i !== index))}
              aria-label="Remove row"
            >
              <Trash2 size={13} />
            </button>
          </div>
        ))}
        <button
          type="button"
          className="mp-btn mp-btn-ghost mp-btn-sm"
          onClick={() => onChange([...rows, { label: '', value: '' }])}
        >
          <Plus size={13} /> {addLabel}
        </button>
      </div>
    </div>
  );
};

/* ── Link list editor ({label, url}) ────────────────────── */

export type LinkRow = { label: string; url: string };

export const LinkEditor: React.FC<{
  label: string;
  rows: LinkRow[];
  onChange: (rows: LinkRow[]) => void;
}> = ({ label, rows, onChange }) => {
  const update = (index: number, patch: Partial<LinkRow>) =>
    onChange(rows.map((row, i) => (i === index ? { ...row, ...patch } : row)));

  return (
    <div className="span-2">
      <label className="mp-input-label">{label}</label>
      <div className="mp-repeat">
        {rows.map((row, index) => (
          <div className="mp-repeat-row" key={index}>
            <div className="mp-repeat-grid" style={{ gridTemplateColumns: '1fr 1.6fr' }}>
              <input
                className="mp-input"
                value={row.label}
                onChange={(e) => update(index, { label: e.target.value })}
                placeholder="Name (e.g. Portfolio)"
              />
              <input
                className="mp-input"
                type="url"
                value={row.url}
                onChange={(e) => update(index, { url: e.target.value })}
                placeholder="https://"
              />
            </div>
            <button
              type="button"
              className="mp-iconbtn is-danger"
              onClick={() => onChange(rows.filter((_, i) => i !== index))}
              aria-label="Remove link"
            >
              <Trash2 size={13} />
            </button>
          </div>
        ))}
        <button
          type="button"
          className="mp-btn mp-btn-ghost mp-btn-sm"
          onClick={() => onChange([...rows, { label: '', url: '' }])}
        >
          <Plus size={13} /> Add link
        </button>
      </div>
    </div>
  );
};

/* ── Semester editor ────────────────────────────────────── */

export type SemesterRow = {
  semester: string;
  cgpa: number | null;
  ongoing_backlogs: number | null;
  total_backlogs: number | null;
  marksheet_doc_id?: string | null;
};

export const emptySemester = (index: number): SemesterRow => ({
  semester: `Sem ${index + 1}`,
  cgpa: null,
  ongoing_backlogs: null,
  total_backlogs: null,
  marksheet_doc_id: null,
});

export const SemesterEditor: React.FC<{
  rows: SemesterRow[];
  onChange: (rows: SemesterRow[]) => void;
  marksheets?: { id: string; label: string }[];
}> = ({ rows, onChange, marksheets = [] }) => {
  const update = (index: number, patch: Partial<SemesterRow>) =>
    onChange(rows.map((row, i) => (i === index ? { ...row, ...patch } : row)));

  return (
    <div className="span-2">
      <label className="mp-input-label">Semester wise performance</label>
      <div className="mp-repeat">
        {rows.map((row, index) => (
          <div className="mp-repeat-row" key={index}>
            <div
              className="mp-repeat-grid"
              style={{ gridTemplateColumns: marksheets.length ? '1fr 0.8fr 0.8fr 0.8fr 1.2fr' : '1fr 0.8fr 0.8fr 0.8fr' }}
            >
              <input
                className="mp-input"
                value={row.semester}
                onChange={(e) => update(index, { semester: e.target.value })}
                placeholder="Sem 1"
                aria-label="Semester name"
              />
              <input
                className="mp-input"
                type="number"
                step="0.01"
                min={0}
                max={10}
                value={row.cgpa ?? ''}
                onChange={(e) => update(index, { cgpa: e.target.value === '' ? null : Number(e.target.value) })}
                placeholder="CGPA"
                aria-label="Semester CGPA"
              />
              <input
                className="mp-input"
                type="number"
                min={0}
                value={row.ongoing_backlogs ?? ''}
                onChange={(e) =>
                  update(index, { ongoing_backlogs: e.target.value === '' ? null : Number(e.target.value) })
                }
                placeholder="Ongoing"
                aria-label="Ongoing backlogs"
              />
              <input
                className="mp-input"
                type="number"
                min={0}
                value={row.total_backlogs ?? ''}
                onChange={(e) =>
                  update(index, { total_backlogs: e.target.value === '' ? null : Number(e.target.value) })
                }
                placeholder="Total"
                aria-label="Total backlogs"
              />
              {marksheets.length > 0 && (
                <select
                  className="mp-select"
                  value={row.marksheet_doc_id ?? ''}
                  onChange={(e) => update(index, { marksheet_doc_id: e.target.value || null })}
                  aria-label="Marksheet document"
                >
                  <option value="">No marksheet</option>
                  {marksheets.map((doc) => (
                    <option key={doc.id} value={doc.id}>
                      {doc.label}
                    </option>
                  ))}
                </select>
              )}
            </div>
            <button
              type="button"
              className="mp-iconbtn is-danger"
              onClick={() => onChange(rows.filter((_, i) => i !== index))}
              aria-label="Remove semester"
            >
              <Trash2 size={13} />
            </button>
          </div>
        ))}
        <button
          type="button"
          className="mp-btn mp-btn-ghost mp-btn-sm"
          onClick={() => onChange([...rows, emptySemester(rows.length)])}
        >
          <Plus size={13} /> Add semester
        </button>
      </div>
      <div className="mp-hint">Leave a field blank to show "--" on your profile.</div>
    </div>
  );
};

/* ── Training editor ────────────────────────────────────── */

export type TrainingRow = { name: string; status: string; score: string; notes: string };

export const TrainingEditor: React.FC<{
  rows: TrainingRow[];
  onChange: (rows: TrainingRow[]) => void;
}> = ({ rows, onChange }) => {
  const update = (index: number, patch: Partial<TrainingRow>) =>
    onChange(rows.map((row, i) => (i === index ? { ...row, ...patch } : row)));

  return (
    <div className="span-2">
      <label className="mp-input-label">Training modules</label>
      <div className="mp-repeat">
        {rows.map((row, index) => (
          <div className="mp-repeat-card" key={index}>
            <div className="mp-repeat-row">
              <div className="mp-repeat-grid" style={{ gridTemplateColumns: '1.3fr 1fr 0.7fr' }}>
                <input
                  className="mp-input"
                  value={row.name}
                  onChange={(e) => update(index, { name: e.target.value })}
                  placeholder="Module name"
                  aria-label="Module name"
                />
                <select
                  className="mp-select"
                  value={row.status}
                  onChange={(e) => update(index, { status: e.target.value })}
                  aria-label="Status"
                >
                  <option value="">Status...</option>
                  <option value="Completed">Completed</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Not Started">Not Started</option>
                </select>
                <input
                  className="mp-input"
                  value={row.score}
                  onChange={(e) => update(index, { score: e.target.value })}
                  placeholder="Score"
                  aria-label="Score"
                />
              </div>
              <button
                type="button"
                className="mp-iconbtn is-danger"
                onClick={() => onChange(rows.filter((_, i) => i !== index))}
                aria-label="Remove module"
              >
                <Trash2 size={13} />
              </button>
            </div>
            <input
              className="mp-input"
              style={{ marginTop: '0.5rem' }}
              value={row.notes}
              onChange={(e) => update(index, { notes: e.target.value })}
              placeholder="Notes (optional)"
              aria-label="Notes"
            />
          </div>
        ))}
        <button
          type="button"
          className="mp-btn mp-btn-ghost mp-btn-sm"
          onClick={() => onChange([...rows, { name: '', status: '', score: '', notes: '' }])}
        >
          <Plus size={13} /> Add module
        </button>
      </div>
    </div>
  );
};
