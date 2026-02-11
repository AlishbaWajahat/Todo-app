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
 * Set a cookie in the browser
 */
function setCookie(name: string, value: string, days: number = 7) {
  if (typeof window === 'undefined') return;

  const expires = new Date();
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);

  document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
}

/**
 * Get a cookie value by name
 */
function getCookie(name: string): string | null {
  if (typeof window === 'undefined') return null;

  const nameEQ = name + '=';
  const ca = document.cookie.split(';');

  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
  }

  return null;
}

/**
 * Delete a cookie by name
 */
function deleteCookie(name: string) {
  if (typeof window === 'undefined') return;
  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
}

/**
 * Sign up a new user
 *
 * @param data - Sign up form data
 * @returns User and JWT token
 */
export async function signUp(data: SignUpFormData): Promise<AuthResponse> {
  const response = await apiRequest<AuthResponse>('/api/v1/auth/signup/', {
    method: 'POST',
    body: JSON.stringify(data),
  });

  // Store token in cookies for middleware access
  if (typeof window !== 'undefined' && response.token) {
    setCookie('auth_token', response.token, 7);
    setCookie('user', JSON.stringify(response.user), 7);
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
  const response = await apiRequest<AuthResponse>('/api/v1/auth/signin/', {
    method: 'POST',
    body: JSON.stringify(data),
  });

  // Store token in cookies for middleware access
  if (typeof window !== 'undefined' && response.token) {
    setCookie('auth_token', response.token, 7);
    setCookie('user', JSON.stringify(response.user), 7);
  }

  return response;
}

/**
 * Sign out the current user
 * Clears cookies and redirects to sign in page
 */
export function signOut(): void {
  if (typeof window !== 'undefined') {
    deleteCookie('auth_token');
    deleteCookie('user');
    window.location.href = '/signin';
  }
}

/**
 * Get current user from cookies
 *
 * @returns User object or null if not authenticated
 */
export function getCurrentUser(): User | null {
  if (typeof window === 'undefined') {
    return null;
  }

  const userStr = getCookie('user');
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
 * Get current auth token from cookies
 *
 * @returns JWT token or null if not authenticated
 */
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }

  return getCookie('auth_token');
}

/**
 * Check if user is authenticated
 *
 * @returns True if user has a valid token
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null;
}
