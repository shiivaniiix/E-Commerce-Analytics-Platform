import React from 'react';
import { useAuth } from '../contexts/AuthContext';

function ProfilePage() {
  const auth = useAuth();
  const user = auth.user;

  if (!user) return <div className="text-center py-12">No profile available.</div>;

  return (
    <div className="max-w-lg">
      <h1 className="text-2xl font-bold mb-4">Profile</h1>
      <div className="space-y-4 rounded-md border p-6">
        <div>
          <div className="text-sm text-slate-500">Name</div>
          <div className="font-medium">{user.first_name} {user.last_name}</div>
        </div>
        <div>
          <div className="text-sm text-slate-500">Email</div>
          <div className="font-medium">{user.email}</div>
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;
