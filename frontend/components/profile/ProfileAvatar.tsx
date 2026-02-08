'use client';

import { useState, useRef } from 'react';
import { User } from '@/lib/types';

export interface ProfileAvatarProps {
  user: User;
  onAvatarChange: (file: File) => void;
  previewUrl?: string | null;
  disabled?: boolean;
}

/**
 * ProfileAvatar Component
 * Avatar display with upload functionality and preview
 */
export function ProfileAvatar({
  user,
  onAvatarChange,
  previewUrl,
  disabled = false,
}: ProfileAvatarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileSelect = (file: File) => {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      alert('Please select a valid image file (JPEG, PNG, GIF, or WebP)');
      return;
    }

    // Validate file size (max 5MB)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
      alert('File size must be less than 5MB');
      return;
    }

    onAvatarChange(file);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (disabled) return;

    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleClick = () => {
    if (!disabled) {
      fileInputRef.current?.click();
    }
  };

  // Construct full URL for avatar (backend serves static files)
  // Handle both absolute URLs (new format) and relative URLs (legacy format)
  const getAvatarUrl = () => {
    if (previewUrl) return previewUrl;
    if (!user.avatar_url) return null;

    // If URL is already absolute (starts with http:// or https://), use it as-is
    if (user.avatar_url.startsWith('http://') || user.avatar_url.startsWith('https://')) {
      return user.avatar_url;
    }

    // Otherwise, prepend the API base URL for relative paths
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return `${apiUrl}${user.avatar_url}`;
  };

  const displayUrl = getAvatarUrl();

  return (
    <div className="flex flex-col items-center gap-3">
      {/* Avatar Display */}
      <div
        className={`relative group ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}`}
        onClick={handleClick}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div
          className={`w-32 h-32 rounded-full bg-gradient-to-br from-accent-pink to-accent-light flex items-center justify-center text-white text-4xl font-semibold shadow-lg transition-all ${
            dragActive ? 'ring-4 ring-primary ring-offset-2' : ''
          } ${disabled ? 'opacity-50' : 'group-hover:opacity-80'}`}
        >
          {displayUrl ? (
            <img
              src={displayUrl}
              alt={user.name || 'User avatar'}
              className="w-full h-full rounded-full object-cover"
            />
          ) : (
            <span>
              {user.name?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase() || 'U'}
            </span>
          )}
        </div>

        {/* Upload Overlay */}
        {!disabled && (
          <div className="absolute inset-0 rounded-full bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all flex items-center justify-center">
            <svg
              className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
        )}
      </div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
        onChange={handleFileInputChange}
        className="hidden"
        disabled={disabled}
      />

      {/* Instructions */}
      {!disabled && (
        <p className="text-sm text-gray-500 text-center max-w-xs">
          Click or drag and drop to upload a new avatar
          <br />
          <span className="text-xs">JPEG, PNG, GIF, or WebP (max 5MB)</span>
        </p>
      )}

      {/* Preview Indicator */}
      {previewUrl && (
        <p className="text-xs text-primary font-medium">
          Preview - Click "Save Changes" to update
        </p>
      )}
    </div>
  );
}
