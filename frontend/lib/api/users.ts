import { apiRequest, apiUpload } from './client';
import { User } from '@/lib/types';

/**
 * Get current user profile
 *
 * @returns User object
 */
export async function getCurrentUserProfile(): Promise<User> {
  return apiRequest<User>('/api/v1/users/me', {
    method: 'GET',
  });
}

/**
 * Update current user profile
 *
 * @param data - Profile update data
 * @returns Updated user object
 */
export async function updateUserProfile(data: {
  name?: string;
}): Promise<User> {
  return apiRequest<User>('/api/v1/users/me', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * Upload user avatar
 *
 * @param file - Avatar image file
 * @returns Updated user object with new avatar URL
 */
export async function uploadAvatar(file: File): Promise<User> {
  const formData = new FormData();
  formData.append('avatar', file);

  return apiUpload<User>('/api/v1/users/me/avatar', formData);
}
