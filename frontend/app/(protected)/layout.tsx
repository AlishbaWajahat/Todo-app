'use client';

import { Header } from '@/components/layout/Header';
import { ClientLayoutWrapper } from '@/components/layout/ClientLayoutWrapper';
import { TaskRevalidationProvider } from '@/lib/context/TaskRevalidationContext';

/**
 * Protected route group layout
 * Wraps all authenticated pages with consistent structure
 * Includes floating ChatKit widget for task management assistance
 */
export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with navigation and user menu */}
      <Header />

      {/* Main content with skip-to-content target */}
      <main id="main-content" className="max-w-[800px] mx-auto px-4 py-8" tabIndex={-1}>
        <TaskRevalidationProvider>
          <ClientLayoutWrapper>
            {children}
          </ClientLayoutWrapper>
        </TaskRevalidationProvider>
      </main>
    </div>
  );
}
