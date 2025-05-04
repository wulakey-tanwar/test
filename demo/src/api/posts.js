import { getToken } from '../utils/localStorage.js';
const BASE_URL = import.meta.env.VITE_API_URL;

export async function fetchPosts() {
  const res = await fetch(`${BASE_URL}/posts`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  return res.json();
}

export async function fetchPostById(id) {
  const res = await fetch(`${BASE_URL}/posts/${id}`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  return res.json();
}

export async function createPost(post) {
  const res = await fetch(`${BASE_URL}/posts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(post),
  });
  return res.json();
}

