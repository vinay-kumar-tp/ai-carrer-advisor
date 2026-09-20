import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedLayout } from './components/ProtectedLayout';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { ProfilePage } from './pages/Profile';
import { VideoResumePage } from './pages/VideoResume';
import { CodeQuestPage } from './pages/CodeQuest';
import { AptitudeQuestPage } from './pages/AptitudeQuest';
import { PersonalityTestPage } from './pages/PersonalityTest';
import { PositionAIPage } from './pages/PositionAI';
import { DocumentsPage } from './pages/Documents';
import { JobBoardPage } from './pages/JobBoard';
import { MyJobsPage } from './pages/MyJobs';
import { ResumeBuilderPage } from './pages/ResumeBuilder';
import { EventsPage } from './pages/Events';
import { InterviewCoachPage } from './pages/InterviewCoach';
import { AssessmentsPage } from './pages/Assessments';
import { AdminDashboardPage } from './pages/AdminDashboard';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Application Routes */}
          <Route element={<ProtectedLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/video-resume" element={<VideoResumePage />} />
            <Route path="/code-quest" element={<CodeQuestPage />} />
            <Route path="/aptitude-quest" element={<AptitudeQuestPage />} />
            <Route path="/personality-test" element={<PersonalityTestPage />} />
            <Route path="/position-ai" element={<PositionAIPage />} />
            <Route path="/candidate/position-ai" element={<PositionAIPage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/job-board" element={<JobBoardPage />} />
            <Route path="/my-jobs" element={<MyJobsPage />} />
            <Route path="/resume-builder" element={<ResumeBuilderPage />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/interview-coach" element={<InterviewCoachPage />} />
            <Route path="/assessments" element={<AssessmentsPage />} />
            <Route path="/admin" element={<AdminDashboardPage />} />
          </Route>

          {/* Default Redirect */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};
export default App;
