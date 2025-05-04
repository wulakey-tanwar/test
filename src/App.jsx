import React from 'react';
import Header from './components/common/Header';
import Footer from './components/common/Footer';
import { ThemeProvider } from './context/ThemeContext';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ProfilePage from './pages/ProfilePage';
import PostDetailPage from './pages/PostDetailPage';
import AuthPage from './pages/AuthPage';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 min-h-screen flex flex-col">
          <Header />
          <main className="flex-grow p-4">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/post/:id" element={<PostDetailPage />} />
              <Route path="/auth" element={<AuthPage />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
