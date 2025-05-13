// src/component/comment/CommentList.jsx

import React, { useState, useEffect } from 'react';
import commentAPI from '../../api/commentAxios';

const CommentList = ({ postId }) => {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadComments = async () => {
      try {
        setLoading(true);
        const res = await commentAPI.get(`/posts/${postId}/comments`);
        setComments(res.data);
        setError('');
      } catch (err) {
        setError('Failed to load comments');
        console.error('Error loading comments:', err);
      } finally {
        setLoading(false);
      }
    };

    loadComments();
  }, [postId]);

  const handleCommentAdded = (newComment) => {
    setComments(prev => [newComment, ...prev]);
  };

  if (loading) {
    return <div className="text-center py-4">Loading comments...</div>;
  }

  if (error) {
    return <div className="text-red-500 py-2">{error}</div>;
  }

  if (comments.length === 0) {
    return <div className="py-2 text-gray-500">No comments yet. Be the first to comment!</div>;
  }

  return (
    <div className="mt-4">
      {comments.map((comment) => (
        <div key={comment._id || comment.id} className="border-b pb-2 mb-2">
          <div className="flex items-center gap-2">
            <p className="font-semibold">{comment.user?.name || 'Anonymous'}:</p>
            <span className="text-xs text-gray-500">
              {new Date(comment.createdAt).toLocaleDateString()}
            </span>
          </div>
          <p>{comment.content}</p>
        </div>
      ))}
    </div>
  );
};

export default CommentList;