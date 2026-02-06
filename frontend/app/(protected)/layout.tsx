import { Metadata } from 'next';
import { Header } from '@/components/layout/Header';

export const metadata: Metadata = {
  title: {
    template: '%s | Todo App',
    default: 'Dashboard',
  },
};

/**
 * Protected route group layout
 * Wraps all authenticated pages with consistent structure
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
      <main id="main-content" className="container mx-auto px-4 py-8" tabIndex={-1}>
        {children}
      </main>
    </div>
  );
}
