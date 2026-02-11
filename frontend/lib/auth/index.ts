import { auth } from './config';

/**
 * Export the configured Better Auth instance
 * This is used throughout the application for authentication
 */
export { auth };

/**
 * Export auth API for client-side usage
 */
export const authClient = auth;
