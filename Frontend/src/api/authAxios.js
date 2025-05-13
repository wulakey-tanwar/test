// src/api/authAxios.js
import axios from 'axios';
import { getToken } from '../utils/localStorage';

const authAPI = axios.create({
  baseURL: import.meta.env.VITE_AUTH_API,
  headers: { 'Content-Type': 'application/json' },
});

authAPI.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default authAPI;