/**
 * Chat Page
 *
 * Provides a full-page chat interface using ChatKit.
 * Uses dynamic import to avoid SSR issues with browser-only APIs.
 */
'use client';

import dynamic from 'next/dynamic';

// Dynamically import ChatKitWrapper with SSR disabled
const ChatKitWrapper = dynamic(
  () => import('@/components/chat/ChatKitWrapper'),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading chat...</p>
        </div>
      </div>
    ),
  }
);

export default function ChatPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Task Assistant
          </h1>
          <p className="text-gray-600">
            Manage your tasks using natural language. Ask me to add, list, update, complete, or delete tasks.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg" style={{ height: 'calc(100vh - 250px)', minHeight: '500px' }}>
          <ChatKitWrapper />
        </div>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h2 className="text-sm font-semibold text-blue-900 mb-2">Example commands:</h2>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• "Add a task to buy groceries"</li>
            <li>• "Show me all my tasks"</li>
            <li>• "Mark task 3 as complete"</li>
            <li>• "Update task 2 title to 'Buy organic milk'"</li>
            <li>• "Delete task 5"</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
