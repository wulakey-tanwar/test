import React from 'react';

const comments = [
  { user: 'Jane Smith', comment: 'Beautiful!' },
  { user: 'John Doe', comment: 'Wish I was there!' },
];

const CommentList = () => (
  <div>
    {comments.map((comment, index) => (
      <div key={index} className="border-b pb-2 mb-2">
        <p className="font-semibold">{comment.user}:</p>
        <p>{comment.comment}</p>
      </div>
    ))}
  </div>
);

export default CommentList;
