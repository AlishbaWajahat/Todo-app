/**
 * User type definition
 * Represents an authenticated user in the system
 */
export interface User {
  id: string;                    // Unique user identifier (from JWT "sub" claim)
  email: string;                 // User's email address
  name: string | null;           // User's display name (optional)
  avatar_url: string | null;     // URL to user's profile picture (optional)
  created_at: string;            // ISO 8601 timestamp of account creation
  updated_at: string;            // ISO 8601 timestamp of last profile update
}
