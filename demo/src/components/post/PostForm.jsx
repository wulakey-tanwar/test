import React, { useState } from 'react';

const PostForm = () => {
  const [caption, setCaption] = useState('');
  const [image, setImage] = useState('');

  const handlePost = (e) => {
    e.preventDefault();
    // Handle post submission (add to state or API)
    console.log('New Post:', { caption, image });
    setCaption('');
    setImage('');
  };

  return (
    <form onSubmit={handlePost} className="max-w-lg mx-auto mt-8">
      <textarea
        value={caption}
        onChange={(e) => setCaption(e.target.value)}
        placeholder="Write a caption..."
        className="w-full p-4 border rounded-lg mb-4"
      />
      <input
        type="file"
        onChange={(e) => setImage(e.target.files[0])}
        className="w-full p-2 border rounded-lg mb-4"
      />
      <button type="submit" className="w-full bg-blue-500 text-white py-2 rounded">Post</button>
    </form>
  );
};

export default PostForm;
