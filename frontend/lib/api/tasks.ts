import { apiRequest } from './client';
import { Task, TaskCreateData, TaskUpdateData } from '@/lib/types';

/**
 * Get all tasks for the authenticated user
 *
 * @returns Array of tasks
 */
export async function getTasks(): Promise<Task[]> {
  return apiRequest<Task[]>('/api/v1/tasks/', {
    method: 'GET',
  });
}

/**
 * Get a single task by ID
 *
 * @param id - Task ID
 * @returns Task object
 */
export async function getTask(id: number): Promise<Task> {
  return apiRequest<Task>(`/api/v1/tasks/${id}/`, {
    method: 'GET',
  });
}

/**
 * Create a new task
 *
 * @param data - Task creation data
 * @returns Created task
 */
export async function createTask(data: TaskCreateData): Promise<Task> {
  return apiRequest<Task>('/api/v1/tasks/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Update an existing task
 *
 * @param id - Task ID
 * @param data - Task update data
 * @returns Updated task
 */
export async function updateTask(id: number, data: TaskUpdateData): Promise<Task> {
  return apiRequest<Task>(`/api/v1/tasks/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * Delete a task
 *
 * @param id - Task ID
 */
export async function deleteTask(id: number): Promise<void> {
  return apiRequest<void>(`/api/v1/tasks/${id}/`, {
    method: 'DELETE',
  });
}

/**
 * Toggle task completion status
 *
 * @param id - Task ID
 * @returns Updated task
 */
export async function toggleTaskComplete(id: number): Promise<Task> {
  return apiRequest<Task>(`/api/v1/tasks/${id}/complete/`, {
    method: 'PATCH',
  });
}
