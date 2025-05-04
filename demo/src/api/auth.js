import { getToken, setToken, clearToken } from '../utils/localStorage.js';

const BASE_URL = import.meta.env.VITE_API_URL;

export async function login(credentials) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });
  const data = await res.json();
  if (res.ok) setToken(data.token);
  return data;
}

export async function register(userInfo) {
  const res = await fetch(`${BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userInfo),
  });
  const data = await res.json();
  if (res.ok) setToken(data.token);
  return data;
}

export function logout() {
  clearToken();
}
