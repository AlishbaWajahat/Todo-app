import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Authentication',
};

/**
 * Auth route group layout
 * Wraps authentication pages (signin, signup) with consistent styling
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#C5B0CD] to-[#9B5DE0] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo/Brand */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Todo App</h1>
          <p className="text-white/80">Manage your tasks efficiently</p>
        </div>

        {/* Auth form container */}
        <div className="bg-white rounded-lg shadow-xl p-8">
          {children}
        </div>

        {/* Footer */}
        <p className="text-center text-white/60 text-sm mt-6">
          &copy; 2026 Todo App. All rights reserved.
        </p>
      </div>
    </div>
  );
}
