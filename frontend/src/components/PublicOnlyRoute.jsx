import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

// Renders children only for unauthenticated users (login/signup).
// Authenticated users are sent to the homepage (or their intended page).
function PublicOnlyRoute({ children }) {
  const auth = useAuth();
  const location = useLocation();

  if (auth.isAuthenticated) {
    const dest = location.state?.from || '/';
    return <Navigate to={dest} replace />;
  }
  return children;
}

export default PublicOnlyRoute;
