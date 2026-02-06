import { Metadata } from 'next';
import { SignInForm } from '@/components/auth/SignInForm';

export const metadata: Metadata = {
  title: 'Sign In',
  description: 'Sign in to your Todo App account',
};

/**
 * Sign In Page
 * Public page for user authentication
 */
export default function SignInPage() {
  return <SignInForm />;
}
