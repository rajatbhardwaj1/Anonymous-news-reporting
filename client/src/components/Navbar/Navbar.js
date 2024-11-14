// src/components/Navbar.js
import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import './Navbar.css';

function Navbar() {
  const { user } = useContext(AuthContext);
  const {handleLogout} = useContext(AuthContext);
  const navigate = useNavigate();

  const onLogout =async  () => {
    await handleLogout();
  };

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <Link to="/" className="navbar-logo">
          NewsApp
        </Link>
      </div>
      <div className="navbar-right">
        {user ? (
          <>
            <span className="username">Welcome, {user.username}</span>
            <Link to="/home" className="navbar-link">
              Home
            </Link>
            <Link to="/profile" className="navbar-link">
              Profile
            </Link>
            <button className="logout-button" onClick={onLogout}>
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="navbar-link">
              Login
            </Link>
            <Link to="/register" className="navbar-link">
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
