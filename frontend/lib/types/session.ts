import { User } from './user';

/**
 * Session type definition
 * Represents the user's authentication session
 */
export interface Session {
  token: string;                 // JWT token
  user: User;                    // User information
  expiresAt: string;             // ISO 8601 timestamp of token expiration
}
