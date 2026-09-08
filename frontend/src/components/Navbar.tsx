import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, Bell, Search, Award } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="navbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1, maxWidth: '450px' }}>
        <div style={{ position: 'relative', width: '100%' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            className="input-field"
            placeholder="Search problems, jobs, skills..."
            style={{ paddingLeft: '2.4rem' }}
          />
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        <div className="badge badge-emerald" style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
          <Award size={14} /> Level 2 Learner
        </div>

        <button className="btn btn-secondary" style={{ padding: '0.5rem', borderRadius: '50%' }}>
          <Bell size={18} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', paddingLeft: '0.5rem', borderLeft: '1px solid var(--border-color)' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--accent-purple), var(--accent-pink))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', color: 'white' }}>
            {user?.email?.[0].toUpperCase() || 'U'}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{user?.full_name || user?.email?.split('@')[0]}</span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>{user?.role || 'Student'}</span>
          </div>
          <button className="btn btn-secondary" onClick={logout} style={{ padding: '0.4rem 0.6rem', marginLeft: '0.5rem' }} title="Logout">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </header>
  );
};
