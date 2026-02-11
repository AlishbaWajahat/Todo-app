'use client';

import { Task } from '@/lib/types';
import { TaskCard } from './TaskCard';

export interface TaskListProps {
  tasks: Task[];
  onUpdate: (updatedTask: Task) => void;
  onDelete: (taskId: number) => void;
  isLoading?: boolean;
}

/**
 * TaskList Component
 * Displays a list of tasks or an empty state message
 */
export function TaskList({ tasks, onUpdate, onDelete, isLoading = false }: TaskListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="bg-white rounded-lg shadow-md p-4 animate-pulse"
          >
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 bg-gray-200 rounded" />
              <div className="flex-1">
                <div className="h-5 bg-gray-200 rounded w-3/4 mb-2" />
                <div className="h-4 bg-gray-200 rounded w-full mb-2" />
                <div className="h-4 bg-gray-200 rounded w-1/2" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-12 text-center">
        <div className="mb-4">
          <div className="w-16 h-16 bg-gray-100 rounded-full mx-auto flex items-center justify-center">
            <svg
              className="w-8 h-8 text-gray-400"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
        </div>

        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          No tasks yet
        </h3>
        <p className="text-gray-600 mb-6">
          Get started by creating your first task!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onUpdate={onUpdate}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
