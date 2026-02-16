import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ExtractionSession from './pages/ExtractionSession';
import RuleReview from './pages/RuleReview';
import MockupPreview from './pages/MockupPreview';
import MockupRender from './pages/MockupRender';
import SkillDownload from './pages/SkillDownload';
import ComponentStudio from './pages/ComponentStudio';
import AuditPage from './pages/AuditPage';
import GeneratorPage from './pages/GeneratorPage';
import DocsLayout from './pages/docs/DocsLayout';
import TmlSpec from './pages/docs/TmlSpec';
import ClaudeCodeGuide from './pages/docs/ClaudeCodeGuide';
import CursorGuide from './pages/docs/CursorGuide';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Loading...</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Loading...</p>
      </div>
    );
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route
        path="/"
        element={
          <PublicRoute>
            <Landing />
          </PublicRoute>
        }
      />
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        }
      />

      {/* Protected routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/session/:sessionId"
        element={
          <ProtectedRoute>
            <ExtractionSession />
          </ProtectedRoute>
        }
      />
      <Route
        path="/session/:sessionId/studio"
        element={
          <ProtectedRoute>
            <ComponentStudio />
          </ProtectedRoute>
        }
      />
      <Route
        path="/session/:sessionId/review"
        element={
          <ProtectedRoute>
            <RuleReview />
          </ProtectedRoute>
        }
      />
      <Route
        path="/session/:sessionId/mockups"
        element={
          <ProtectedRoute>
            <MockupPreview />
          </ProtectedRoute>
        }
      />
      <Route
        path="/session/:sessionId/download"
        element={
          <ProtectedRoute>
            <SkillDownload />
          </ProtectedRoute>
        }
      />
      <Route
        path="/audit"
        element={
          <ProtectedRoute>
            <AuditPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/generate"
        element={
          <ProtectedRoute>
            <GeneratorPage />
          </ProtectedRoute>
        }
      />

      {/* Standalone mockup render (no auth - for Puppeteer capture) */}
      <Route path="/mockup-render/:sessionId/:mockupType" element={<MockupRender />} />

      {/* Documentation pages */}
      <Route path="/docs" element={<DocsLayout />}>
        <Route path="tml" element={<TmlSpec />} />
        <Route path="claude-code" element={<ClaudeCodeGuide />} />
        <Route path="cursor" element={<CursorGuide />} />
      </Route>

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
