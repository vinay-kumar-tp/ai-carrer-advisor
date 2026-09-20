import React, { useMemo, useState } from 'react';
import { CheckCircle2, ShieldCheck, Ticket, X } from 'lucide-react';
import type { EventDetail, EventQuestion } from './types';
import { formatEventDate, formatPrice } from './types';

type Props = {
  event: EventDetail;
  onClose: () => void;
  onSubmit: (payload: Record<string, any>) => Promise<void>;
};

type Step = 'attendee' | 'extra' | 'confirm';

const GRAD_YEARS = Array.from({ length: 9 }, (_, i) => String(new Date().getFullYear() - 2 + i));

const EXPERIENCE_LEVELS = ['Fresher / Student', '0-1 years', '1-3 years', '3-5 years', '5+ years'];
const HEARD_FROM = [
  'Carrerpulse Ai',
  'College / University',
  'LinkedIn',
  'Friend or colleague',
  'Company website',
  'Other',
];
const TSHIRT_SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL'];
const DIETARY = ['No preference', 'Vegetarian', 'Vegan', 'Jain', 'Halal', 'Gluten free'];

export const RegisterModal: React.FC<Props> = ({ event, onClose, onSubmit }) => {
  const p = event.prefill || {};
  const needsOnsiteInfo = event.mode !== 'Online';

  const [step, setStep] = useState<Step>('attendee');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [form, setForm] = useState({
    full_name: p.full_name || '',
    email: p.email || '',
    phone: p.phone || '',
    organization: p.current_institute || '',
    designation: p.headline || '',
    degree: p.degree || '',
    branch: p.specialization || '',
    graduation_year: p.graduation_year ? String(p.graduation_year) : '',
    experience_level: 'Fresher / Student',
    city: p.location || '',
    country: 'India',
    linkedin_url: p.linkedin_url || '',
    github_url: p.github_url || '',
    portfolio_url: p.portfolio_url || '',
    resume_url: '',
    heard_from: 'Carrerpulse Ai',
    dietary_preference: needsOnsiteInfo ? 'No preference' : '',
    tshirt_size: '',
    accessibility_needs: '',
    emergency_contact: '',
    motivation: '',
    consent_updates: true,
    agree_terms: false,
  });

  const questions = event.registration_questions || [];
  const [answers, setAnswers] = useState<Record<string, any>>(() => {
    const init: Record<string, any> = {};
    for (const q of questions) {
      if (q.type === 'multiselect') init[q.key] = [];
      else if (q.type === 'boolean') init[q.key] = null;
      else init[q.key] = '';
    }
    if ('repo_url' in init) init.repo_url = p.github_url || '';
    return init;
  });

  const set = (key: string, value: any) => setForm((f) => ({ ...f, [key]: value }));
  const setAnswer = (key: string, value: any) => setAnswers((a) => ({ ...a, [key]: value }));

  const attendeeErrors = useMemo(() => {
    const errs: string[] = [];
    if (!form.full_name.trim() || form.full_name.trim().length < 2) errs.push('Full name');
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errs.push('A valid email address');
    if (form.phone.replace(/\D/g, '').length < 6) errs.push('Phone number');
    if (!form.organization.trim()) errs.push('College or organisation');
    if (needsOnsiteInfo && !form.emergency_contact.trim()) errs.push('Emergency contact');
    return errs;
  }, [form, needsOnsiteInfo]);

  const missingQuestions = useMemo(
    () =>
      questions.filter((q) => {
        if (!q.required) return false;
        const v = answers[q.key];
        if (q.type === 'boolean') return v === null || v === undefined;
        if (q.type === 'multiselect') return !Array.isArray(v) || v.length === 0;
        return v === '' || v === undefined || v === null;
      }),
    [questions, answers],
  );

  const goNext = () => {
    setError('');
    if (step === 'attendee') {
      if (attendeeErrors.length) {
        setError(`Please complete: ${attendeeErrors.join(', ')}`);
        return;
      }
      setStep(questions.length ? 'extra' : 'confirm');
      return;
    }
    if (step === 'extra') {
      if (missingQuestions.length) {
        setError(`Please complete: ${missingQuestions.map((q) => q.label).join(', ')}`);
        return;
      }
      setStep('confirm');
    }
  };

  const goBack = () => {
    setError('');
    if (step === 'confirm') setStep(questions.length ? 'extra' : 'attendee');
    else if (step === 'extra') setStep('attendee');
  };

  const submit = async () => {
    setError('');
    if (!form.agree_terms) {
      setError('Please accept the event terms and code of conduct.');
      return;
    }
    setSubmitting(true);
    try {
      await onSubmit({
        ...form,
        graduation_year: form.graduation_year ? Number(form.graduation_year) : null,
        answers,
      });
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Registration failed. Please try again.');
      setSubmitting(false);
    }
  };

  const renderQuestion = (q: EventQuestion) => {
    const v = answers[q.key];
    switch (q.type) {
      case 'textarea':
        return (
          <textarea
            className="ev-input"
            rows={3}
            placeholder={q.placeholder}
            value={v || ''}
            onChange={(e) => setAnswer(q.key, e.target.value)}
          />
        );
      case 'number':
        return (
          <input
            type="number"
            className="ev-input"
            placeholder={q.placeholder}
            value={v ?? ''}
            onChange={(e) => setAnswer(q.key, e.target.value)}
          />
        );
      case 'url':
        return (
          <input
            type="url"
            className="ev-input"
            placeholder={q.placeholder || 'https://'}
            value={v || ''}
            onChange={(e) => setAnswer(q.key, e.target.value)}
          />
        );
      case 'date':
        return (
          <input
            type="date"
            className="ev-input"
            value={v || ''}
            onChange={(e) => setAnswer(q.key, e.target.value)}
          />
        );
      case 'select':
        return (
          <select className="ev-input" value={v || ''} onChange={(e) => setAnswer(q.key, e.target.value)}>
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
          <div className="ev-chip-row">
            {(q.options || []).map((o) => {
              const active = Array.isArray(v) && v.includes(o);
              return (
                <button
                  key={o}
                  type="button"
                  className={`ev-choice${active ? ' is-active' : ''}`}
                  aria-pressed={active}
                  onClick={() =>
                    setAnswer(q.key, active ? (v as string[]).filter((x) => x !== o) : [...(v || []), o])
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
          <div className="ev-bool-row">
            <button
              type="button"
              className={`ev-choice${v === true ? ' is-active' : ''}`}
              onClick={() => setAnswer(q.key, true)}
            >
              Yes
            </button>
            <button
              type="button"
              className={`ev-choice${v === false ? ' is-active' : ''}`}
              onClick={() => setAnswer(q.key, false)}
            >
              No
            </button>
          </div>
        );
      default:
        return (
          <input
            type="text"
            className="ev-input"
            placeholder={q.placeholder}
            value={v || ''}
            onChange={(e) => setAnswer(q.key, e.target.value)}
          />
        );
    }
  };

  const steps: { key: Step; label: string }[] = [
    { key: 'attendee', label: 'Your details' },
    ...(questions.length ? ([{ key: 'extra', label: 'Event questions' }] as { key: Step; label: string }[]) : []),
    { key: 'confirm', label: 'Confirm' },
  ];
  const stepIndex = steps.findIndex((s) => s.key === step);

  return (
    <div className="ev-modal-overlay" onClick={onClose} role="presentation">
      <div
        className="ev-modal cp-pop"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={`Register for ${event.title}`}
      >
        <button className="ev-modal-close" onClick={onClose} aria-label="Close">
          <X size={16} />
        </button>

        <div className="ev-modal-head">
          <h3>Register — {event.title}</h3>
          <p>
            {event.host_company} · {formatEventDate(event.event_date)} · {event.mode} ·{' '}
            {formatPrice(event.price, event.currency)}
          </p>
        </div>

        <ol className="ev-steps" aria-label="Registration steps">
          {steps.map((s, i) => (
            <li key={s.key} className={`ev-step${i === stepIndex ? ' is-active' : ''}${i < stepIndex ? ' is-done' : ''}`}>
              <span className="ev-step-dot">{i < stepIndex ? <CheckCircle2 size={12} /> : i + 1}</span>
              {s.label}
            </li>
          ))}
        </ol>

        {step === 'attendee' && (
          <div className="ev-form">
            <div className="ev-autofill">
              <ShieldCheck size={14} /> Pre-filled from your profile — edit anything that looks off.
            </div>

            <div className="ev-field-grid">
              <div className="ev-field">
                <label htmlFor="ev-name">
                  Full name <span className="req">*</span>
                </label>
                <input
                  id="ev-name"
                  className="ev-input"
                  value={form.full_name}
                  onChange={(e) => set('full_name', e.target.value)}
                />
              </div>
              <div className="ev-field">
                <label htmlFor="ev-email">
                  Email <span className="req">*</span>
                </label>
                <input
                  id="ev-email"
                  type="email"
                  className="ev-input"
                  value={form.email}
                  onChange={(e) => set('email', e.target.value)}
                />
              </div>
              <div className="ev-field">
                <label htmlFor="ev-phone">
                  Phone <span className="req">*</span>
                </label>
                <input
                  id="ev-phone"
                  className="ev-input"
                  placeholder="+91 98765 43210"
                  value={form.phone}
                  onChange={(e) => set('phone', e.target.value)}
                />
              </div>
              <div className="ev-field">
                <label htmlFor="ev-org">
                  College / organisation <span className="req">*</span>
                </label>
                <input
                  id="ev-org"
                  className="ev-input"
                  value={form.organization}
                  onChange={(e) => set('organization', e.target.value)}
                />
              </div>
              <div className="ev-field">
                <label htmlFor="ev-degree">Degree</label>
                <input
                  id="ev-degree"
                  className="ev-input"
                  placeholder="B.Tech"
                  value={form.degree}
                  onChange={(e) => set('degree', e.target.value)}
                />
              </div>
              <div className="ev-field">
                <label htmlFor="ev-branch">Branch / specialisation</label>
                <input
                  id="ev-branch"
                  className="ev-input"
                  placeholder="Computer Science"
                  value={form.branch}
                  onChange={(e) => set('branch', e.target.value)}
                />
              </div>
              <div className="ev-field">
                <label htmlFor="ev-gradyear">Graduation year</label>
                <select
                  id="ev-gradyear"
                  className="ev-input"
                  value={form.graduation_year}
                  onChange={(e) => set('graduation_year', e.target.value)}
                >
                  <option value="">Select...</option>
                  {GRAD_YEARS.map((y) => (
                    <option key={y} value={y}>
                      {y}
                    </option>
                  ))}
                </select>
              </div>
              <div className="ev-field">
                <label htmlFor="ev-exp">Experience level</label>
                <select
                  id="ev-exp"
                  className="ev-input"
                  value={form.experience_level}
                  onChange={(e) => set('experience_level', e.target.value)}
                >
                  {EXPERIENCE_LEVELS.map((l) => (
                    <option key={l} value={l}>
                      {l}
                    </option>
                  ))}
                </select>
              </div>
              <div className="ev-field">
                <label htmlFor="ev-city">City</label>
                <input
                  id="ev-city"
                  className="ev-input"
                  value={form.city}
                  onChange={(e) => set('city', e.target.value)}
                />
              </div>
              <div className="ev-field">
                <label htmlFor="ev-country">Country</label>
                <input
                  id="ev-country"
                  className="ev-input"
                  value={form.country}
                  onChange={(e) => set('country', e.target.value)}
                />
              </div>
              <div className="ev-field">
                <label htmlFor="ev-linkedin">LinkedIn</label>
                <input
                  id="ev-linkedin"
                  type="url"
                  className="ev-input"
                  placeholder="https://linkedin.com/in/..."
                  value={form.linkedin_url}
                  onChange={(e) => set('linkedin_url', e.target.value)}
                />
              </div>
              <div className="ev-field">
                <label htmlFor="ev-github">GitHub</label>
                <input
                  id="ev-github"
                  type="url"
                  className="ev-input"
                  placeholder="https://github.com/..."
                  value={form.github_url}
                  onChange={(e) => set('github_url', e.target.value)}
                />
              </div>
              <div className="ev-field">
                <label htmlFor="ev-resume">Resume link</label>
                <input
                  id="ev-resume"
                  type="url"
                  className="ev-input"
                  placeholder="Drive or portfolio link"
                  value={form.resume_url}
                  onChange={(e) => set('resume_url', e.target.value)}
                />
              </div>
              <div className="ev-field">
                <label htmlFor="ev-heard">How did you hear about this?</label>
                <select
                  id="ev-heard"
                  className="ev-input"
                  value={form.heard_from}
                  onChange={(e) => set('heard_from', e.target.value)}
                >
                  {HEARD_FROM.map((h) => (
                    <option key={h} value={h}>
                      {h}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {needsOnsiteInfo && (
              <>
                <div className="ev-form-divider">
                  On-site details <span>this event has an in-person component</span>
                </div>
                <div className="ev-field-grid">
                  <div className="ev-field">
                    <label htmlFor="ev-emergency">
                      Emergency contact <span className="req">*</span>
                    </label>
                    <input
                      id="ev-emergency"
                      className="ev-input"
                      placeholder="Name and phone number"
                      value={form.emergency_contact}
                      onChange={(e) => set('emergency_contact', e.target.value)}
                    />
                  </div>
                  <div className="ev-field">
                    <label htmlFor="ev-diet">Dietary preference</label>
                    <select
                      id="ev-diet"
                      className="ev-input"
                      value={form.dietary_preference}
                      onChange={(e) => set('dietary_preference', e.target.value)}
                    >
                      {DIETARY.map((d) => (
                        <option key={d} value={d}>
                          {d}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="ev-field">
                    <label htmlFor="ev-tshirt">T-shirt size</label>
                    <select
                      id="ev-tshirt"
                      className="ev-input"
                      value={form.tshirt_size}
                      onChange={(e) => set('tshirt_size', e.target.value)}
                    >
                      <option value="">Select...</option>
                      {TSHIRT_SIZES.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="ev-field">
                    <label htmlFor="ev-access">Accessibility needs</label>
                    <input
                      id="ev-access"
                      className="ev-input"
                      placeholder="Anything we should arrange?"
                      value={form.accessibility_needs}
                      onChange={(e) => set('accessibility_needs', e.target.value)}
                    />
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {step === 'extra' && (
          <div className="ev-form">
            <div className="ev-form-divider">
              Event questions <span>set by {event.host_company}</span>
            </div>
            {questions.map((q) => (
              <div className="ev-field" key={q.key}>
                <label>
                  {q.label} {q.required && <span className="req">*</span>}
                </label>
                {renderQuestion(q)}
                {q.help && <div className="ev-help">{q.help}</div>}
              </div>
            ))}
            <div className="ev-field">
              <label htmlFor="ev-motivation">Why do you want to attend?</label>
              <textarea
                id="ev-motivation"
                className="ev-input"
                rows={3}
                placeholder="Optional, but organisers do read these."
                value={form.motivation}
                onChange={(e) => set('motivation', e.target.value)}
              />
            </div>
          </div>
        )}

        {step === 'confirm' && (
          <div className="ev-form">
            <div className="ev-summary">
              <div className="ev-summary-row">
                <span>Name</span>
                <b>{form.full_name}</b>
              </div>
              <div className="ev-summary-row">
                <span>Email</span>
                <b>{form.email}</b>
              </div>
              <div className="ev-summary-row">
                <span>Phone</span>
                <b>{form.phone}</b>
              </div>
              <div className="ev-summary-row">
                <span>Organisation</span>
                <b>{form.organization}</b>
              </div>
              <div className="ev-summary-row">
                <span>Event</span>
                <b>{event.title}</b>
              </div>
              <div className="ev-summary-row">
                <span>When</span>
                <b>
                  {formatEventDate(event.event_date)} {event.timezone_label}
                </b>
              </div>
              {event.mode !== 'Online' && (
                <div className="ev-summary-row">
                  <span>Where</span>
                  <b>{event.venue || event.location}</b>
                </div>
              )}
              <div className="ev-summary-row">
                <span>Fee</span>
                <b>{formatPrice(event.price, event.currency)}</b>
              </div>
            </div>

            {event.is_full && (
              <div className="ev-notice is-warn">
                This event is at capacity — you'll be added to the waitlist and notified if a seat frees up.
              </div>
            )}

            <label className="ev-check">
              <input
                type="checkbox"
                checked={form.consent_updates}
                onChange={(e) => set('consent_updates', e.target.checked)}
              />
              <span>Send me reminders and updates about this event.</span>
            </label>
            <label className="ev-check">
              <input
                type="checkbox"
                checked={form.agree_terms}
                onChange={(e) => set('agree_terms', e.target.checked)}
              />
              <span>
                I accept the event terms and the code of conduct. <span className="req">*</span>
              </span>
            </label>
          </div>
        )}

        {error && <div className="ev-notice is-error">{error}</div>}

        <div className="ev-modal-foot">
          {stepIndex > 0 ? (
            <button className="ev-btn ev-btn-ghost" onClick={goBack} disabled={submitting}>
              Back
            </button>
          ) : (
            <button className="ev-btn ev-btn-ghost" onClick={onClose} disabled={submitting}>
              Cancel
            </button>
          )}
          {step === 'confirm' ? (
            <button className="ev-btn ev-btn-primary" onClick={submit} disabled={submitting}>
              <Ticket size={15} /> {submitting ? 'Registering...' : 'Confirm registration'}
            </button>
          ) : (
            <button className="ev-btn ev-btn-primary" onClick={goNext}>
              Continue
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
