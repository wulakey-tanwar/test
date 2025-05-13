// src/api/postAxios.js
import axios from 'axios';
import { getToken } from '../utils/localStorage';

const postAPI = axios.create({
  baseURL: import.meta.env.VITE_POST_API,
  headers: { 'Content-Type': 'application/json' },
});

postAPI.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default postAPI;