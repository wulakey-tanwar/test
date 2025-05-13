import React, { useState, useEffect } from 'react';
import userAPI from '../../api/userAxios';

const UserSearch = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [users, setUsers] = useState([]);

  const handleSearch = async (e) => {
    const term = e.target.value;
    setSearchTerm(term);
    try {
      const res = await userAPI.get(`/search?query=${term}`);
      setUsers(res.data);
    } catch (err) {
      console.error('User search failed:', err);
    }
  };

  useEffect(() => {
    // Optionally load all users initially
    const loadUsers = async () => {
      try {
        const res = await userAPI.get('/users');
        setUsers(res.data);
      } catch (err) {
        console.error('Error loading users:', err);
      }
    };
    loadUsers();
  }, []);

  return (
    <div className="max-w-lg mx-auto mt-8">
      <input
        type="text"
        value={searchTerm}
        onChange={handleSearch}
        className="w-full p-2 border rounded"
        placeholder="Search users..."
      />
      <div className="mt-4">
        {users.map(user => (
          <div key={user.id} className="flex items-center space-x-4 p-2 border-b">
            <img src={user.avatar} alt={user.name} className="w-10 h-10 rounded-full" />
            <div>
              <h3 className="font-semibold">{user.name}</h3>
              <p className="text-sm text-gray-500">{user.email}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UserSearch;