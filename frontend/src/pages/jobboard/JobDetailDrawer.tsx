import React from 'react';
import {
  X, MapPin, Briefcase, Wallet, Clock, Users, CalendarClock,
  CheckCircle2, XCircle, Building2, ListChecks, GraduationCap, Gift, ShieldCheck,
} from 'lucide-react';
import type { JobDetail } from './types';
import { formatCTC, formatStipend, timeAgo } from './types';
import { CompanyLogo } from './CompanyLogo';
import { Loading } from '../../components/codequest/ui';

type Props = {
  job: JobDetail | null;
  loading: boolean;
  onClose: () => void;
  onApply: () => void;
};

export const JobDetailDrawer: React.FC<Props> = ({ job, loading, onClose, onApply }) => {
  return (
    <div className="jb-drawer-overlay" onClick={onClose}>
      <div className="jb-drawer" onClick={(e) => e.stopPropagation()} style={{ position: 'relative' }}>
        <button className="jb-drawer-close" onClick={onClose} aria-label="Close">
          <X size={16} />
        </button>

        {loading || !job ? (
          <Loading label="Loading job details..." />
        ) : (
          <>
            <div className="jb-drawer-head">
              <CompanyLogo company={job.company} fallback={job.company_logo} />
              <div>
                <h2>{job.title}</h2>
                <div className="jb-drawer-sub">
                  <b style={{ color: '#fff' }}>{job.company}</b> · Posted on {job.source_portal} · {timeAgo(job.posted_at)}
                </div>
                <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
                  <span className="badge badge-indigo" style={{ textTransform: 'capitalize' }}>{job.job_type}</span>
                  <span className="badge badge-purple">{job.employment_mode}</span>
                  {job.industry && <span className="badge badge-emerald">{job.industry}</span>}
                </div>
              </div>
            </div>

            <div className="jb-meta-row" style={{ marginTop: '1rem' }}>
              <span><MapPin size={14} /> {job.location || job.employment_mode}</span>
              <span><Briefcase size={14} /> {job.experience_min_years}{job.experience_max_years ? `-${job.experience_max_years}` : '+'} yr exp</span>
              <span>
                <Wallet size={14} />{' '}
                {job.job_type === 'internship'
                  ? formatStipend(job.stipend_min, job.stipend_max)
                  : formatCTC(job.ctc_min, job.ctc_max) || 'Not disclosed'}
              </span>
              <span><Users size={14} /> {job.openings} opening{job.openings > 1 ? 's' : ''}</span>
              {job.application_deadline && <span><CalendarClock size={14} /> Apply by {job.application_deadline}</span>}
              <span><Clock size={14} /> {timeAgo(job.posted_at)}</span>
            </div>

            {/* Eligibility */}
            {job.eligibility.has_criteria && (
              <div className="glass-card jb-section" style={{ marginTop: '1.25rem' }}>
                <div className="jb-elig-head">
                  <ShieldCheck size={17} color={job.eligibility.eligible ? '#34d399' : '#f87171'} />
                  <span className={`jb-elig-summary ${job.eligibility.eligible ? 'ok' : 'no'}`}>
                    {job.eligibility.eligible
                      ? `You meet all ${job.eligibility.total} eligibility criteria`
                      : `You meet ${job.eligibility.met_count} of ${job.eligibility.total} criteria`}
                  </span>
                </div>
                {job.eligibility.criteria.map((c) => (
                  <div className="jb-crit" key={c.key + c.label}>
                    {c.met ? (
                      <CheckCircle2 size={16} className="jb-crit-icon met" />
                    ) : (
                      <XCircle size={16} className="jb-crit-icon miss" />
                    )}
                    <div className="jb-crit-body">
                      <div className="jb-crit-label">{c.label}</div>
                      <div className="jb-crit-detail">
                        Requires: {c.requirement} · <span className="you">You: {c.candidate_value}</span>
                        {c.note ? ` (${c.note})` : ''}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* About company */}
            {job.about_company && (
              <div className="jb-section">
                <h4><Building2 size={16} /> About {job.company}</h4>
                <p>{job.about_company}</p>
              </div>
            )}

            {/* Description */}
            <div className="jb-section">
              <h4><ListChecks size={16} /> Job Description</h4>
              <p>{job.description}</p>
            </div>

            {/* Responsibilities */}
            {job.responsibilities?.length > 0 && (
              <div className="jb-section">
                <h4>Key Responsibilities</h4>
                <ul>
                  {job.responsibilities.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </div>
            )}

            {/* Required skills */}
            {job.required_skills?.length > 0 && (
              <div className="jb-section">
                <h4>Required Skills</h4>
                <div className="jb-tags">
                  {job.required_skills.map((s) => <span key={s} className="jb-tag">{s}</span>)}
                </div>
              </div>
            )}

            {/* Preferred qualifications */}
            {job.qualifications?.length > 0 && (
              <div className="jb-section">
                <h4><GraduationCap size={16} /> Preferred Qualifications</h4>
                <ul>
                  {job.qualifications.map((q, i) => <li key={i}>{q}</li>)}
                </ul>
              </div>
            )}

            {/* CTC breakdown */}
            {job.ctc_breakdown?.length > 0 && (
              <div className="jb-section">
                <h4><Wallet size={16} /> Compensation Breakdown</h4>
                <div className="jb-ctc-table">
                  {job.ctc_breakdown.map((row, i) => (
                    <div className="jb-ctc-row" key={i}>
                      <span>{row.component}</span>
                      <b>{row.amount}</b>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Perks */}
            {job.perks?.length > 0 && (
              <div className="jb-section">
                <h4><Gift size={16} /> Perks & Benefits</h4>
                <div className="jb-tags">
                  {job.perks.map((p) => (
                    <span key={p} className="jb-tag" style={{ background: 'rgba(16,185,129,0.14)', color: '#6ee7b7' }}>{p}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Footer */}
            <div className="jb-drawer-foot">
              {job.applied ? (
                <span className="jb-applied-badge" style={{ fontSize: '0.95rem' }}>
                  <CheckCircle2 size={18} /> Application submitted{job.application_status ? ` · ${job.application_status}` : ''}
                </span>
              ) : job.eligibility.eligible ? (
                <button className="btn btn-primary" onClick={onApply} style={{ minWidth: 200 }}>
                  Interested — Apply Now
                </button>
              ) : (
                <div className="jb-blocked" style={{ flex: 1 }}>
                  You don't currently meet the eligibility criteria for this role. Update your profile
                  (skills, CGPA, experience) to become eligible.
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};
