import React from 'react';
import UserProfile from '../components/user/UserProfile';
import ProfileEdit from '../components/user/ProfileEdit';

const ProfilePage = () => {
  return (
    <div className="max-w-4xl mx-auto mt-8">
      <UserProfile />
      <ProfileEdit />
    </div>
  );
};

export default ProfilePage;
