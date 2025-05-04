import React, { useState } from 'react';
import { useUser } from '../../hooks';
import Loader from '../common/Loader';
import ErrorMessage from '../common/ErrorMessage';

const ProfileEdit = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [avatar, setAvatar] = useState('');
  const { user, loading, error } = useUser(1); // Using dummy user ID 1

  if (loading) return <Loader />;
  if (error) return <ErrorMessage message={error} />;

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle profile update (add to state or API)
    console.log('Profile Update:', { name, email, avatar });
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-lg mx-auto mt-8">
      <div className="mb-4">
        <label className="block text-gray-700">Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full p-2 border rounded"
          placeholder="Enter your name"
        />
      </div>
      <div className="mb-4">
        <label className="block text-gray-700">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 border rounded"
          placeholder="Enter your email"
        />
      </div>
      <div className="mb-4">
        <label className="block text-gray-700">Avatar URL</label>
        <input
          type="text"
          value={avatar}
          onChange={(e) => setAvatar(e.target.value)}
          className="w-full p-2 border rounded"
          placeholder="Enter avatar URL"
        />
      </div>
      <button type="submit" className="w-full bg-blue-500 text-white py-2 rounded">
        Update Profile
      </button>
    </form>
  );
};

export default ProfileEdit;
