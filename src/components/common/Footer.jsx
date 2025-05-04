import React from 'react'

export default function Footer() {
  return (
    <footer className="bg-gray-100 dark:bg-gray-900 text-gray-700 dark:text-gray-300 py-6">
      <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
        <span className="text-sm">
          © {new Date().getFullYear()} MySocialApp. All rights reserved.
          lebljdenjln
        </span>
        <nav className="flex space-x-4">
          <a
            href="/privacy"
            className="text-sm hover:text-indigo-500 dark:hover:text-indigo-400 transition"
          >
            Privacy Policy
          </a>
          <a
            href="/terms"
            className="text-sm hover:text-indigo-500 dark:hover:text-indigo-400 transition"
          >
            Terms of Service
          </a>
        </nav>
      </div>
    </footer>
  )
}
