// src/pages/AuthPage.jsx
import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import LoginForm from '../components/auth/LoginForm'
import RegisterForm from '../components/auth/RegisterForm'

export default function AuthPage() {
  const location = useLocation()
  const isRegister = location.pathname.includes('register')

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="w-full max-w-md bg-white dark:bg-gray-800 shadow-lg rounded-2xl p-8">
        <h2 className="text-3xl font-extrabold text-gray-900 dark:text-gray-100 mb-6 text-center">
          {isRegister ? 'Create an Account' : 'Welcome Back'}
        </h2>

        {isRegister ? <RegisterForm /> : <LoginForm />}

        <p className="mt-6 text-center text-gray-600 dark:text-gray-300">
          {isRegister
            ? 'Already have an account?'  
            : "Don't have an account?"}
          {' '}
          <Link
            to={isRegister ? '/login' : '/register'}
            className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline"
          >
            {isRegister ? 'Login' : 'Sign up'}
          </Link>
        </p>
      </div>
    </main>
  )
}
