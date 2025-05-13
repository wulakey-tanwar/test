// src/api/userAxios.js
import axios from 'axios';
import { getToken } from '../utils/localStorage';

const userAPI = axios.create({
  baseURL: import.meta.env.VITE_USER_API,
  headers: { 'Content-Type': 'application/json' },
});

userAPI.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default userAPI;