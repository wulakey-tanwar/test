// src/components/common/Header.jsx
import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext.jsx'

export default function Header() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const linkClass = ({ isActive }) =>
    [
      'text-gray-700 dark:text-gray-300 hover:text-indigo-500 dark:hover:text-indigo-400',
      isActive ? 'font-semibold' : 'font-normal'
    ].join(' ')

  return (
    <header className="bg-white dark:bg-gray-900 shadow">
      <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
        <NavLink to="/" className="text-2xl font-extrabold text-indigo-600 dark:text-indigo-400">
          MySocialApp
        </NavLink>
        <nav className="flex items-center space-x-6">
          <NavLink to="/" className={linkClass}>Home</NavLink>
          {user ? (
            <>
              <NavLink to="/explore" className={linkClass}>Explore</NavLink>
              <NavLink to="/profile" className={linkClass}>{user.name}</NavLink>
              <button
                onClick={handleLogout}
                className="text-red-600 hover:text-red-500 dark:text-red-400 dark:hover:text-red-300 font-medium"
              >
                Logout
              </button>
            </>
          ) : (
            <NavLink to="/login" className={linkClass}>Login</NavLink>
          )}
        </nav>
      </div>
    </header>
  )
}
