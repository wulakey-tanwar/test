import React from 'react';
import PostList from '../components/post/PostList';

const HomePage = () => {
  return (
    <div className="max-w-4xl mx-auto mt-8">
      <h2 className="text-3xl font-bold mb-4">Welcome to MySocialApp</h2>
      <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
        Discover posts and connect with people.
      </p>
      <PostList />
    </div>
  );
};

export default HomePage;
