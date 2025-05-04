import React from 'react';
import { motion } from 'framer-motion';

const HomePage = () => {
  return (
     <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="max-w-4xl mx-auto mt-8"
  >
   <h2 className="text-3xl font-bold mb-4">Welcome to MySocialApp</h2>
   <p className="text-lg text-gray-600 dark:text-gray-300">
        Connect, share and explore with your community.
    </p>    
   </motion.div>
  );
};
export default HomePage;
