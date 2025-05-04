import React, { createContext, useContext, useEffect, useState } from 'react';

// Create the context
const AuthContext = createContext();

// Create the provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const [loading, setLoading] = useState(false);

  const login = async (email, password) => {
    setLoading(true);
    try {
      // TODO: Replace with real API call
      const dummyUser = {
        id: 1,
        name: 'John Doe',
        email,
        token: 'fake-jwt-token',
      };

      // Simulate network delay
      await new Promise((res) => setTimeout(res, 1000));

      localStorage.setItem('user', JSON.stringify(dummyUser));
      setUser(dummyUser);
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, message: 'Login failed' };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('user');
    setUser(null);
  };

  const isAuthenticated = !!user;

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook for consuming the auth context
export const useAuth = () => useContext(AuthContext);
