import React from 'react';
import { Link } from 'react-router-dom';
import FollowButton from '../components/user/FollowButton';

const UserProfile = () => {
  return (
    <div className="max-w-2xl mx-auto mt-8 bg-white shadow-lg rounded-lg">
      <div className="p-6">
        <div className="flex items-center space-x-4">
          <img src="/assets/sample-avatar.jpg" alt="User Avatar" className="w-16 h-16 rounded-full" />
          <div>
            <h2 className="text-2xl font-bold">John Doe</h2>
            <p className="text-gray-600">@john_doe</p>
          </div>
        </div>
        <FollowButton />
      </div>
      <div className="border-t border-gray-200 p-6">
        <h3 className="text-xl font-semibold">Posts</h3>
        {/* Display user's posts here */}
      </div>
    </div>
  );
};

export default UserProfile;
