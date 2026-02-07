import Link from 'next/link';
import { Buttonnn } from '@/components/ui/Buttonnn';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-[#C5B0CD] to-[#9B5DE0] p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full text-center">
        <div className="mb-6">
          <h1 className="text-6xl font-bold text-primary mb-2">404</h1>
          <div className="w-16 h-1 bg-accent-pink mx-auto rounded-full" />
        </div>

        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Page Not Found
        </h2>

        <p className="text-gray-600 mb-6">
          The page you are looking for does not exist or has been moved.
        </p>

        <div className="flex flex-col gap-3">
          <Link href="/">
            <Buttonnn variant="primary" className="w-full">
              Go to Home
            </Buttonnn>
          </Link>

          <Link href="/dashboard">
            <Buttonnn variant="secondary" className="w-full">
              Go to Dashboard
            </Buttonnn>
          </Link>
        </div>
      </div>
    </div>
  );
}
