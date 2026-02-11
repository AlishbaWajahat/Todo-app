/**
 * ChatKit Widget Component
 *
 * OpenAI ChatKit React integration with toggleable floating widget
 * Features cute purple/pink theme with custom controls
 */
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useTaskRevalidation } from '@/lib/context/TaskRevalidationContext';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

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

export default function ChatKitWidget() {
  const [sessionId, setSessionId] = useState('');
  const [isClient, setIsClient] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [chatKey, setChatKey] = useState(0);
  const [showHistory, setShowHistory] = useState(false);
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [deletingSessionId, setDeletingSessionId] = useState<string | null>(null);

  // Get task revalidation function
  let revalidateTasks: (() => void) | undefined;
  try {
    const context = useTaskRevalidation();
    revalidateTasks = context.revalidateTasks;
  } catch {
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

  // Load chat history from backend
  const loadChatHistory = useCallback(async () => {
    setLoadingHistory(true);
    try {
      const token = getCookie('auth_token');
      if (!token) {
        console.log('No auth token found');
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/chatkit/history`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Loaded chat sessions:', data);
        // Only set sessions from database
        const sessions = data.conversations || [];
        console.log(`Found ${sessions.length} sessions in database`);
        setChatSessions(sessions);
      } else {
        console.error('Failed to load history:', response.status);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    } finally {
      setLoadingHistory(false);
    }
  }, []);

  // Delete chat session
  const deleteChatSession = useCallback(async (sessionId: string, event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent session click

    setDeletingSessionId(sessionId);
    try {
      const token = getCookie('auth_token');
      if (!token) return;

      const response = await fetch(`${API_BASE_URL}/api/v1/chatkit/history/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        // Remove from local state
        setChatSessions(prev => prev.filter(s => s.id !== sessionId));
        console.log(`Deleted session: ${sessionId}`);
      } else {
        console.error('Failed to delete session:', response.status);
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    } finally {
      setDeletingSessionId(null);
    }
  }, []);

  // Note: ChatKit doesn't support programmatic thread loading
  // Sessions are view-only for now

  // Start new chat
  const startNewChat = useCallback(() => {
    setShowHistory(false);
    setChatKey(prev => prev + 1); // Force ChatKit to remount with fresh state
  }, []);


  // Custom fetch with JWT authentication and task revalidation
  const customFetch = useCallback(
    async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const token = getCookie('auth_token');

      const headers: Record<string, string> = {
        ...(init?.headers as Record<string, string> || {}),
        'X-Session-Id': sessionId,
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(input, { ...init, headers });

      if (response.ok && init?.method === 'POST') {
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

  // Initialize ChatKit with built-in history enabled
  const { control } = useChatKit({
    api: {
      url: `${API_BASE_URL}/api/v1/chatkit`,
      domainKey: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || 'todo-app',
      fetch: customFetch,
    },
    startScreen: {
      greeting: "Hi! I'm your task assistant 💜 How can I help you today?",
      prompts: [
        { label: '✨ Add a task', prompt: 'Add a task to buy groceries' },
        { label: '📋 Show tasks', prompt: 'Show me all my tasks' },
        { label: '✅ Complete task', prompt: 'Mark my homework task done' },
        { label: '✏️ Update task', prompt: 'Update task 2 title to "Buy organic milk"' },
      ],
    },
    composer: {
      placeholder: 'Ask me anything about your tasks... 💭',
    },
    header: { enabled: false },
    history: { enabled: false },
    threadItemActions: { feedback: false, retry: true },
  });

  if (!isClient) {
    return null;
  }

  return (
    <>
      {/* Floating toggle button - cute purple/pink theme */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-[9999] w-16 h-16 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center group"
          style={{
            background: 'linear-gradient(135deg, #E879F9 0%, #C084FC 50%, #A78BFA 100%)',
          }}
          aria-label="Open chat assistant"
        >
          <svg
            className="w-8 h-8 text-white group-hover:scale-110 transition-transform"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <span className="absolute -top-1 -right-1 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-pink-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-pink-500"></span>
          </span>
        </button>
      )}

      {/* Chat widget - cute purple/pink theme */}
      {isOpen && (
        <div
          className="fixed bottom-6 right-6 z-[9999] rounded-2xl shadow-2xl overflow-hidden bg-white"
          style={{
            width: '400px',
            height: '620px',
            border: '3px solid',
            borderImage: 'linear-gradient(135deg, #E879F9, #C084FC, #A78BFA) 1',
          }}
        >
          {/* Custom cute header with gradient - RESTORED */}
          <div
            className="flex items-center justify-between px-4 py-3"
            style={{
              background: 'linear-gradient(135deg, #E879F9 0%, #C084FC 50%, #A78BFA 100%)',
            }}
          >
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                <span className="text-xl">💜</span>
              </div>
              <div>
                <h3 className="text-white font-semibold text-sm">Task Assistant</h3>
                <p className="text-white/80 text-xs">Your chats auto-save!</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              {/* New Chat Button */}
              <button
                onClick={startNewChat}
                className="text-white hover:bg-white/20 rounded-full p-1.5 transition-colors"
                aria-label="Start new chat"
                title="New Chat"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M12 4v16m8-8H4" />
                </svg>
              </button>

              {/* Close Button */}
              <button
                onClick={() => setIsOpen(false)}
                className="text-white hover:bg-white/20 rounded-full p-1.5 transition-colors"
                aria-label="Close chat"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* ChatKit component - account for custom header */}
          <div key={chatKey} style={{ height: 'calc(100% - 60px)', width: '100%' }}>
            {control ? (
              <ChatKit control={control} style={{ width: '100%', height: '100%' }} />
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#9333EA' }}>
                <div style={{ textAlign: 'center' }}>
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
                  <p>Loading chat assistant... 💜</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Custom purple/pink theme styles - Enhanced for cutest experience 💜 */}
      <style jsx global>{`
        /* ChatKit custom variables - Cute purple/pink theme */
        openai-chatkit {
          --chatkit-primary-color: #C084FC;
          --chatkit-primary-hover: #E879F9;
          --chatkit-background: #FFFBFE;
          --chatkit-text-primary: #4B0082;
          --chatkit-text-secondary: #9333EA;
          --chatkit-border: #E9D5FF;
        }

        /* Style the header with gradient background - EXTRA CUTE! */
        openai-chatkit::part(header) {
          background: linear-gradient(135deg, #E879F9 0%, #C084FC 50%, #A78BFA 100%) !important;
          border-bottom: 3px solid #A78BFA !important;
          box-shadow: 0 4px 12px rgba(232, 121, 249, 0.3) !important;
        }

        openai-chatkit::part(header-title) {
          color: white !important;
          font-weight: 700 !important;
          font-size: 16px !important;
          text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }

        /* Style header buttons */
        openai-chatkit::part(new-chat-button),
        openai-chatkit::part(history-button) {
          background: rgba(255, 255, 255, 0.2) !important;
          color: white !important;
          border-radius: 8px !important;
          transition: all 0.2s !important;
        }

        openai-chatkit::part(new-chat-button):hover,
        openai-chatkit::part(history-button):hover {
          background: rgba(255, 255, 255, 0.3) !important;
          transform: scale(1.05) !important;
        }

        /* Style history panel with purple theme */
        openai-chatkit::part(history-panel) {
          background: linear-gradient(180deg, #FAF5FF 0%, #FFFFFF 100%) !important;
          border-right: 2px solid #E9D5FF !important;
        }

        openai-chatkit::part(thread-item) {
          border: 2px solid #E9D5FF !important;
          border-radius: 12px !important;
          background: #FFFFFF !important;
          transition: all 0.3s ease !important;
          margin: 8px !important;
        }

        openai-chatkit::part(thread-item):hover {
          border-color: #C084FC !important;
          background: #F3E8FF !important;
          transform: translateX(4px) !important;
          box-shadow: 0 4px 12px rgba(192, 132, 252, 0.2) !important;
        }

        openai-chatkit::part(thread-item-active) {
          border-color: #E879F9 !important;
          background: linear-gradient(135deg, #FAF5FF, #F3E8FF) !important;
          box-shadow: 0 6px 16px rgba(232, 121, 249, 0.3) !important;
        }

        /* Style message bubbles - user messages with gradient */
        openai-chatkit::part(user-message) {
          background: linear-gradient(135deg, #E879F9, #C084FC, #A78BFA) !important;
          color: white !important;
          border-radius: 18px 18px 4px 18px !important;
          box-shadow: 0 4px 12px rgba(232, 121, 249, 0.3) !important;
          padding: 12px 16px !important;
          font-weight: 500 !important;
        }

        /* Style assistant messages with cute purple tint */
        openai-chatkit::part(assistant-message) {
          background: #FAF5FF !important;
          border: 1px solid #E9D5FF !important;
          color: #4B0082 !important;
          border-radius: 4px 18px 18px 18px !important;
          padding: 12px 16px !important;
          box-shadow: 0 2px 8px rgba(147, 51, 234, 0.1) !important;
        }

        /* Style the composer (input area) */
        openai-chatkit::part(composer) {
          border-top: 2px solid #E9D5FF !important;
          background: linear-gradient(180deg, #FFFFFF, #FAF5FF) !important;
        }

        openai-chatkit::part(composer-input) {
          border: 2px solid #E9D5FF !important;
          border-radius: 20px !important;
          background: white !important;
          padding: 12px 16px !important;
          color: #4B0082 !important;
        }

        openai-chatkit::part(composer-input):focus {
          border-color: #C084FC !important;
          box-shadow: 0 0 0 3px rgba(192, 132, 252, 0.2) !important;
        }

        /* Style send button with gradient and hover effect */
        openai-chatkit::part(send-button) {
          background: linear-gradient(135deg, #E879F9, #C084FC) !important;
          color: white !important;
          border-radius: 12px !important;
          padding: 10px 20px !important;
          font-weight: 600 !important;
          transition: all 0.2s !important;
          box-shadow: 0 4px 12px rgba(232, 121, 249, 0.3) !important;
        }

        openai-chatkit::part(send-button):hover {
          transform: translateY(-2px) !important;
          box-shadow: 0 6px 16px rgba(232, 121, 249, 0.4) !important;
        }

        openai-chatkit::part(send-button):active {
          transform: translateY(0) !important;
        }

        /* Style start screen prompts */
        openai-chatkit::part(start-prompt) {
          background: linear-gradient(135deg, #FAF5FF, #F3E8FF) !important;
          border: 2px solid #E9D5FF !important;
          border-radius: 12px !important;
          color: #7C3AED !important;
          transition: all 0.2s !important;
        }

        openai-chatkit::part(start-prompt):hover {
          border-color: #C084FC !important;
          background: linear-gradient(135deg, #E879F9, #C084FC) !important;
          color: white !important;
          transform: scale(1.05) !important;
        }

        /* Scrollbar styling for cute purple theme */
        openai-chatkit::-webkit-scrollbar {
          width: 8px;
        }

        openai-chatkit::-webkit-scrollbar-track {
          background: #FAF5FF;
          border-radius: 4px;
        }

        openai-chatkit::-webkit-scrollbar-thumb {
          background: linear-gradient(180deg, #E879F9, #C084FC);
          border-radius: 4px;
        }

        openai-chatkit::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(180deg, #C084FC, #A78BFA);
        }
      `}</style>
    </>
  );
}
