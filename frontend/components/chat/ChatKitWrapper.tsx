/**
 * ChatKitWrapper Component
 *
 * Integrates OpenAI ChatKit UI with the FastAPI backend chat endpoint.
 * Handles JWT authentication, session management, and conversation persistence.
 */
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useTaskRevalidation } from '@/lib/context/TaskRevalidationContext';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Get JWT token from cookies
 */
function getCookie(name: string): string | null {
  if (typeof window === 'undefined') return null;

  const nameEQ = name + '=';
  const ca = document.cookie.split(';');

  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
  }

  return null;
}

export default function ChatKitWrapper() {
  const [sessionId, setSessionId] = useState('');
  const [isClient, setIsClient] = useState(false);

  // Get task revalidation function (may be undefined if not in dashboard context)
  let revalidateTasks: (() => void) | undefined;
  try {
    const context = useTaskRevalidation();
    revalidateTasks = context.revalidateTasks;
  } catch {
    // Context not available - that's okay, we're probably on the chat page
    revalidateTasks = undefined;
  }

  // Initialize session ID
  useEffect(() => {
    setIsClient(true);
    const getOrCreateSessionId = () => {
      let sid = localStorage.getItem('chatkit_session_id');
      if (!sid) {
        sid = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
        localStorage.setItem('chatkit_session_id', sid);
      }
      return sid;
    };
    setSessionId(getOrCreateSessionId());
  }, []);

  // Custom fetch with JWT authentication and task revalidation
  const customFetch = useCallback(
    async (input: RequestInfo | URL, init?: RequestInit) => {
      const token = getCookie('auth_token');

      const headers: Record<string, string> = {
        ...(init?.headers as Record<string, string> || {}),
        'X-Session-Id': sessionId,
      };

      // Add auth headers only if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(input, { ...init, headers });

      // Intercept response to check for task operations
      if (response.ok && init?.method === 'POST') {
        // Trigger revalidation after any POST request (which includes message sends)
        // We use a delay to ensure backend has committed changes
        setTimeout(() => {
          if (revalidateTasks) {
            revalidateTasks();
          }
        }, 500);
      }

      return response;
    },
    [sessionId, revalidateTasks]
  );

  // Initialize ChatKit
  const { control } = useChatKit({
    api: {
      url: `${API_BASE_URL}/api/v1/chatkit`,
      domainKey: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || 'todo-app',
      fetch: customFetch,
    },
    startScreen: {
      greeting: "Hello! I can help you manage your tasks.",
      prompts: [
        { label: 'Add a task', prompt: 'Add a task to buy groceries' },
        { label: 'Show my tasks', prompt: 'Show me all my tasks' },
        { label: 'Complete a task', prompt: 'Mark task 1 as complete' },
        { label: 'Update a task', prompt: 'Update task 2 title to "Buy organic milk"' },
      ],
    },
    composer: {
      placeholder: 'Ask me to manage your tasks...',
    },
    header: { enabled: false },
    history: { enabled: true, showDelete: false, showRename: false },
    threadItemActions: { feedback: false, retry: true },
  });

  // Don't render until client-side hydration is complete
  if (!isClient) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading chat...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full">
      <ChatKit control={control} style={{ width: '100%', height: '100%' }} />
    </div>
  );
}
