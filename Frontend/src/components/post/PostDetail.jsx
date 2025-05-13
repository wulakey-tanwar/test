// src/components/post/PostDetail.jsx
import React from 'react';
import { Link, useParams } from 'react-router-dom';
import { usePost } from '../../hooks';
import Loader from '../common/Loader';
import ErrorMessage from '../common/ErrorMessage';
import CommentList from '../comment/CommentList';
import CommentForm from '../comment/CommentForm';

export default function PostDetail() {
  const { id } = useParams();
  const { post, loading, error } = usePost(id);

  if (loading) return <Loader />;
  if (error)   return <ErrorMessage message={error} />;
  if (!post)  return <ErrorMessage message="Post not found" />;

  const content = post.content || post.message;

  return (
    <article className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden">
      <Link to="/" className="block text-indigo-600 dark:text-indigo-400 hover:underline px-6 pt-6">
        &larr; Back to Feed
      </Link>
      {post.image && (
        <img
          src={post.image}
          alt={post.title}
          className="w-full h-80 object-cover"
        />
      )}
      <div className="p-6 space-y-4">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          {post.title}
        </h1>
        <div className="flex items-center space-x-4">
          {post.author?.avatar && (
            <img
              src={post.author.avatar}
              alt={post.author.name}
              className="w-10 h-10 rounded-full"
            />
          )}
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              {post.author?.name || post.user?.name || 'Unknown'}
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              @{post.author?.username || post.user?.username}
            </p>
          </div>
        </div>
        <p className="text-gray-700 dark:text-gray-300">
          {content}
        </p>
        <time className="text-xs text-gray-500 dark:text-gray-400 block">
          {new Date(post.createdAt).toLocaleString()}
        </time>
      </div>
      <section className="px-6 pb-6 space-y-6">
        <CommentList postId={id} />
        <CommentForm postId={id} />
      </section>
    </article>
  );
}