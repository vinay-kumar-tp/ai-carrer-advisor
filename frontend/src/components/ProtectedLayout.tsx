import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';
import { IntroAnimation } from './IntroAnimation';

export const ProtectedLayout: React.FC = () => {
  const { token, user, showIntro, dismissIntro } = useAuth();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="app-container">
      {showIntro && <IntroAnimation userName={user?.full_name} onDone={dismissIntro} />}
      <Sidebar />
      <div className="main-content">
        <Navbar />
        <main className="page-body">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
