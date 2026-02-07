import { ApiError } from './errors';

/**
 * Base API URL from environment variable
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Debug: Log the API URL being used (will show in browser console)
if (typeof window !== 'undefined') {
  console.log('🔍 API_BASE_URL:', API_BASE_URL);
  console.log('🔍 NEXT_PUBLIC_API_URL env:', process.env.NEXT_PUBLIC_API_URL);
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
 * Get JWT token from cookies
 */
async function getAuthToken(): Promise<string | null> {
  if (typeof window === 'undefined') {
    return null;
  }

  // Read token from cookies (set by auth.ts)
  return getCookie('auth_token');
}

/**
 * API request wrapper with automatic JWT injection
 *
 * @param endpoint - API endpoint (e.g., '/api/v1/tasks')
 * @param options - Fetch options
 * @returns Parsed JSON response
 * @throws ApiError on HTTP errors
 */
export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const token = await getAuthToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string>),
  };

  // Add Authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle 401 Unauthorized - redirect to signin
  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      window.location.href = '/signin';
    }
    throw new ApiError('Authentication required', 'UNAUTHORIZED', 401);
  }

  // Handle other HTTP errors
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      throw new ApiError(
        'An unexpected error occurred',
        'INTERNAL_ERROR',
        response.status
      );
    }

    throw new ApiError(
      errorData.detail || 'An error occurred',
      errorData.code || 'UNKNOWN_ERROR',
      response.status,
      errorData.field
    );
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  // Parse and return JSON response
  return response.json();
}

/**
 * API request for multipart/form-data (file uploads)
 *
 * @param endpoint - API endpoint
 * @param formData - FormData object
 * @returns Parsed JSON response
 * @throws ApiError on HTTP errors
 */
export async function apiUpload<T>(
  endpoint: string,
  formData: FormData
): Promise<T> {
  const token = await getAuthToken();

  const headers: HeadersInit = {};

  // Add Authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Note: Don't set Content-Type for FormData - browser sets it automatically with boundary

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: formData,
  });

  // Handle 401 Unauthorized
  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      window.location.href = '/signin';
    }
    throw new ApiError('Authentication required', 'UNAUTHORIZED', 401);
  }

  // Handle other HTTP errors
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      throw new ApiError(
        'An unexpected error occurred',
        'INTERNAL_ERROR',
        response.status
      );
    }

    throw new ApiError(
      errorData.detail || 'An error occurred',
      errorData.code || 'UNKNOWN_ERROR',
      response.status,
      errorData.field
    );
  }

  return response.json();
}
