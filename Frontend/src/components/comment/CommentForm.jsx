import React, { useState } from 'react';

const CommentForm = () => {
  const [comment, setComment] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Add comment logic
    console.log(comment);
    setComment('');
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center">
      <input
        type="text"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        className="w-full p-2 border rounded-l-md"
        placeholder="Add a comment..."
      />
      <button type="submit" className="p-2 bg-blue-500 text-white rounded-r-md">
        Post
      </button>
    </form>
  );
};

export default CommentForm;
