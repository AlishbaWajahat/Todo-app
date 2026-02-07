'use client';

import { useState } from 'react';
import { Modal, ModalFooter } from '@/components/ui/Modal';
import { Buttonnn } from '@/components/ui/Buttonnn';
import { Task } from '@/lib/types';
import { deleteTask } from '@/lib/api/tasks';
import { ApiError } from '@/lib/api/errors';

export interface DeleteConfirmModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onDelete: (taskId: number) => void;
}

/**
 * DeleteConfirmModal Component
 * Confirmation modal for deleting tasks
 */
export function DeleteConfirmModal({
  task,
  isOpen,
  onClose,
  onDelete,
}: DeleteConfirmModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleDelete = async () => {
    if (!task) return;

    setLoading(true);
    setError('');

    try {
      await deleteTask(task.id);
      onDelete(task.id);
      onClose();
    } catch (err) {
      if (ApiError.isApiError(err)) {
        setError(err.getUserMessage());
      } else {
        setError('Failed to delete task. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setError('');
      onClose();
    }
  };

  if (!task) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Delete Task"
      size="sm"
    >
      <div className="space-y-4">
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <p className="text-gray-700">
          Are you sure you want to delete this task?
        </p>

        <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
          <p className="font-medium text-gray-900">{task.title}</p>
          {task.description && (
            <p className="text-sm text-gray-600 mt-1">{task.description}</p>
          )}
        </div>

        <p className="text-sm text-gray-600">
          This action cannot be undone.
        </p>

        <ModalFooter>
          <Buttonnn
            variant="secondary"
            onClick={handleClose}
            disabled={loading}
          >
            Cancel
          </Buttonnn>
          <Buttonnn
            variant="danger"
            onClick={handleDelete}
            loading={loading}
            disabled={loading}
          >
            {loading ? 'Deleting...' : 'Delete Task'}
          </Buttonnn>
        </ModalFooter>
      </div>
    </Modal>
  );
}
