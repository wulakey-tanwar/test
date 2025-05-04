import React from 'react';
import { useTheme } from '../../context/ThemeContext';

const Header = () => {
  const { theme, toggleTheme } = useTheme();
  return (
    <header className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 p-4 flex justify-between items-center shadow">
      <h1 className="text-xl font-bold text-white">MySocialApp</h1>
      <button
        onClick={toggleTheme}
        className="bg-white text-gray-800 px-3 py-1 rounded shadow hover:bg-gray-200"
      >
        {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
      </button>
    </header>
  );
};
export default Header;