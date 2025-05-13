// src/api/post.js
import postAPI from './postAxios';

export const fetchPosts = async (page = 1, limit = 10) => {
  const res = await postAPI.get('/posts', { params: { page, limit } });
  return res.data;
};

export const fetchPostById = async (id) => {
  const res = await postAPI.get(`/posts/${id}`);
  return res.data;
};

export const createPost = async (postData) => {
  const res = await postAPI.post('/posts', postData);
  return res.data;
};

export const updatePost = async (id, postData) => {
  const res = await postAPI.put(`/posts/${id}`, postData);
  return res.data;
};

export const deletePost = async (id) => {
  const res = await postAPI.delete(`/posts/${id}`);
  return res.data;
};

export const likePost = async (id) => {
  const res = await postAPI.post(`/posts/${id}/like`);
  return res.data;
};

export const unlikePost = async (id) => {
  const res = await postAPI.post(`/posts/${id}/unlike`);
  return res.data;
};