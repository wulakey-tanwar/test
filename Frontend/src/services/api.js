import axios from 'axios';

// Create axios instances for different services
const authApi = axios.create({
  baseURL: process.env.REACT_APP_AUTH_SERVICE_URL || 'http://localhost:8000',
});

const userApi = axios.create({
  baseURL: process.env.REACT_APP_USER_SERVICE_URL || 'http://localhost:8001',
});

const postApi = axios.create({
  baseURL: process.env.REACT_APP_POST_SERVICE_URL || 'http://localhost:8002',
});

const commentApi = axios.create({
  baseURL: process.env.REACT_APP_COMMENT_SERVICE_URL || 'http://localhost:8003',
});

// Auth Service API calls
export const authService = {
  login: (credentials) => authApi.post('/auth/login', credentials),
  register: (userData) => authApi.post('/auth/register', userData),
  logout: () => authApi.post('/auth/logout'),
};

// User Service API calls
export const userService = {
  getProfile: (userId) => userApi.get(`/users/${userId}`),
  updateProfile: (userId, data) => userApi.put(`/users/${userId}`, data),
};

// Post Service API calls
export const postService = {
  getPosts: () => postApi.get('/posts'),
  getPost: (postId) => postApi.get(`/posts/${postId}`),
  createPost: (postData) => postApi.post('/posts', postData),
  updatePost: (postId, postData) => postApi.put(`/posts/${postId}`, postData),
  deletePost: (postId) => postApi.delete(`/posts/${postId}`),
};

// Comment Service API calls
export const commentService = {
  getComments: (postId) => commentApi.get(`/comments/post/${postId}`),
  createComment: (commentData) => commentApi.post('/comments', commentData),
  updateComment: (commentId, commentData) => commentApi.put(`/comments/${commentId}`, commentData),
  deleteComment: (commentId) => commentApi.delete(`/comments/${commentId}`),
};

// Add request interceptor to include auth token
const addAuthToken = (config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

[authApi, userApi, postApi, commentApi].forEach(api => {
  api.interceptors.request.use(addAuthToken);
});

// Add response interceptor to handle errors
const handleResponseError = (error) => {
  if (error.response?.status === 401) {
    // Handle unauthorized access
    localStorage.removeItem('token');
    window.location.href = '/login';
  }
  return Promise.reject(error);
};

[authApi, userApi, postApi, commentApi].forEach(api => {
  api.interceptors.response.use(response => response, handleResponseError);
}); 