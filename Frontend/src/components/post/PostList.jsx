// src/components/post/PostList.jsx
import React, { useState, useEffect } from 'react';
import PostCard from './PostCard';
import { fetchPosts } from '../../api/post';
import Loader from '../common/Loader';
import ErrorMessage from '../common/ErrorMessage';

const PostList = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    const loadPosts = async () => {
      try {
        setLoading(true);
        const data = await fetchPosts(page);
        
        if (page === 1) {
          setPosts(data.posts || data);
        } else {
          setPosts(prev => [...prev, ...(data.posts || data)]);
        }
        
        setHasMore(data.hasMore || data.length === 10);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load posts');
        console.error('Error loading posts:', err);
      } finally {
        setLoading(false);
      }
    };

    loadPosts();
  }, [page]);

  const loadMore = () => {
    if (!loading && hasMore) {
      setPage(prev => prev + 1);
    }
  };

  if (loading && posts.length === 0) {
    return <Loader />;
  }

  if (error && posts.length === 0) {
    return <ErrorMessage message={error} />;
  }

  return (
    <div className="space-y-8">
      <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
        {posts.map((post) => (
          <PostCard key={post._id || post.id} post={post} />
        ))}
      </div>
      
      {loading && posts.length > 0 && (
        <div className="text-center py-4">
          <Loader />
        </div>
      )}
      
      {hasMore && !loading && (
        <div className="text-center py-4">
          <button 
            onClick={loadMore}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 transition"
          >
            Load More
          </button>
        </div>
      )}
      
      {!hasMore && posts.length > 0 && (
        <div className="text-center py-4 text-gray-500">
          No more posts to load
        </div>
      )}
    </div>
  );
};

export default PostList;