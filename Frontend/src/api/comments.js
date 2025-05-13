// src/api/comment.js
import commentAPI from './commentAxios';

// Create a new comment
export const createComment = async (postId, commentData) => {
  const response = await commentAPI.post(`/posts/${postId}/comments`, commentData);
  return response.data;
};

// Fetch comments for a post
export const fetchComments = async (postId) => {
  const response = await commentAPI.get(`/posts/${postId}/comments`);
  return response.data;
};