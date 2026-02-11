'use client';

import React, { createContext, useContext, useRef, useCallback } from 'react';

interface TaskRevalidationContextType {
  revalidateTasks: () => void;
  registerRevalidation: (callback: () => void) => void;
}

const TaskRevalidationContext = createContext<TaskRevalidationContextType | undefined>(undefined);

export function TaskRevalidationProvider({ children }: {
  children: React.ReactNode;
}) {
  const revalidationCallbackRef = useRef<(() => void) | null>(null);

  const registerRevalidation = useCallback((callback: () => void) => {
    revalidationCallbackRef.current = callback;
  }, []);

  const revalidateTasks = useCallback(() => {
    if (revalidationCallbackRef.current) {
      revalidationCallbackRef.current();
    }
  }, []);

  return (
    <TaskRevalidationContext.Provider value={{ revalidateTasks, registerRevalidation }}>
      {children}
    </TaskRevalidationContext.Provider>
  );
}

export function useTaskRevalidation() {
  const context = useContext(TaskRevalidationContext);
  if (context === undefined) {
    throw new Error('useTaskRevalidation must be used within a TaskRevalidationProvider');
  }
  return context;
}
