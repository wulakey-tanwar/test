// src/pages/ProfilePage.jsx
import React from 'react'
import UserProfile from '../components/user/UserProfile'
import ProfileEdit  from '../components/user/ProfileEdit'

const ProfilePage = () => (
  <main className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div className="max-w-4xl mx-auto px-4 space-y-12">
      <UserProfile />
      <ProfileEdit />
    </div>
  </main>
)

export default ProfilePage
