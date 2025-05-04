import React from 'react';
import { Link } from 'react-router-dom';

const PostCard = ({ post }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <img src={post.image} alt={post.caption} className="w-full h-64 object-cover" />
      <div className="p-4">
        <h3 className="text-xl font-semibold">{post.user}</h3>
        <p className="text-sm text-gray-500">{post.caption}</p>
        <Link to={`/post/${post.id}`} className="text-blue-500 mt-2 block">
          View Details
        </Link>
      </div>
    </div>
  );
};

export default PostCard;
