/**
 * Task filter options
 * Filter options for task list
 */
export type TaskFilter = 'all' | 'active' | 'completed';

/**
 * Task sort options
 * Sort options for task list
 */
export type TaskSort = 'created' | 'updated' | 'due_date' | 'priority';

/**
 * Loading state
 * Loading state for async operations
 */
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

/**
 * Button variant
 * Visual style variants for buttons
 */
export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';

/**
 * Button size
 * Size variants for buttons
 */
export type ButtonSize = 'sm' | 'md' | 'lg';
