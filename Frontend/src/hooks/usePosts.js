// src/hooks/usePost.js
import { useState, useEffect } from 'react';
import { fetchPostById } from '../api/post';

export const usePost = (postId) => {
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getPost = async () => {
      try {
        setLoading(true);
        const data = await fetchPostById(postId);
        setPost(data);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to fetch post');
        console.error('Error fetching post:', err);
      } finally {
        setLoading(false);
      }
    };

    if (postId) {
      getPost();
    }
  }, [postId]);

  return { post, loading, error };
};