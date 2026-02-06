import { apiRequest } from './client';
import { User, SignUpFormData, SignInFormData } from '@/lib/types';

/**
 * Authentication response from backend
 */
interface AuthResponse {
  user: User;
  token: string;
}

/**
 * Sign up a new user
 *
 * @param data - Sign up form data
 * @returns User and JWT token
 */
export async function signUp(data: SignUpFormData): Promise<AuthResponse> {
  const response = await apiRequest<AuthResponse>('/api/v1/auth/signup', {
    method: 'POST',
    body: JSON.stringify(data),
  });

  // Store token in localStorage for subsequent requests
  if (typeof window !== 'undefined' && response.token) {
    localStorage.setItem('auth_token', response.token);
    localStorage.setItem('user', JSON.stringify(response.user));
  }

  return response;
}

/**
 * Sign in an existing user
 *
 * @param data - Sign in form data
 * @returns User and JWT token
 */
export async function signIn(data: SignInFormData): Promise<AuthResponse> {
  const response = await apiRequest<AuthResponse>('/api/v1/auth/signin', {
    method: 'POST',
    body: JSON.stringify(data),
  });

  // Store token in localStorage for subsequent requests
  if (typeof window !== 'undefined' && response.token) {
    localStorage.setItem('auth_token', response.token);
    localStorage.setItem('user', JSON.stringify(response.user));
  }

  return response;
}

/**
 * Sign out the current user
 * Clears local storage and redirects to sign in page
 */
export function signOut(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    window.location.href = '/signin';
  }
}

/**
 * Get current user from local storage
 *
 * @returns User object or null if not authenticated
 */
export function getCurrentUser(): User | null {
  if (typeof window === 'undefined') {
    return null;
  }

  const userStr = localStorage.getItem('user');
  if (!userStr) {
    return null;
  }

  try {
    return JSON.parse(userStr) as User;
  } catch {
    return null;
  }
}

/**
 * Get current auth token from local storage
 *
 * @returns JWT token or null if not authenticated
 */
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }

  return localStorage.getItem('auth_token');
}

/**
 * Check if user is authenticated
 *
 * @returns True if user has a valid token
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null;
}
