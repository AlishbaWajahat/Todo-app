import { User } from '@/lib/types';

export interface ProfileHeaderProps {
  user: User;
}

/**
 * ProfileHeader Component
 * Displays user profile header with avatar and basic info
 */
export function ProfileHeader({ user }: ProfileHeaderProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
        {/* Avatar */}
        <div className="flex-shrink-0">
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-accent-pink to-accent-light flex items-center justify-center text-white text-3xl font-semibold shadow-lg">
            {user.avatar_url ? (
              <img
                src={user.avatar_url}
                alt={user.name || 'User avatar'}
                className="w-full h-full rounded-full object-cover"
              />
            ) : (
              <span>
                {user.name?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase() || 'U'}
              </span>
            )}
          </div>
        </div>

        {/* User Info */}
        <div className="flex-1 text-center sm:text-left">
          <h1 className="text-2xl font-bold text-gray-900 mb-1">
            {user.name || 'User'}
          </h1>
          <p className="text-gray-600 mb-3">{user.email}</p>

          <div className="flex flex-wrap gap-4 text-sm text-gray-500 justify-center sm:justify-start">
            <div className="flex items-center gap-1">
              <svg
                className="w-4 h-4"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>Joined {formatDate(user.created_at)}</span>
            </div>

            {user.updated_at !== user.created_at && (
              <div className="flex items-center gap-1">
                <svg
                  className="w-4 h-4"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>Updated {formatDate(user.updated_at)}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
