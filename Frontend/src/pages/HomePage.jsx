import React from 'react';
import PostList from '../components/post/PostList';

const HomePage = () => (
  <main className="min-h-screen bg-gray-50 dark:bg-gray-900">
    <header className="bg-gradient-to-r from-purple-500 to-indigo-600 dark:from-purple-700 dark:to-indigo-800 py-12">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-4">
          Welcome to MySocialApp
        </h1>
        <p className="text-lg text-purple-100 mb-6">
          Discover posts and connect with people in one easy-to-use platform.
        </p>
        <a
          href="/create"
          className="inline-block bg-white text-indigo-600 font-medium py-3 px-6 rounded-lg shadow hover:bg-gray-100 transition"
        >
          Create Your First Post
        </a>
      </div>
    </header>

    <section className="max-w-6xl mx-auto px-4 mt-12">
      <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-6">
        Latest Posts
      </h2>
      <PostList />
    </section>
  </main>
);

export default HomePage;