// hooks/useComment.js
import { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/authcontext';

const API_BASE = 'http://localhost:8000'; // replace with your actual API base

export const useComment = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);

  const authHeaders = () => ({
    headers: {
      Authorization: `Bearer ${user?.token}`,
    },
  });

  const createComment = async (postId, content, parentId = null) => {
    setLoading(true);
    try {
      const res = await axios.post(
        `${API_BASE}/comments`,
        {
          post_id: postId,
          content,
          parent_id: parentId,
        },
        authHeaders()
      );
      return { success: true, data: res.data };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Error creating comment',
      };
    } finally {
      setLoading(false);
    }
  };

  const getCommentsForPost = async (postId, skip = 0, limit = 20) => {
    try {
      const res = await axios.get(
        `${API_BASE}/posts/${postId}/comments`,
        { params: { skip, limit }, ...authHeaders() }
      );
      return res.data;
    } catch (error) {
      return [];
    }
  };

  const deleteComment = async (commentId) => {
    try {
      await axios.delete(`${API_BASE}/comments/${commentId}`, authHeaders());
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Delete failed',
      };
    }
  };

  const likeComment = async (commentId) => {
    try {
      const res = await axios.post(
        `${API_BASE}/comments/${commentId}/like`,
        null,
        authHeaders()
      );
      return res.data;
    } catch (error) {
      return null;
    }
  };

  const unlikeComment = async (commentId) => {
    try {
      const res = await axios.post(
        `${API_BASE}/comments/${commentId}/unlike`,
        null,
        authHeaders()
      );
      return res.data;
    } catch (error) {
      return null;
    }
  };

  return {
    loading,
    createComment,
    getCommentsForPost,
    deleteComment,
    likeComment,
    unlikeComment,
  };
};