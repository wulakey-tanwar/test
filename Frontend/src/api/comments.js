import { getToken } from '../utils/localStorage.js';
const BASE_URL = import.meta.env.VITE_API_URL;

export async function fetchComments(postId) {
  const res = await fetch(`${BASE_URL}/posts/${postId}/comments`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  return res.json();
}

export async function createComment(postId, comment) {
  const res = await fetch(`${BASE_URL}/posts/${postId}/comments`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(comment),
  });
  return res.json();
}

