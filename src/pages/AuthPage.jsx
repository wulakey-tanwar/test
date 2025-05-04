import React from 'react';
import { Link } from 'react-router-dom';
import LoginForm from '../components/auth/LoginForm';
import RegisterForm from '../components/auth/RegisterForm';

const AuthPage = () => {
  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="max-w-lg w-full p-8 bg-white shadow-md rounded-md">
        <h2 className="text-3xl font-bold mb-6">Welcome to MySocialApp</h2>
        <LoginForm />
        <div className="text-center mt-4">
          <p>Don't have an account? <Link to="/register" className="text-blue-500">Sign up</Link></p>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
