'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Task, TaskCreateData, TaskUpdateData } from '@/lib/types';
import { Input } from '@/components/ui/Input';
import { Buttonnn } from '@/components/ui/Buttonnn';
import { createTask, updateTask } from '@/lib/api/tasks';
import { ApiError } from '@/lib/api/errors';

export interface TaskFormProps {
  task?: Task;
  mode: 'create' | 'edit';
}

/**
 * TaskForm Component
 * Form for creating or editing tasks
 */
export function TaskForm({ task, mode }: TaskFormProps) {
  const router = useRouter();
  const [formData, setFormData] = useState({
    title: task?.title || '',
    description: task?.description || '',
    priority: task?.priority || '',
    due_date: task?.due_date ? task.due_date.split('T')[0] : '',
  });
  const [error, setError] = useState<string>('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setFieldErrors({});
    setLoading(true);

    try {
      const data: TaskCreateData | TaskUpdateData = {
        title: formData.title,
        description: formData.description || undefined,
        priority: formData.priority ? (formData.priority as 'low' | 'medium' | 'high') : undefined,
        due_date: formData.due_date || undefined,
      };

      if (mode === 'create') {
        await createTask(data as TaskCreateData);
      } else if (task) {
        await updateTask(task.id, data as TaskUpdateData);
      }

      // Redirect to dashboard on success
      router.push('/dashboard');
    } catch (err) {
      if (ApiError.isApiError(err)) {
        if (err.field) {
          setFieldErrors({ [err.field]: err.getUserMessage() });
        } else {
          setError(err.getUserMessage());
        }
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear errors when user starts typing
    if (error) setError('');
    if (fieldErrors[name]) {
      setFieldErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleCancel = () => {
    router.push('/dashboard');
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        {mode === 'create' ? 'Create New Task' : 'Edit Task'}
      </h2>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          type="text"
          name="title"
          label="Title"
          value={formData.title}
          onChange={handleChange}
          placeholder="Enter task title"
          required
          minLength={3}
          maxLength={200}
          disabled={loading}
          error={fieldErrors.title}
          helperText="3-200 characters"
        />

        <div className="w-full">
          <label
            htmlFor="description"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Enter task description (optional)"
            rows={4}
            maxLength={1000}
            disabled={loading}
            className={`
              w-full px-3 py-2 border rounded-lg
              focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
              disabled:bg-gray-100 disabled:cursor-not-allowed
              ${fieldErrors.description ? 'border-red-500' : 'border-gray-300'}
            `}
          />
          {fieldErrors.description && (
            <p className="mt-1 text-sm text-red-600">{fieldErrors.description}</p>
          )}
          <p className="mt-1 text-sm text-gray-500">
            Optional, up to 1000 characters
          </p>
        </div>

        <div className="w-full">
          <label
            htmlFor="priority"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Priority
          </label>
          <select
            id="priority"
            name="priority"
            value={formData.priority}
            onChange={handleChange}
            disabled={loading}
            className={`
              w-full px-3 py-2 border rounded-lg
              focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
              disabled:bg-gray-100 disabled:cursor-not-allowed
              ${fieldErrors.priority ? 'border-red-500' : 'border-gray-300'}
            `}
          >
            <option value="">None</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          {fieldErrors.priority && (
            <p className="mt-1 text-sm text-red-600">{fieldErrors.priority}</p>
          )}
        </div>

        <Input
          type="date"
          name="due_date"
          label="Due Date"
          value={formData.due_date}
          onChange={handleChange}
          disabled={loading}
          error={fieldErrors.due_date}
          helperText="Optional"
        />

        <div className="flex gap-3 pt-4">
          <Buttonnn
            type="submit"
            variant="primary"
            loading={loading}
            disabled={loading}
            className="flex-1"
          >
            {loading
              ? mode === 'create'
                ? 'Creating...'
                : 'Saving...'
              : mode === 'create'
              ? 'Create Task'
              : 'Save Changes'}
          </Buttonnn>

          <Buttonnn
            type="button"
            variant="secondary"
            onClick={handleCancel}
            disabled={loading}
            className="flex-1"
          >
            Cancel
          </Buttonnn>
        </div>
      </form>
    </div>
  );
}
