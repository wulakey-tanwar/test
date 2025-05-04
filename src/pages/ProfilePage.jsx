import React from 'react';
import { useParams } from 'react-router-dom';
import CommentList from '../components/comment/CommentList';
import CommentForm from '../components/comment/CommentForm';

const PostDetailPage = () => {
  const { id } = useParams();

  // Sample post detail (replace with API call)
  const post = {
    user: 'John Doe',
    image: '/assets/sample-post1.jpg',
    caption: 'Amazing view!',
  };

  return (
    <div className="max-w-4xl mx-auto mt-8">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <img src={post.image} alt={post.caption} className="w-full h-64 object-cover" />
        <div className="p-4">
          <h3 className="text-xl font-semibold">{post.user}</h3>
          <p className="text-sm text-gray-500">{post.caption}</p>
        </div>
      </div>
      <div className="mt-8">
        <CommentList />
        <CommentForm />
      </div>
    </div>
  );
};

export default PostDetailPage;
