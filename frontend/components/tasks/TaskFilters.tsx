'use client';

import { TaskFilter, TaskSort } from '@/lib/types';

export interface TaskFiltersProps {
  currentFilter: TaskFilter;
  currentSort: TaskSort;
  onFilterChange: (filter: TaskFilter) => void;
  onSortChange: (sort: TaskSort) => void;
  taskCounts: {
    all: number;
    active: number;
    completed: number;
  };
}

/**
 * TaskFilters Component
 * Provides filtering and sorting controls for the task list
 */
export function TaskFilters({
  currentFilter,
  currentSort,
  onFilterChange,
  onSortChange,
  taskCounts,
}: TaskFiltersProps) {
  const filters: { value: TaskFilter; label: string }[] = [
    { value: 'all', label: `All (${taskCounts.all})` },
    { value: 'active', label: `Active (${taskCounts.active})` },
    { value: 'completed', label: `Completed (${taskCounts.completed})` },
  ];

  const sortOptions: { value: TaskSort; label: string }[] = [
    { value: 'created', label: 'Date Created' },
    { value: 'updated', label: 'Last Updated' },
    { value: 'due_date', label: 'Due Date' },
    { value: 'priority', label: 'Priority' },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6">
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        {/* Filter Tabs */}
        <div className="flex gap-2 flex-wrap">
          {filters.map((filter) => (
            <button
              key={filter.value}
              onClick={() => onFilterChange(filter.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                currentFilter === filter.value
                  ? 'bg-primary text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>

        {/* Sort Dropdown */}
        <div className="flex items-center gap-2">
          <label htmlFor="sort" className="text-sm font-medium text-gray-700 whitespace-nowrap">
            Sort by:
          </label>
          <select
            id="sort"
            value={currentSort}
            onChange={(e) => onSortChange(e.target.value as TaskSort)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
