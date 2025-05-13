// utils/validation.js

export const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
  };
  
  export const validatePassword = (password) => {
    return password.length >= 6;
  };
  
  export const validateUsername = (username) => {
    return username.trim().length >= 3;
  };
  
  export const validateComment = (comment) => {
    return comment.trim().length > 0;
  };