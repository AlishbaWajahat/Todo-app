'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Task, TaskFilter, TaskSort } from '@/lib/types';
import { Buttonnn } from '@/components/ui/Buttonnn';
import { TaskList } from '@/components/tasks/TaskList';
import { TaskFilters } from '@/components/tasks/TaskFilters';
import { DeleteConfirmModal } from '@/components/tasks/DeleteConfirmModal';
import { getTasks } from '@/lib/api/tasks';
import { ApiError } from '@/lib/api/errors';

/**
 * Dashboard Page
 * Main page for task management with filtering and sorting
 */
export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [currentFilter, setCurrentFilter] = useState<TaskFilter>('all');
  const [currentSort, setCurrentSort] = useState<TaskSort>('created');
  const [taskToDelete, setTaskToDelete] = useState<Task | null>(null);

  // Fetch tasks on mount
  useEffect(() => {
    fetchTasks();
  }, []);

  // Apply filtering and sorting when tasks or filters change
  useEffect(() => {
    let filtered = [...tasks];

    // Apply filter
    switch (currentFilter) {
      case 'active':
        filtered = filtered.filter((task) => !task.completed);
        break;
      case 'completed':
        filtered = filtered.filter((task) => task.completed);
        break;
      case 'all':
      default:
        // No filtering
        break;
    }

    // Apply sort
    filtered.sort((a, b) => {
      switch (currentSort) {
        case 'created':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case 'updated':
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
        case 'due_date':
          // Tasks without due dates go to the end
          if (!a.due_date && !b.due_date) return 0;
          if (!a.due_date) return 1;
          if (!b.due_date) return -1;
          return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
        case 'priority':
          const priorityOrder = { high: 3, medium: 2, low: 1, null: 0 };
          const aPriority = priorityOrder[a.priority || 'null'];
          const bPriority = priorityOrder[b.priority || 'null'];
          return bPriority - aPriority;
        default:
          return 0;
      }
    });

    setFilteredTasks(filtered);
  }, [tasks, currentFilter, currentSort]);

  const fetchTasks = async () => {
    setLoading(true);
    setError('');

    try {
      const fetchedTasks = await getTasks();
      setTasks(fetchedTasks);
    } catch (err) {
      if (ApiError.isApiError(err)) {
        setError(err.getUserMessage());
      } else {
        setError('Failed to load tasks. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTaskUpdate = (updatedTask: Task) => {
    setTasks((prevTasks) =>
      prevTasks.map((task) => (task.id === updatedTask.id ? updatedTask : task))
    );
  };

  const handleTaskDelete = (taskId: number) => {
    setTasks((prevTasks) => prevTasks.filter((task) => task.id !== taskId));
    setTaskToDelete(null);
  };

  const handleDeleteClick = (taskId: number) => {
    const task = tasks.find((t) => t.id === taskId);
    if (task) {
      setTaskToDelete(task);
    }
  };

  const taskCounts = {
    all: tasks.length,
    active: tasks.filter((task) => !task.completed).length,
    completed: tasks.filter((task) => task.completed).length,
  };

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">
            Manage your tasks and stay organized
          </p>
        </div>

        <Link href="/tasks/new">
          <Buttonnn variant="primary" size="lg">
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M12 4v16m8-8H4" />
            </svg>
            New Task
          </Buttonnn>
        </Link>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-3">
            <svg
              className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <p className="text-sm text-red-600">{error}</p>
              <Buttonnn
                variant="ghost"
                size="sm"
                onClick={fetchTasks}
                className="mt-2 text-red-600 hover:bg-red-50"
              >
                Try Again
              </Buttonnn>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      {!loading && tasks.length > 0 && (
        <TaskFilters
          currentFilter={currentFilter}
          currentSort={currentSort}
          onFilterChange={setCurrentFilter}
          onSortChange={setCurrentSort}
          taskCounts={taskCounts}
        />
      )}

      {/* Task List */}
      <TaskList
        tasks={filteredTasks}
        onUpdate={handleTaskUpdate}
        onDelete={handleDeleteClick}
        isLoading={loading}
      />

      {/* Delete Confirmation Modal */}
      <DeleteConfirmModal
        task={taskToDelete}
        isOpen={taskToDelete !== null}
        onClose={() => setTaskToDelete(null)}
        onDelete={handleTaskDelete}
      />
    </div>
  );
}
