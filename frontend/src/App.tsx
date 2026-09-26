import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './components/Login';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './components/Dashboard';
import Models from './components/Models';
import ModelDetails from './components/ModelDetails';
import Alerts from './components/Alerts';
import Comparison from './components/Comparison';

const App: React.FC = () => (
  <BrowserRouter>
    <Toaster position="top-right" />
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="models" element={<Models />} />
        <Route path="models/:id" element={<ModelDetails />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="compare" element={<Comparison />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </BrowserRouter>
);

export default App;