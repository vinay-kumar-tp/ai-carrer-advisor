import React, { useMemo, useState } from 'react';
import { X, ShieldCheck, Send } from 'lucide-react';
import type { ApplyQuestion, JobDetail, Prefill } from './types';

type Props = {
  job: JobDetail;
  onClose: () => void;
  onSubmit: (answers: Record<string, any>) => Promise<void>;
};

const prefillRows = (p: Prefill): { k: string; v: string }[] => {
  const rows: { k: string; v: string }[] = [
    { k: 'Full name', v: p.full_name },
    { k: 'Email', v: p.email },
    { k: 'Phone', v: p.phone || '—' },
    { k: 'Location', v: p.location || '—' },
    { k: 'Institute', v: p.current_institute || '—' },
    { k: 'Degree', v: [p.degree, p.specialization].filter(Boolean).join(' · ') || '—' },
    { k: 'Graduation', v: p.graduation_year || '—' },
    { k: 'CGPA', v: p.cgpa != null ? String(p.cgpa) : '—' },
    { k: 'Experience', v: `${p.total_experience_years} yr` },
  ];
  return rows.filter((r) => r.v && r.v !== '');
};

export const ApplyModal: React.FC<Props> = ({ job, onClose, onSubmit }) => {
  const questions = job.apply_questions || [];
  const [answers, setAnswers] = useState<Record<string, any>>(() => {
    const init: Record<string, any> = {};
    for (const q of questions) {
      if (q.type === 'multiselect') init[q.key] = [];
      else if (q.type === 'boolean') init[q.key] = null;
      else init[q.key] = '';
    }
    // Sensible autofill for a couple of known keys.
    if ('expected_ctc' in init && job.prefill.expected_ctc)
      init['expected_ctc'] = Math.round((job.prefill.expected_ctc || 0) / 100000) || '';
    if ('willing_to_relocate' in init) init['willing_to_relocate'] = job.prefill.willing_to_relocate;
    if ('portfolio_link' in init) init['portfolio_link'] = job.prefill.portfolio_url || job.prefill.github_url || '';
    return init;
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const set = (key: string, value: any) => setAnswers((a) => ({ ...a, [key]: value }));

  const rows = useMemo(() => prefillRows(job.prefill), [job.prefill]);

  const missingRequired = questions.filter((q) => {
    if (!q.required) return false;
    const v = answers[q.key];
    if (q.type === 'boolean') return v === null || v === undefined;
    if (q.type === 'multiselect') return !Array.isArray(v) || v.length === 0;
    return v === '' || v === undefined || v === null;
  });

  const submit = async () => {
    setError('');
    if (missingRequired.length) {
      setError(`Please complete: ${missingRequired.map((q) => q.label).join(', ')}`);
      return;
    }
    setSubmitting(true);
    try {
      await onSubmit(answers);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Application failed. Please try again.');
      setSubmitting(false);
    }
  };

  const renderField = (q: ApplyQuestion) => {
    const v = answers[q.key];
    switch (q.type) {
      case 'textarea':
        return (
          <textarea
            className="input-field"
            placeholder={q.placeholder}
            value={v || ''}
            onChange={(e) => set(q.key, e.target.value)}
          />
        );
      case 'number':
        return (
          <input
            type="number"
            className="input-field"
            placeholder={q.placeholder}
            value={v ?? ''}
            onChange={(e) => set(q.key, e.target.value)}
          />
        );
      case 'url':
        return (
          <input
            type="url"
            className="input-field"
            placeholder={q.placeholder || 'https://'}
            value={v || ''}
            onChange={(e) => set(q.key, e.target.value)}
          />
        );
      case 'date':
        return (
          <input
            type="date"
            className="input-field"
            value={v || ''}
            onChange={(e) => set(q.key, e.target.value)}
          />
        );
      case 'select':
        return (
          <select className="jb-select" value={v || ''} onChange={(e) => set(q.key, e.target.value)}>
            <option value="">Select...</option>
            {(q.options || []).map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        );
      case 'multiselect':
        return (
          <div className="jb-multi">
            {(q.options || []).map((o) => {
              const active = Array.isArray(v) && v.includes(o);
              return (
                <button
                  key={o}
                  type="button"
                  className={`jb-chip${active ? ' active' : ''}`}
                  onClick={() =>
                    set(
                      q.key,
                      active ? (v as string[]).filter((x) => x !== o) : [...(v || []), o],
                    )
                  }
                >
                  {o}
                </button>
              );
            })}
          </div>
        );
      case 'boolean':
        return (
          <div className="jb-bool-row">
            <button
              type="button"
              className={`jb-bool-btn${v === true ? ' active' : ''}`}
              onClick={() => set(q.key, true)}
            >
              Yes
            </button>
            <button
              type="button"
              className={`jb-bool-btn${v === false ? ' active' : ''}`}
              onClick={() => set(q.key, false)}
            >
              No
            </button>
          </div>
        );
      default:
        return (
          <input
            type="text"
            className="input-field"
            placeholder={q.placeholder}
            value={v || ''}
            onChange={(e) => set(q.key, e.target.value)}
          />
        );
    }
  };

  return (
    <div className="jb-modal-overlay" onClick={onClose}>
      <div className="jb-modal" onClick={(e) => e.stopPropagation()}>
        <button className="jb-modal-close" onClick={onClose} aria-label="Close">
          <X size={16} />
        </button>
        <h3>Apply to {job.title}</h3>
        <p className="sub">
          {job.company} · via {job.source_portal}
        </p>

        <div className="jb-autofill-note">
          <ShieldCheck size={14} /> Auto-filled from your profile
        </div>
        <div className="jb-prefill-grid">
          {rows.map((r) => (
            <div className="jb-prefill-item" key={r.k}>
              <div className="k">{r.k}</div>
              <div className="v">{r.v}</div>
            </div>
          ))}
        </div>

        {questions.length > 0 && (
          <>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, margin: '0.25rem 0 0.75rem' }}>
              Additional questions
            </div>
            {questions.map((q) => (
              <div className="jb-field" key={q.key}>
                <label>
                  {q.label} {q.required && <span className="req">*</span>}
                </label>
                {renderField(q)}
                {q.help && <div className="help">{q.help}</div>}
              </div>
            ))}
          </>
        )}

        {error && <div className="jb-blocked">{error}</div>}

        <div className="jb-modal-foot">
          <button className="btn" onClick={onClose} disabled={submitting}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={submit} disabled={submitting}>
            <Send size={15} style={{ verticalAlign: -2, marginRight: 6 }} />
            {submitting ? 'Submitting...' : 'Submit Application'}
          </button>
        </div>
      </div>
    </div>
  );
};
