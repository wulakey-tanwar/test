import React, { useState } from 'react';
import { dummyUsers } from '../../api';

const UserSearch = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [users, setUsers] = useState(dummyUsers);

  const handleSearch = (e) => {
    const term = e.target.value;
    setSearchTerm(term);
    const filteredUsers = dummyUsers.filter(user =>
      user.name.toLowerCase().includes(term.toLowerCase()) ||
      user.email.toLowerCase().includes(term.toLowerCase())
    );
    setUsers(filteredUsers);
  };

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
