import userAPI from './userAxios';

export async function fetchProfile() {
  const res = await userAPI.get('/users/me');
  return res.data;
}

export async function updateProfile(data) {
  const res = await userAPI.patch('/users/me', data);
  return res.data;
}