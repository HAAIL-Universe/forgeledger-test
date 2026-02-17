
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

/**
 * Root application component for ForgeLedger Test.
 *
 * Sets up client-side routing with react-router-dom.
 * Per the UI blueprint, this is a single-page application with
 * all functionality accessible from the Dashboard route ("/").
 */

/**
 * Placeholder Dashboard page component.
 * Will be replaced with the full Dashboard implementation in a later phase.
 */
const DashboardPlaceholder: React.FC = () => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
        backgroundColor: '#F9FAFB',
        color: '#111827',
      }}
    >
      <h1 style={{ fontSize: '2rem', fontWeight: 600, marginBottom: '0.5rem' }}>
        ForgeLedger Test
      </h1>
      <p style={{ fontSize: '1rem', color: '#6B7280' }}>
        Lightweight financial ledger for tracking income and expenses.
      </p>
      <p style={{ fontSize: '0.875rem', color: '#9CA3AF', marginTop: '1rem' }}>
        Dashboard coming soon.
      </p>
    </div>
  );
};

/**
 * Simple 404 Not Found page for unmatched routes.
 */
const NotFound: React.FC = () => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
        backgroundColor: '#F9FAFB',
        color: '#111827',
      }}
    >
      <h1 style={{ fontSize: '2rem', fontWeight: 600, marginBottom: '0.5rem' }}>
        404 — Page Not Found
      </h1>
      <p style={{ fontSize: '1rem', color: '#6B7280' }}>
        The page you're looking for doesn't exist.
      </p>
      <a
        href="/"
        style={{
          marginTop: '1.5rem',
          color: '#2563EB',
          textDecoration: 'none',
          fontWeight: 500,
        }}
      >
        Go to Dashboard
      </a>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardPlaceholder />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
