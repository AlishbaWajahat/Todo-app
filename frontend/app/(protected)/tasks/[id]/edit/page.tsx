'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Task } from '@/lib/types';
import { TaskForm } from '@/components/tasks/TaskForm';
import { getTask } from '@/lib/api/tasks';
import { ApiError } from '@/lib/api/errors';
import { LoadingPage } from '@/components/ui/LoadingSpinner';
import { Button } from '@/components/ui/Button';

/**
 * Edit Task Page
 * Page for editing an existing task
 */
export default function EditTaskPage() {
  const params = useParams();
  const router = useRouter();
  const taskId = parseInt(params.id as string);

  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (isNaN(taskId)) {
      setError('Invalid task ID');
      setLoading(false);
      return;
    }

    fetchTask();
  }, [taskId]);

  const fetchTask = async () => {
    setLoading(true);
    setError('');

    try {
      const fetchedTask = await getTask(taskId);
      setTask(fetchedTask);
    } catch (err) {
      if (ApiError.isApiError(err)) {
        setError(err.getUserMessage());
      } else {
        setError('Failed to load task. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingPage message="Loading task..." />;
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <div className="mb-4">
            <svg
              className="w-16 h-16 text-red-500 mx-auto"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Error Loading Task
          </h2>

          <p className="text-gray-600 mb-6">{error}</p>

          <div className="flex gap-3 justify-center">
            <Button onClick={fetchTask} variant="primary">
              Try Again
            </Button>
            <Button onClick={() => router.push('/dashboard')} variant="secondary">
              Back to Dashboard
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Task Not Found
          </h2>
          <p className="text-gray-600 mb-6">
            The task you are looking for does not exist or you do not have access to it.
          </p>
          <Button onClick={() => router.push('/dashboard')} variant="primary">
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <TaskForm task={task} mode="edit" />
    </div>
  );
}
