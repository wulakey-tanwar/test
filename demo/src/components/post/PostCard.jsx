import React from 'react';

const PostCard = ({ title, message, image }) => {
  return (
    <div className="max-w-sm rounded-2xl shadow-lg overflow-hidden bg-white p-4">
      {image && <img className="w-full rounded-xl" src={image} alt={title} />}
      <div className="mt-4">
        <h2 className="text-xl font-bold">{title}</h2>
        <p className="text-gray-600 mt-2">{message}</p>
      </div>
    </div>
  );
};

export default PostCard;
