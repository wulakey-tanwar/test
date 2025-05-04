import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';

import App from './App.jsx';
import { AuthProvider } from './context/AuthContext.jsx';
import { ThemeProvider } from './context/ThemeContext.jsx';
import './styles/global.css';

const container = document.getElementById('root');
const root = createRoot(container);

root.render(
  <BrowserRouter>
    <AuthProvider>
      <ThemeProvider>
        <App />
      </ThemeProvider>
    </AuthProvider>
  </BrowserRouter>
);

