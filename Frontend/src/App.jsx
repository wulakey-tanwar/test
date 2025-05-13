import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/common/Header.jsx';
import Footer from './components/common/Footer.jsx';
import HomePage from './pages/HomePage.jsx';
import AuthPage from './pages/AuthPage.jsx';
import ProfilePage from './pages/ProfilePage.jsx';
import PostDetailPage from './pages/PostDetailPage.jsx';
import ExplorePage from './pages/ExplorePage.jsx';
import CreatePostPage from './components/post/CreatePost.jsx';

export default function App() {
  return (
    <div className="app-container">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<AuthPage />} />
          <Route path="/register" element={<AuthPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/posts/:id" element={<PostDetailPage />} />
          <Route path="/explore" element={<ExplorePage />} />
          <Route path="/create" element={<CreatePostPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}
