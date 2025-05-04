import React from 'react';
import { usePosts } from '../../hooks';
import PostCard from './PostCard';
import Loader from '../common/Loader';
import ErrorMessage from '../common/ErrorMessage';

const PostList = () => {
  const { posts, loading, error } = usePosts();

  if (loading) return <Loader />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {posts.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
};

export default PostList;
