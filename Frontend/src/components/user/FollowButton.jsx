import React, { useState } from 'react';
import userAPI from '../../api/userAxios';

const FollowButton = ({ userId }) => {
  const [isFollowing, setIsFollowing] = useState(false);

  const toggleFollow = async () => {
    try {
      const endpoint = isFollowing ? `/unfollow/${userId}` : `/follow/${userId}`;
      await userAPI.post(endpoint);
      setIsFollowing(!isFollowing);
    } catch (error) {
      console.error('Follow/unfollow error:', error);
    }
  };

  return (
    <button
      onClick={toggleFollow}
      className={`py-2 px-4 rounded-full border ${
        isFollowing ? 'bg-blue-500 text-white' : 'bg-white text-blue-500 border-blue-500'
      }`}
    >
      {isFollowing ? 'Following' : 'Follow'}
    </button>
  );
};

export default FollowButton;