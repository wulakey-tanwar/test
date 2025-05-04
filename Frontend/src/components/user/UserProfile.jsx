// src/components/user/UserProfile.jsx
import React from 'react'
import { Link } from 'react-router-dom'

// Dummy user data
const dummyUser = {
  name:       'John Doe',
  username:   'john_doe',
  avatar:     'https://via.placeholder.com/64',
  postsCount: 12,
  followers:  345,
}

const UserProfile = () => {
  const { name, username, avatar, postsCount, followers } = dummyUser

  return (
    <div className="bg-white dark:bg-gray-800 shadow-lg rounded-2xl p-6">
      <div className="flex items-center space-x-4">
        <img
          src={avatar}
          alt={`${name} avatar`}
          className="w-16 h-16 rounded-full"
        />
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {name}
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            @{username}
          </p>
        </div>
      </div>

      <div className="mt-6 flex space-x-6">
        <div>
          <span className="block text-lg font-semibold">{postsCount}</span>
          <span className="text-gray-500 dark:text-gray-400">Posts</span>
        </div>
        <div>
          <span className="block text-lg font-semibold">{followers}</span>
          <span className="text-gray-500 dark:text-gray-400">Followers</span>
        </div>
      </div>
    </div>
  )
}

export default UserProfile
