/**
 * Client Layout Wrapper
 *
 * Wraps the protected layout content with client-side features like ChatKitWidget.
 * This allows the parent layout to remain a Server Component for metadata support.
 */
'use client';

import dynamic from 'next/dynamic';
import { ReactNode } from 'react';

// Dynamically import ChatKitWidget with SSR disabled (client-only component)
const ChatKitWidget = dynamic(
  () => import('@/components/chat/ChatKitWidget'),
  { ssr: false }
);

interface ClientLayoutWrapperProps {
  children: ReactNode;
}

export function ClientLayoutWrapper({ children }: ClientLayoutWrapperProps) {
  return (
    <>
      {children}
      {/* Floating ChatKit Widget - appears on all protected pages */}
      <ChatKitWidget />
    </>
  );
}
