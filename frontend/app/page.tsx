'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/api/auth';
import { LoadingPage } from '@/components/ui/LoadingSpinner';

/**
 * Home Page
 * Redirects authenticated users to dashboard, unauthenticated users to signin
 */
export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check authentication status and redirect accordingly
    if (isAuthenticated()) {
      router.push('/dashboard');
    } else {
      router.push('/signin');
    }
  }, [router]);

  // Show loading while redirecting
  return <LoadingPage message="Redirecting..." />;
}
