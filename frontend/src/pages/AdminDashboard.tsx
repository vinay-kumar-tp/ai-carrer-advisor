import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { ShieldCheck, Users, Briefcase, Code2, Brain, CheckCircle2 } from 'lucide-react';

export const AdminDashboardPage: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);

  useEffect(() => {
    fetchStats();
    fetchUsers();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await api.get('/admin/stats');
      setStats(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchUsers = async () => {
    try {
      const res = await api.get('/admin/users');
      setUsers(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h2>System Administration & Platform Metrics</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Real-time overview of active student accounts, job listings, coding problems, and mock interviews.</p>
      </div>

      {stats && (
        <div className="grid-4">
          <div className="glass-card">
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Registered Users</span>
            <h2 style={{ fontSize: '2rem', marginTop: '0.25rem' }}>{stats.total_users}</h2>
          </div>
          <div className="glass-card">
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Active Job Listings</span>
            <h2 style={{ fontSize: '2rem', marginTop: '0.25rem' }}>{stats.total_jobs}</h2>
          </div>
          <div className="glass-card">
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Coding Problems</span>
            <h2 style={{ fontSize: '2rem', marginTop: '0.25rem' }}>{stats.total_coding_problems}</h2>
          </div>
          <div className="glass-card">
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Mock Interviews Conducted</span>
            <h2 style={{ fontSize: '2rem', marginTop: '0.25rem' }}>{stats.total_mock_interviews}</h2>
          </div>
        </div>
      )}

      <div className="glass-card">
        <h3 style={{ marginBottom: '1rem' }}>User Directory</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {users.map((u) => (
            <div key={u.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', background: 'rgba(10,13,20,0.5)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <div>
                <span style={{ fontWeight: 600, display: 'block' }}>{u.full_name} ({u.email})</span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Joined: {new Date(u.created_at).toLocaleDateString()}</span>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <span className={`badge ${u.role === 'admin' ? 'badge-amber' : 'badge-indigo'}`} style={{ textTransform: 'capitalize' }}>{u.role}</span>
                {u.is_active && <span className="badge badge-emerald">Active</span>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
