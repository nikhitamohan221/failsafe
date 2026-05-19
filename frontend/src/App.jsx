import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import FacultyDashboard from './pages/FacultyDashboard';
import HODDashboard from './pages/HODDashboard';
import StudentDetail from './pages/StudentDetail';
import StudentProfile from './pages/StudentProfile';
import Navbar from './components/Navbar';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  
  if (!token) {
    return <Navigate to="/" replace />;
  }
  
  if (allowedRoles && !allowedRoles.includes(role)) {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

const AppLayout = ({ children }) => (
  <>
    <Navbar />
    {children}
  </>
);

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        
        <Route path="/faculty" element={
          <ProtectedRoute allowedRoles={['faculty']}>
            <AppLayout><FacultyDashboard /></AppLayout>
          </ProtectedRoute>
        } />
        
        <Route path="/hod" element={
          <ProtectedRoute allowedRoles={['hod']}>
            <AppLayout><HODDashboard /></AppLayout>
          </ProtectedRoute>
        } />
        
        <Route path="/student/:id" element={
          <ProtectedRoute allowedRoles={['faculty', 'hod']}>
            <AppLayout><StudentDetail /></AppLayout>
          </ProtectedRoute>
        } />
        
        <Route path="/my-profile" element={
          <ProtectedRoute allowedRoles={['student']}>
            <AppLayout><StudentProfile /></AppLayout>
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
