import React from 'react';

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'white' | 'gray';
  className?: string;
}

/**
 * Reusable LoadingSpinner component
 * Animated spinner for loading states
 */
export function LoadingSpinner({
  size = 'md',
  color = 'primary',
  className = '',
}: LoadingSpinnerProps) {
  const sizeStyles = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  const colorStyles = {
    primary: 'text-primary',
    white: 'text-white',
    gray: 'text-gray-500',
  };

  return (
    <div className={`inline-block ${className}`} role="status" aria-label="Loading">
      <svg
        className={`animate-spin ${sizeStyles[size]} ${colorStyles[color]}`}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <span className="sr-only">Loading...</span>
    </div>
  );
}

export interface LoadingOverlayProps {
  message?: string;
}

/**
 * Full-screen loading overlay
 * Used for page-level loading states
 */
export function LoadingOverlay({ message = 'Loading...' }: LoadingOverlayProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg p-6 shadow-xl flex flex-col items-center gap-4">
        <LoadingSpinner size="lg" />
        <p className="text-gray-700 font-medium">{message}</p>
      </div>
    </div>
  );
}

export interface LoadingPageProps {
  message?: string;
}

/**
 * Full-page loading component
 * Used for initial page loads
 */
export function LoadingPage({ message = 'Loading...' }: LoadingPageProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-[#C5B0CD] to-[#9B5DE0]">
      <div className="text-center">
        <LoadingSpinner size="lg" color="white" />
        <p className="mt-4 text-white text-lg font-medium">{message}</p>
      </div>
    </div>
  );
}
