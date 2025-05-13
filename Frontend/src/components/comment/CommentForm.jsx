// src/component/comment/CommentForm.jsx

import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import commentAPI from '../../api/commentAxios';

const CommentForm = ({ postId, onCommentAdded }) => {
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const { isAuthenticated } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!isAuthenticated) {
      setError('You must be logged in to comment');
      return;
    }

    if (!content.trim()) {
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const res = await commentAPI.post(`/posts/${postId}/comments`, { content });
      const newComment = res.data;

      setContent('');

      if (onCommentAdded) {
        onCommentAdded(newComment);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to post comment');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
      <form onSubmit={handleSubmit} className="flex items-center">
        <input
          type="text"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full p-2 border rounded-l-md"
          placeholder="Add a comment..."
          disabled={isSubmitting || !isAuthenticated}
        />
        <button
          type="submit"
          className="p-2 bg-blue-500 text-white rounded-r-md disabled:bg-blue-300"
          disabled={isSubmitting || !content.trim() || !isAuthenticated}
        >
          {isSubmitting ? 'Posting...' : 'Post'}
        </button>
      </form>
    </div>
  );
};

export default CommentForm;