import React from 'react';
import PostCard from '../components/post/PostCard';
import { motion } from 'framer-motion';

// Sample posts (for now, dummy data)
const posts = [
  { id: 1, user: 'John Doe', image: '/assets/sample-post1.jpg', caption: 'Amazing view!' },
  { id: 2, user: 'Jane Smith', image: '/assets/sample-post2.jpg', caption: 'Love this place!' },
];

const HomePage = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="max-w-4xl mx-auto mt-8"
    >
      <h2 className="text-3xl font-bold mb-4">Welcome to MySocialApp</h2>
      <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
        Discover posts and connect with people.
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>
    </motion.div>
  );
};

export default HomePage;
