import React from 'react';
import { MapPin, Briefcase, Wallet, Clock, Users, CheckCircle2 } from 'lucide-react';
import type { JobCard as JobCardType } from './types';
import { formatCTC, formatStipend, timeAgo } from './types';
import { CompanyLogo } from './CompanyLogo';

type Props = {
  job: JobCardType;
  onOpen: (id: string) => void;
};

export const JobCardItem: React.FC<Props> = ({ job, onOpen }) => {
  const isInternship = job.job_type === 'internship';
  const pay = isInternship
    ? formatStipend(job.stipend_min, job.stipend_max)
    : formatCTC(job.ctc_min, job.ctc_max);

  return (
    <div className="glass-card jb-card" onClick={() => onOpen(job.id)}>
      <CompanyLogo company={job.company} fallback={job.company_logo} />
      <div className="jb-card-main">
        <div className="jb-card-top">
          <div>
            <h3 className="jb-card-title">{job.title}</h3>
            <div className="jb-card-company">{job.company}</div>
            <div className="jb-portal">
              Posted on <b>{job.source_portal}</b>
              {job.company_tagline ? ` · ${job.company_tagline}` : ''}
            </div>
          </div>
          <div className="jb-card-side">
            <span className="badge badge-indigo" style={{ textTransform: 'capitalize' }}>
              {job.job_type}
            </span>
            {job.applied && (
              <span className="jb-applied-badge">
                <CheckCircle2 size={15} /> Applied
              </span>
            )}
          </div>
        </div>

        <div className="jb-meta-row">
          <span>
            <MapPin size={14} /> {job.location || job.employment_mode}
          </span>
          <span>
            <Briefcase size={14} /> {job.employment_mode}
          </span>
          {pay && (
            <span>
              <Wallet size={14} /> {pay}
            </span>
          )}
          <span>
            <Clock size={14} /> {timeAgo(job.posted_at)}
          </span>
          {job.openings > 1 && (
            <span>
              <Users size={14} /> {job.openings} openings
            </span>
          )}
        </div>

        <div className="jb-tags">
          {job.industry && <span className="jb-tag" style={{ background: 'rgba(34,211,238,0.14)', color: '#67e8f9' }}>{job.industry}</span>}
          {job.required_skills?.slice(0, 5).map((s) => (
            <span key={s} className="jb-tag">
              {s}
            </span>
          ))}
          {job.required_skills?.length > 5 && (
            <span className="jb-tag">+{job.required_skills.length - 5}</span>
          )}
        </div>
      </div>
    </div>
  );
};
