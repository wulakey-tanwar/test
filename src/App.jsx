import React from 'react';
import Header from './components/common/Header';
import Footer from './components/common/Footer';
import HomePage from './pages/HomePage';
import { ThemeProvider } from './context/ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <div className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 min-h-screen flex flex-col">
        <Header />
        <main className="flex-grow p-4">
          <HomePage />
        </main>
        <Footer />
      </div>
    </ThemeProvider>
  );
}
export default App;