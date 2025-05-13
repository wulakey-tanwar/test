// src/api/commentAxios.js
import axios from 'axios';
import { getToken } from '../utils/localStorage';

const commentAPI = axios.create({
  baseURL: import.meta.env.VITE_COMMENT_API,
  headers: { 'Content-Type': 'application/json' },
});

commentAPI.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default commentAPI;