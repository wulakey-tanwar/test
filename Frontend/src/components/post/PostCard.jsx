// src/components/post/PostCard.jsx
import React from 'react';
import { Link } from 'react-router-dom';

const PostCard = ({ post }) => {
  const { _id, id, title, content, message, image, author, user } = post;
  const postId = _id || id;
  const postContent = content || message;
  const postAuthor = author || user;

  return (
    <Link to={`/posts/${postId}`} className="block transform hover:-translate-y-1 transition">
      <article className="bg-white dark:bg-gray-800 rounded-2xl overflow-hidden shadow-lg hover:shadow-xl p-4 flex flex-col">
        {image && (
          <img
            src={image}
            alt={title}
            className="w-full h-48 object-cover rounded-xl mb-4"
          />
        )}
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">
            {title}
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mt-2 line-clamp-3">
            {postContent}
          </p>
        </div>
        {postAuthor && (
          <div className="mt-4 flex items-center">
            {postAuthor.avatar && (
              <img
                src={postAuthor.avatar}
                alt={postAuthor.name}
                className="w-8 h-8 rounded-full mr-2"
              />
            )}
            <span className="text-sm text-gray-700 dark:text-gray-300">
              {postAuthor.name}
            </span>
          </div>
        )}
      </article>
    </Link>
  );
};

export default PostCard;