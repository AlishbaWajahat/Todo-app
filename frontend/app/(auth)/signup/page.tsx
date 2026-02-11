import { Metadata } from 'next';
import { SignUpForm } from '@/components/auth/SignUpForm';

export const metadata: Metadata = {
  title: 'Sign Up',
  description: 'Create a new Todo App account',
};

/**
 * Sign Up Page
 * Public page for new user registration
 */
export default function SignUpPage() {
  return <SignUpForm />;
}
