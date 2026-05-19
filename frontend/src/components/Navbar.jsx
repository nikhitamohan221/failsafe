import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Activity, LogOut, LayoutDashboard, User } from 'lucide-react';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const role = localStorage.getItem('role');
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/');
  };

  if (!role) return null;

  return (
    <nav className="navbar">
      <div className="brand-logo">
        <Activity className="brand-icon" size={28} />
        <span>FAILSAFE</span>
      </div>
      <div className="nav-links">
        {role === 'faculty' && (
          <a 
            href="/faculty" 
            className={location.pathname === '/faculty' ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); navigate('/faculty'); }}
          >
            <LayoutDashboard size={18} /> Dashboard
          </a>
        )}
        {role === 'hod' && (
          <a 
            href="/hod"
            className={location.pathname === '/hod' ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); navigate('/hod'); }}
          >
            <LayoutDashboard size={18} /> Department View
          </a>
        )}
        {role === 'student' && (
          <a 
            href="/my-profile"
            className={location.pathname === '/my-profile' ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); navigate('/my-profile'); }}
          >
            <User size={18} /> My Profile
          </a>
        )}
        <button onClick={handleLogout} className="logout-btn">
          <LogOut size={16} /> Logout
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
