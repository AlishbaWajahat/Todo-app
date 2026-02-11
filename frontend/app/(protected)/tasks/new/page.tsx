import { Metadata } from 'next';
import { TaskForm } from '@/components/tasks/TaskForm';

export const metadata: Metadata = {
  title: 'New Task',
  description: 'Create a new task',
};

/**
 * New Task Page
 * Page for creating a new task
 */
export default function NewTaskPage() {
  return (
    <div className="max-w-2xl mx-auto">
      <TaskForm mode="create" />
    </div>
  );
}
