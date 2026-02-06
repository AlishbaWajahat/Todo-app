'use client';

import { useState } from 'react';
import { User } from '@/lib/types';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { ProfileAvatar } from './ProfileAvatar';
import { updateUserProfile, uploadAvatar } from '@/lib/api/users';
import { ApiError } from '@/lib/api/errors';
import { useAuth } from '@/lib/hooks/useAuth';

export interface ProfileFormProps {
  user: User;
  onUpdate: (updatedUser: User) => void;
}

/**
 * ProfileForm Component
 * Form for updating user profile information
 */
export function ProfileForm({ user, onUpdate }: ProfileFormProps) {
  const { updateUser } = useAuth();
  const [formData, setFormData] = useState({
    name: user.name || '',
  });
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const [error, setError] = useState<string>('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string>('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear errors when user starts typing
    if (error) setError('');
    if (successMessage) setSuccessMessage('');
    if (fieldErrors[name]) {
      setFieldErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleAvatarChange = (file: File) => {
    setAvatarFile(file);
    // Create preview URL
    const previewUrl = URL.createObjectURL(file);
    setAvatarPreview(previewUrl);
    if (error) setError('');
    if (successMessage) setSuccessMessage('');
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setFieldErrors({});
    setSuccessMessage('');
    setLoading(true);

    try {
      let updatedUser = user;

      // Update profile name if changed
      if (formData.name !== user.name) {
        updatedUser = await updateUserProfile({
          name: formData.name || undefined,
        });
      }

      // Upload avatar if selected
      if (avatarFile) {
        updatedUser = await uploadAvatar(avatarFile);
        // Clean up preview URL
        if (avatarPreview) {
          URL.revokeObjectURL(avatarPreview);
        }
        setAvatarFile(null);
        setAvatarPreview(null);
      }

      // Update local state and auth context
      onUpdate(updatedUser);
      updateUser(updatedUser);

      setSuccessMessage('Profile updated successfully!');
    } catch (err) {
      if (ApiError.isApiError(err)) {
        if (err.field) {
          setFieldErrors({ [err.field]: err.getUserMessage() });
        } else {
          setError(err.getUserMessage());
        }
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const hasChanges = formData.name !== user.name || avatarFile !== null;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Edit Profile</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {successMessage && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-600">{successMessage}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Avatar Upload */}
        <div className="flex justify-center py-4">
          <ProfileAvatar
            user={user}
            onAvatarChange={handleAvatarChange}
            previewUrl={avatarPreview}
            disabled={loading}
          />
        </div>

        {/* Name Input */}
        <Input
          type="text"
          name="name"
          label="Name"
          value={formData.name}
          onChange={handleChange}
          placeholder="Enter your name"
          maxLength={100}
          disabled={loading}
          error={fieldErrors.name}
          helperText="Your display name (optional)"
        />

        {/* Email (Read-only) */}
        <Input
          type="email"
          name="email"
          label="Email"
          value={user.email}
          disabled
          helperText="Email cannot be changed"
        />

        {/* Submit Button */}
        <div className="flex gap-3 pt-4">
          <Button
            type="submit"
            variant="primary"
            loading={loading}
            disabled={loading || !hasChanges}
            className="flex-1"
          >
            {loading ? 'Saving...' : 'Save Changes'}
          </Button>

          {hasChanges && !loading && (
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setFormData({ name: user.name || '' });
                setAvatarFile(null);
                if (avatarPreview) {
                  URL.revokeObjectURL(avatarPreview);
                }
                setAvatarPreview(null);
                setError('');
                setSuccessMessage('');
              }}
              className="flex-1"
            >
              Cancel
            </Button>
          )}
        </div>
      </form>
    </div>
  );
}
