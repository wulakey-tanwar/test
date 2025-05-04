import React from 'react'
import PostDetail from '../components/post/PostDetail'

export default function PostDetailPage() {
  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <PostDetail />
      </div>
    </main>
  )
}
