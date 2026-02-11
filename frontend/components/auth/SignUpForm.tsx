'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Input } from '@/components/ui/Input';
import { Buttonnn } from '@/components/ui/Buttonnn';
import { signUp } from '@/lib/api/auth';
import { ApiError } from '@/lib/api/errors';
import { SignUpFormData } from '@/lib/types';

/**
 * Sign Up Form Component
 * Handles new user registration with email, password, and optional name
 */
export function SignUpForm() {
  const router = useRouter();
  const [formData, setFormData] = useState<SignUpFormData>({
    email: '',
    password: '',
    name: '',
  });
  const [error, setError] = useState<string>('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setFieldErrors({});
    setLoading(true);

    try {
      await signUp(formData);

      // Redirect to dashboard after successful signup
      router.push('/dashboard');
    } catch (err) {
      if (ApiError.isApiError(err)) {
        // Handle field-specific errors
        if (err.field) {
          setFieldErrors({ [err.field]: err.getUserMessage() });
        } else {
          setError(err.getUserMessage());
        }
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear errors when user starts typing
    if (error) setError('');
    if (fieldErrors[name]) {
      setFieldErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
        Create Account
      </h2>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          type="email"
          name="email"
          label="Email"
          value={formData.email}
          onChange={handleChange}
          placeholder="you@example.com"
          required
          autoComplete="email"
          disabled={loading}
          error={fieldErrors.email}
        />

        <Input
          type="password"
          name="password"
          label="Password"
          value={formData.password}
          onChange={handleChange}
          placeholder="At least 8 characters"
          required
          minLength={8}
          autoComplete="new-password"
          disabled={loading}
          error={fieldErrors.password}
          helperText="Must be at least 8 characters"
        />

        <Input
          type="text"
          name="name"
          label="Name"
          value={formData.name}
          onChange={handleChange}
          placeholder="Your name (optional)"
          maxLength={100}
          autoComplete="name"
          disabled={loading}
          error={fieldErrors.name}
        />

        <Buttonnn
          type="submit"
          variant="primary"
          className="w-full"
          loading={loading}
          disabled={loading}
        >
          {loading ? 'Creating account...' : 'Sign Up'}
        </Buttonnn>
      </form>

      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600">
          Already have an account?{' '}
          <Link
            href="/signin"
            className="text-primary hover:text-primary-dark font-medium"
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
