import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { BrandLogo } from './BrandLogo';
import {
  LayoutDashboard,
  User,
  Code2,
  Brain,
  Sparkles,
  Target,
  FolderOpen,
  Briefcase,
  BookmarkCheck,
  FileCheck2,
  Calendar,
  Bot,
  BarChart3,
  ShieldCheck,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();

  const navItems = [
    { path: '/dashboard', label: 'Home Dashboard', icon: LayoutDashboard },
    { path: '/profile', label: 'My Profile', icon: User },
    { path: '/code-quest', label: 'Code Quest', icon: Code2 },
    { path: '/aptitude-quest', label: 'Aptitude Quest', icon: Brain },
    { path: '/personality-test', label: 'Personality Test', icon: Sparkles },
    { path: '/position-ai', label: 'Position AI', icon: Target },
    { path: '/documents', label: 'Documents', icon: FolderOpen },
    { path: '/job-board', label: 'Job Board', icon: Briefcase },
    { path: '/my-jobs', label: 'My Jobs', icon: BookmarkCheck },
    { path: '/resume-builder', label: 'AI Resume Builder', icon: FileCheck2 },
    { path: '/events', label: 'Events', icon: Calendar },
    { path: '/interview-coach', label: 'AI Interview Coach', icon: Bot },
    { path: '/assessments', label: 'Assessments', icon: BarChart3 },
  ];

  if (user?.role === 'admin') {
    navItems.push({ path: '/admin', label: 'Admin Dashboard', icon: ShieldCheck });
  }

  return (
    <aside className="sidebar">
      <Link to="/dashboard" className="sidebar-header" aria-label="Carrerpulse Ai — go to dashboard">
        <BrandLogo variant="full" markSize={40} />
      </Link>
      <nav className="sidebar-menu">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `sidebar-nav-item ${isActive ? 'active' : ''}`
              }
            >
              <Icon size={18} />
              <span className="nav-label">{item.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
};
