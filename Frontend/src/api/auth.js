// src/api/auth.js
import axios from 'axios';

const authAPI = axios.create({
  baseURL: import.meta.env.VITE_AUTH_SERVICE_URL, // points to your auth microservice
  headers: { 'Content-Type': 'application/json' },
});

export const loginUser = (credentials) => authAPI.post('/auth/login', credentials);
export const registerUser = (credentials) => authAPI.post('/auth/register', credentials);

export default authAPI;