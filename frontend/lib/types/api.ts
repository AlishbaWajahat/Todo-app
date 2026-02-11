/**
 * API Response wrapper
 * Generic wrapper for successful API responses
 */
export interface ApiResponse<T> {
  data: T;                       // Response data (typed)
  message?: string;              // Optional success message
}

/**
 * API Error
 * Represents an error response from the API
 */
export interface ApiError {
  detail: string;                // Human-readable error message
  code: string;                  // Machine-readable error code
  field?: string;                // Field name for validation errors (optional)
}

/**
 * Common error codes
 */
export enum ErrorCode {
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  TASK_NOT_FOUND = 'TASK_NOT_FOUND',
  USER_NOT_FOUND = 'USER_NOT_FOUND',
  EMAIL_EXISTS = 'EMAIL_EXISTS',
  INVALID_CREDENTIALS = 'INVALID_CREDENTIALS',
  FILE_TOO_LARGE = 'FILE_TOO_LARGE',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
}
