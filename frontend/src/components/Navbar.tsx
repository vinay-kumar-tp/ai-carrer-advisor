import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, Bell, Search, Award } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="navbar">
      <div className="nav-search">
        <Search size={16} />
        <input
          type="text"
          className="input-field"
          placeholder="Search problems, jobs, skills..."
          aria-label="Search"
        />
      </div>

      <div className="nav-actions">
        <div className="badge badge-emerald nav-level">
          <Award size={14} /> Level 2 Learner
        </div>

        <ThemeToggle />

        <button className="nav-icon-btn" aria-label="Notifications" title="Notifications">
          <Bell size={18} />
        </button>

        <div className="nav-user">
          <div className="nav-avatar">{user?.email?.[0].toUpperCase() || 'U'}</div>
          <div className="nav-user-meta">
            <span className="nav-user-name">{user?.full_name || user?.email?.split('@')[0]}</span>
            <span className="nav-user-role">{user?.role || 'Student'}</span>
          </div>
          <button className="nav-icon-btn" onClick={logout} title="Logout" aria-label="Logout">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </header>
  );
};
