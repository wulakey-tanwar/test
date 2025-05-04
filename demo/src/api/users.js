import { getToken } from '../utils/localStorage.js';
const BASE_URL = import.meta.env.VITE_API_URL;

export async function fetchProfile() {
  const res = await fetch(`${BASE_URL}/users/me`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  return res.json();
}

export async function updateProfile(data) {
  const res = await fetch(`${BASE_URL}/users/me`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(data),
  });
  return res.json();
}
