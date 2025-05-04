// src/components/post/PostList.jsx
import React from 'react'
import PostCard from './PostCard'

// Dummy data for preview purposes
const dummyPosts = [
  {
    id: '1',
    title: 'A Day in the Life',
    message: 'Exploring the beautiful parks and cafes in the city.',
    image: 'https://via.placeholder.com/400x200',
    author: { name: 'Alice', avatar: 'https://via.placeholder.com/32' },
  },
  {
    id: '2',
    title: 'React Tips & Tricks',
    message: 'Learn how to optimize your React components for performance.',
    image: 'https://via.placeholder.com/400x200',
    author: { name: 'Bob', avatar: 'https://via.placeholder.com/32' },
  },
  {
    id: '3',
    title: 'Travel Bucket List',
    message: 'Top 10 destinations to add to your travel wishlist.',
    image: 'https://via.placeholder.com/400x200',
    author: { name: 'Carol', avatar: 'https://via.placeholder.com/32' },
  },
]

const PostList = () => (
  <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
    {dummyPosts.map((post) => (
      <PostCard key={post.id} post={post} />
    ))}
  </div>
)

export default PostList;
