'use client';

import { useAuthContext } from '@/components/auth/AuthProvider';
import { signOut as apiSignOut } from '@/lib/api/auth';
import { User } from '@/lib/types';

/**
 * useAuth hook
 * Provides authentication state and methods to components
 */
export function useAuth() {
  const { user, isAuthenticated, isLoading, setUser } = useAuthContext();

  /**
   * Sign out the current user
   */
  const signOut = () => {
    setUser(null);
    apiSignOut();
  };

  /**
   * Update the current user
   */
  const updateUser = (updatedUser: User) => {
    setUser(updatedUser);
    // Update localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    signOut,
    updateUser,
  };
}
