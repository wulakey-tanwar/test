// Dummy data for posts
export const dummyPosts = [
  {
    id: 1,
    user: 'John Doe',
    image: 'https://source.unsplash.com/400x300/?mountains',
    caption: 'Amazing view!',
  },
  {
    id: 2,
    user: 'Jane Smith',
    image: 'https://source.unsplash.com/400x300/?beach',
    caption: 'Love this place!',
  },
  {
    id: 3,
    user: 'Alice Johnson',
    image: 'https://source.unsplash.com/400x300/?city,night',
    caption: 'Urban adventures!',
  },
];

// Dummy data for users
export const dummyUsers = [
  {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    avatar: 'https://source.unsplash.com/100x100/?portrait',
  },
  {
    id: 2,
    name: 'Jane Smith',
    email: 'jane@example.com',
    avatar: 'https://source.unsplash.com/100x100/?woman',
  },
  {
    id: 3,
    name: 'Alice Johnson',
    email: 'alice@example.com',
    avatar: 'https://source.unsplash.com/100x100/?girl',
  },
];

// Mock API functions
export const getPosts = () => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(dummyPosts), 1000);
  });
};

export const getPostById = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(dummyPosts.find(post => post.id === parseInt(id))), 1000);
  });
};

export const getUserById = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(dummyUsers.find(user => user.id === parseInt(id))), 1000);
  });
};

export const login = (email, password) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const user = dummyUsers.find(u => u.email === email);
      if (user) {
        resolve({ success: true, user });
      } else {
        resolve({ success: false, message: 'Invalid credentials' });
      }
    }, 1000);
  });
};

export const register = (email, password, name) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newUser = {
        id: dummyUsers.length + 1,
        name,
        email,
        avatar: 'https://source.unsplash.com/100x100/?newuser',
      };
      dummyUsers.push(newUser);
      resolve({ success: true, user: newUser });
    }, 1000);
  });
}; 