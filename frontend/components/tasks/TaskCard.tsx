'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Task } from '@/lib/types';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { toggleTaskComplete } from '@/lib/api/tasks';
import { ApiError } from '@/lib/api/errors';

export interface TaskCardProps {
  task: Task;
  onUpdate: (updatedTask: Task) => void;
  onDelete: (taskId: number) => void;
}

/**
 * TaskCard Component
 * Displays a single task with completion toggle, edit, and delete actions
 */
export function TaskCard({ task, onUpdate, onDelete }: TaskCardProps) {
  const [isToggling, setIsToggling] = useState(false);
  const [error, setError] = useState<string>('');

  const handleToggleComplete = async () => {
    setIsToggling(true);
    setError('');

    // Optimistic update
    const optimisticTask = { ...task, completed: !task.completed };
    onUpdate(optimisticTask);

    try {
      const updatedTask = await toggleTaskComplete(task.id);
      onUpdate(updatedTask);
    } catch (err) {
      // Revert optimistic update on error
      onUpdate(task);

      if (ApiError.isApiError(err)) {
        setError(err.getUserMessage());
      } else {
        setError('Failed to update task');
      }
    } finally {
      setIsToggling(false);
    }
  };

  const getPriorityColor = (priority: string | null) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const isOverdue = (dueDate: string | null) => {
    if (!dueDate || task.completed) return false;
    return new Date(dueDate) < new Date();
  };

  return (
    <Card hover className="transition-all">
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <button
          onClick={handleToggleComplete}
          disabled={isToggling}
          className="mt-1 flex-shrink-0"
          aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
        >
          <div
            className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
              task.completed
                ? 'bg-primary border-primary'
                : 'border-gray-300 hover:border-primary'
            } ${isToggling ? 'opacity-50' : ''}`}
          >
            {task.completed && (
              <svg
                className="w-3 h-3 text-white"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="3"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>
        </button>

        {/* Task Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-2">
            <h3
              className={`text-lg font-semibold ${
                task.completed
                  ? 'text-gray-400 line-through'
                  : 'text-gray-900'
              }`}
            >
              {task.title}
            </h3>

            {/* Actions */}
            <div className="flex items-center gap-1 flex-shrink-0">
              <Link href={`/tasks/${task.id}/edit`}>
                <Button
                  variant="ghost"
                  size="sm"
                  className="p-1.5"
                  aria-label="Edit task"
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </Button>
              </Link>

              <Button
                variant="ghost"
                size="sm"
                className="p-1.5 text-red-600 hover:bg-red-50"
                onClick={() => onDelete(task.id)}
                aria-label="Delete task"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </Button>
            </div>
          </div>

          {/* Description */}
          {task.description && (
            <p
              className={`text-sm mb-3 ${
                task.completed ? 'text-gray-400' : 'text-gray-600'
              }`}
            >
              {task.description}
            </p>
          )}

          {/* Metadata */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Priority Badge */}
            {task.priority && (
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getPriorityColor(
                  task.priority
                )}`}
              >
                {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
              </span>
            )}

            {/* Due Date */}
            {task.due_date && (
              <span
                className={`inline-flex items-center gap-1 text-xs ${
                  isOverdue(task.due_date)
                    ? 'text-red-600 font-medium'
                    : 'text-gray-500'
                }`}
              >
                <svg
                  className="w-3.5 h-3.5"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {formatDate(task.due_date)}
                {isOverdue(task.due_date) && ' (Overdue)'}
              </span>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <p className="mt-2 text-sm text-red-600">{error}</p>
          )}
        </div>
      </div>
    </Card>
  );
}
