/**
 * Custom API Error class
 * Extends Error with additional API-specific properties
 */
export class ApiError extends Error {
  public readonly code: string;
  public readonly status: number;
  public readonly field?: string;

  /**
   * Create a new ApiError
   *
   * @param message - Human-readable error message
   * @param code - Machine-readable error code
   * @param status - HTTP status code
   * @param field - Field name for validation errors (optional)
   */
  constructor(
    message: string,
    code: string,
    status: number,
    field?: string
  ) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
    this.field = field;

    // Maintains proper stack trace for where error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ApiError);
    }
  }

  /**
   * Check if error is an ApiError instance
   */
  static isApiError(error: unknown): error is ApiError {
    return error instanceof ApiError;
  }

  /**
   * Get user-friendly error message
   */
  getUserMessage(): string {
    // Map common error codes to user-friendly messages
    const userMessages: Record<string, string> = {
      UNAUTHORIZED: 'Please sign in to continue.',
      FORBIDDEN: 'You do not have permission to perform this action.',
      NOT_FOUND: 'The requested resource was not found.',
      VALIDATION_ERROR: this.message,
      TASK_NOT_FOUND: 'Task not found or you do not have access to it.',
      USER_NOT_FOUND: 'User not found.',
      EMAIL_EXISTS: 'An account with this email already exists.',
      INVALID_CREDENTIALS: 'Invalid email or password.',
      FILE_TOO_LARGE: 'File size exceeds the maximum limit.',
      INTERNAL_ERROR: 'An unexpected error occurred. Please try again later.',
    };

    return userMessages[this.code] || this.message;
  }

  /**
   * Convert to JSON for logging
   */
  toJSON() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      status: this.status,
      field: this.field,
      stack: this.stack,
    };
  }
}
