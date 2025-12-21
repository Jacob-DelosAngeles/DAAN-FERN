import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { SignIn, SignUp, SignedIn, SignedOut } from '@clerk/clerk-react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Dashboard from './pages/Dashboard';
import IRICalculator from './pages/IRICalculator';
import Mapping from './pages/Mapping';
import AdminDashboard from './pages/AdminDashboard';
import Layout from './components/Layout';
import AuthLayout from './components/Auth/AuthLayout';
import { clerkAppearance } from './utils/clerkTheme';

// Protected Route Component - uses our AuthContext which wraps Clerk
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return children;
};

// Clerk Sign In Page wrapper with custom styling
const LoginPage = () => (
  <AuthLayout>
    <SignIn
      routing="path"
      path="/login"
      signUpUrl="/register"
      afterSignInUrl="/dashboard"
      appearance={clerkAppearance}
    />
  </AuthLayout>
);

// Clerk Sign Up Page wrapper with custom styling
const RegisterPage = () => (
  <AuthLayout>
    <SignUp
      routing="path"
      path="/register"
      signInUrl="/login"
      afterSignUpUrl="/dashboard"
      appearance={clerkAppearance}
    />
  </AuthLayout>
);

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes - Clerk handles auth */}
          <Route path="/login/*" element={<LoginPage />} />
          <Route path="/register/*" element={<RegisterPage />} />

          {/* Protected routes */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<Navigate to="/dashboard" />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="iri" element={<IRICalculator />} />
            <Route path="mapping" element={<Mapping />} />
            <Route path="admin" element={<AdminDashboard />} />
            <Route path="reports" element={<div>Reports Component (Coming Soon)</div>} />
            <Route path="settings" element={<div>Settings Component (Coming Soon)</div>} />
          </Route>

          {/* Catch all - redirect to dashboard or login */}
          <Route path="*" element={<Navigate to="/dashboard" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
