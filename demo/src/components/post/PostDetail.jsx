import React from 'react';
import { useParams } from 'react-router-dom';
import { usePost } from '../../hooks';
import CommentList from '../comment/CommentList';
import CommentForm from '../comment/CommentForm';
import Loader from '../common/Loader';
import ErrorMessage from '../common/ErrorMessage';

const PostDetail = () => {
  const { id } = useParams();
  const { post, loading, error } = usePost(id);

  if (loading) return <Loader />;
  if (error) return <ErrorMessage message={error} />;
  if (!post) return <ErrorMessage message="Post not found" />;

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

export default PostDetail;
