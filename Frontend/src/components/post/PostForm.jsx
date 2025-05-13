// src/components/post/PostForm.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createPost } from '../../api/post';
import { useAuth } from '../../context/AuthContext';

const PostForm = () => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      
      // Create a preview URL for the image
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handlePost = async (e) => {
    e.preventDefault();
    
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    if (!title.trim() || !content.trim()) {
      setError('Title and content are required');
      return;
    }
    
    try {
      setIsSubmitting(true);
      
      // Create FormData if we have an image file
      let postData;
      if (image) {
        const formData = new FormData();
        formData.append('title', title);
        formData.append('content', content);
        formData.append('image', image);
        postData = formData;
      } else {
        postData = { title, content };
      }
      
      const newPost = await createPost(postData);
      
      // Clear form and redirect to the new post
      setTitle('');
      setContent('');
      setImage(null);
      setImagePreview('');
      
      navigate(`/posts/${newPost._id || newPost.id}`);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create post');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handlePost} className="max-w-lg mx-auto mt-8">
      {error && <div className="text-red-500 mb-4">{error}</div>}
      
      <div className="mb-4">
        <label className="block text-gray-700 mb-2">Title</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full p-2 border rounded-lg"
          placeholder="Enter a title for your post"
          disabled={isSubmitting}
        />
      </div>
      
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Write your post content..."
        className="w-full p-4 border rounded-lg mb-4"
        rows={6}
        disabled={isSubmitting}
      />
      
      <div className="mb-4">
        <label className="block text-gray-700 mb-2">Image</label>
        <input
          type="file"
          onChange={handleImageChange}
          className="w-full p-2 border rounded-lg"
          accept="image/*"
          disabled={isSubmitting}
        />
        
        {imagePreview && (
          <div className="mt-2">
            <img 
              src={imagePreview} 
              alt="Preview" 
              className="max-h-40 rounded"
            />
          </div>
        )}
      </div>
      
      <button 
        type="submit" 
        className="w-full bg-blue-500 text-white py-2 rounded disabled:bg-blue-300"
        disabled={isSubmitting}
      >
        {isSubmitting ? 'Posting...' : 'Post'}
      </button>
    </form>
  );
};

export default PostForm;