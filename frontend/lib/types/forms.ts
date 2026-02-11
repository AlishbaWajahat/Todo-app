/**
 * Sign up form data
 * Data for user registration
 */
export interface SignUpFormData {
  email: string;                 // User's email address
  password: string;              // User's password
  name?: string;                 // User's display name (optional)
}

/**
 * Sign in form data
 * Data for user authentication
 */
export interface SignInFormData {
  email: string;                 // User's email address
  password: string;              // User's password
}

/**
 * Profile form data
 * Data for updating user profile
 */
export interface ProfileFormData {
  name: string;                  // Updated display name
  avatar?: File | null;          // New avatar image file (optional)
}
