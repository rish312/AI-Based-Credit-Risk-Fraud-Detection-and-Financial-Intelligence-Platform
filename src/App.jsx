import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './context/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import PredictPage from './pages/PredictPage';
import ResultsPage from './pages/ResultsPage';
import ReviewPage from './pages/ReviewPage';
import MonitoringPage from './pages/MonitoringPage';

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      
      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<DashboardPage />} />
        <Route path="predict" element={
          <ProtectedRoute allowedRoles={['loan_officer', 'fraud_analyst', 'admin']}>
            <PredictPage />
          </ProtectedRoute>
        } />
        <Route path="predictions/:id" element={<ResultsPage />} />
        <Route path="review" element={
          <ProtectedRoute allowedRoles={['fraud_analyst', 'admin']}>
            <ReviewPage />
          </ProtectedRoute>
        } />
        <Route path="monitoring" element={
          <ProtectedRoute allowedRoles={['compliance', 'admin']}>
            <MonitoringPage />
          </ProtectedRoute>
        } />
      </Route>
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
