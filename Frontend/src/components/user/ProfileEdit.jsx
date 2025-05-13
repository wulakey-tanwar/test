import React, { useState } from 'react';
import userAPI from '../../api/userAxios';

const initial = {
  name: 'John Doe',
  email: 'john@example.com',
  avatar: 'https://via.placeholder.com/150',
};

const ProfileEdit = () => {
  const [name, setName] = useState(initial.name);
  const [email, setEmail] = useState(initial.email);
  const [avatar, setAvatar] = useState(initial.avatar);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await userAPI.put('/profile', { name, email, avatar });
      console.log('Updated:', res.data);
    } catch (error) {
      console.error('Profile update failed:', error);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 shadow-lg rounded-2xl p-6">
      <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-4">Edit Profile</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Name */}
        <div>
          <label className="block text-gray-700 dark:text-gray-300 mb-1">Name</label>
          <input type="text" value={name} onChange={e => setName(e.target.value)} className="w-full p-2 border rounded" />
        </div>
        {/* Email */}
        <div>
          <label className="block text-gray-700 dark:text-gray-300 mb-1">Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} className="w-full p-2 border rounded" />
        </div>
        {/* Avatar */}
        <div>
          <label className="block text-gray-700 dark:text-gray-300 mb-1">Avatar URL</label>
          <input type="text" value={avatar} onChange={e => setAvatar(e.target.value)} className="w-full p-2 border rounded" />
        </div>
        <button type="submit" className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-500 transition">
          Save Changes
        </button>
      </form>
    </div>
  );
};

export default ProfileEdit;