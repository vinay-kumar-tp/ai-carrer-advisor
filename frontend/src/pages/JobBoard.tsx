import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Briefcase, MapPin, DollarSign, Search, CheckCircle2 } from 'lucide-react';

export const JobBoardPage: React.FC = () => {
  const [jobs, setJobs] = useState<any[]>([]);
  const [keyword, setKeyword] = useState('');
  const [appliedJobs, setAppliedJobs] = useState<string[]>([]);

  useEffect(() => {
    fetchJobs();
    fetchMyApplications();
  }, []);

  const fetchJobs = async () => {
    try {
      const res = await api.get('/jobs/', { params: { keyword: keyword || undefined } });
      setJobs(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchMyApplications = async () => {
    try {
      const res = await api.get('/jobs/applications/mine');
      setAppliedJobs(res.data.map((a: any) => a.job_id));
    } catch (err) {
      console.error(err);
    }
  };

  const handleApply = async (jobId: string) => {
    try {
      await api.post(`/jobs/${jobId}/apply`);
      setAppliedJobs([...appliedJobs, jobId]);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Application failed');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h2>Career Opportunities & Job Board</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Browse curated software engineering, AI, and developer job opportunities matched to your skill profile.</p>
      </div>

      {/* Search Filter Bar */}
      <div className="glass-card" style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            className="input-field"
            placeholder="Filter jobs by title, skill (Python, React)..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            style={{ paddingLeft: '2.5rem' }}
          />
        </div>
        <button onClick={fetchJobs} className="btn btn-primary">Search</button>
      </div>

      {/* Job Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {jobs.map((j) => {
          const isApplied = appliedJobs.includes(j.id);
          return (
            <div key={j.id} className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.35rem' }}>
                  <h3 style={{ fontSize: '1.2rem' }}>{j.title}</h3>
                  <span className="badge badge-indigo">{j.job_type}</span>
                  {j.remote && <span className="badge badge-emerald">Remote</span>}
                </div>

                <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', display: 'flex', gap: '1.25rem', marginBottom: '0.75rem' }}>
                  <span style={{ fontWeight: 600, color: 'white' }}>{j.company}</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><MapPin size={14} /> {j.location}</span>
                  {j.salary_range && <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><DollarSign size={14} /> {j.salary_range}</span>}
                </div>

                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem', maxWidth: '750px' }}>{j.description}</p>

                <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                  {j.required_skills?.map((s: string) => (
                    <span key={s} className="badge badge-purple" style={{ fontSize: '0.75rem' }}>{s}</span>
                  ))}
                </div>
              </div>

              <div>
                {isApplied ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#34d399', fontSize: '0.9rem', fontWeight: 600 }}>
                    <CheckCircle2 size={18} /> Applied
                  </div>
                ) : (
                  <button onClick={() => handleApply(j.id)} className="btn btn-primary">
                    Apply Now
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
