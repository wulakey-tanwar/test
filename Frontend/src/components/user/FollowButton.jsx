import React, { useState } from 'react';

const FollowButton = () => {
  const [isFollowing, setIsFollowing] = useState(false);

  const toggleFollow = () => {
    setIsFollowing(!isFollowing);
  };

  return (
    <button
      onClick={toggleFollow}
      className={`py-2 px-4 rounded-full border ${isFollowing ? 'bg-blue-500 text-white' : 'bg-white text-blue-500 border-blue-500'}`}
    >
      {isFollowing ? 'Following' : 'Follow'}
    </button>
  );
};

export default FollowButton;
