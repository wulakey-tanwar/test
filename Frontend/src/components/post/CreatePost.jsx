// src/pages/CreatePostPage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createPost } from '../api/post';
import { useAuth } from '../context/AuthContext.jsx';

export default function CreatePostPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    if (!title.trim() || !message.trim()) {
      setError('Title and message are required.');
      return;
    }
    
    try {
      setIsSubmitting(true);
      
      const newPost = await createPost({
        title,
        content: message,
        image: imageUrl || null
      });
      
      // After successful creation, redirect to the new post detail page
      navigate(`/posts/${newPost._id || newPost.id}`);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create post. Please try again.');
      console.error('Error creating post:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-2xl mx-auto bg-white dark:bg-gray-800 shadow-lg rounded-2xl p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          Create New Post
        </h2>
        {error && (
          <div className="mb-4 text-red-600 dark:text-red-400">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700 dark:text-gray-300 mb-1">
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={e => setTitle(e.target.value)}
              className="w-full p-2 border rounded shadow-sm"
              placeholder="Post title"
              disabled={isSubmitting}
            />
          </div>
          <div>
            <label className="block text-gray-700 dark:text-gray-300 mb-1">
              Message
            </label>
            <textarea
              value={message}
              onChange={e => setMessage(e.target.value)}
              className="w-full p-2 border rounded shadow-sm"
              rows={4}
              placeholder="Write your message here"
              disabled={isSubmitting}
            />
          </div>
          <div>
            <label className="block text-gray-700 dark:text-gray-300 mb-1">
              Image URL (optional)
            </label>
            <input
              type="text"
              value={imageUrl}
              onChange={e => setImageUrl(e.target.value)}
              className="w-full p-2 border rounded shadow-sm"
              placeholder="https://..."
              disabled={isSubmitting}
            />
          </div>
          <button
            type="submit"
            className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded-lg transition disabled:bg-indigo-300"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Publishing...' : 'Publish Post'}
          </button>
        </form>
      </div>
    </main>
  );
}