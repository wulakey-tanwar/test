// src/components/post/PostCard.jsx
import React from 'react'
import { Link } from 'react-router-dom'

const PostCard = ({ post }) => {
  const { id, title, message, image, author } = post

  return (
    <Link to={`/posts/${id}`} className="block transform hover:-translate-y-1 transition">
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
            {message}
          </p>
        </div>
        {author && (
          <div className="mt-4 flex items-center">
            {author.avatar && (
              <img
                src={author.avatar}
                alt={author.name}
                className="w-8 h-8 rounded-full mr-2"
              />
            )}
            <span className="text-sm text-gray-700 dark:text-gray-300">
              {author.name}
            </span>
          </div>
        )}
      </article>
    </Link>
  )
}

export default PostCard
