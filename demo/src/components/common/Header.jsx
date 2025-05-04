import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.jsx';

export default function Header() {
  const { user, logout } = useAuth();
  const nav = useNavigate();

  const handleLogout = () => {
    logout();
    nav('/login');
  };

  return (
    <header className="header">
      <Link to="/">Home</Link>
      {user ? (
        <>
          <Link to="/explore">Explore</Link>
          <Link to="/profile">{user.name}</Link>
          <button onClick={handleLogout}>Logout</button>
        </>
      ) : (
        <Link to="/login">Login</Link>
      )}
    </header>
  );
}
