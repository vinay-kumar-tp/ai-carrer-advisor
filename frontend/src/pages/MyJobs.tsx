import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { BookmarkCheck, Clock, Building } from 'lucide-react';

export const MyJobsPage: React.FC = () => {
  const [applications, setApplications] = useState<any[]>([]);

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      const res = await api.get('/jobs/applications/mine');
      setApplications(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h2>My Applications & Job Tracker</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Track the status of your active job applications, interview schedules, and recruiter feedback.</p>
      </div>

      <div className="glass-card">
        {applications.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {applications.map((app) => (
              <div key={app.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', background: 'rgba(10,13,20,0.5)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div>
                  <span style={{ fontWeight: 600, display: 'block', fontSize: '1rem' }}>Application ID: #{app.id.substring(0, 8)}</span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Applied on: {new Date(app.applied_at).toLocaleDateString()}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <span className="badge badge-indigo" style={{ textTransform: 'capitalize' }}>Status: {app.status}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            No applications submitted yet. Visit the Job Board to apply for software engineering positions.
          </div>
        )}
      </div>
    </div>
  );
};
