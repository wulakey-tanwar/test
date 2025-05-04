import React from 'react';
import PostList from '../components/post/PostList';

const ExplorePage = () => {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Explore Posts</h1>
      <PostList />
    </div>
  );
};

export default ExplorePage;
