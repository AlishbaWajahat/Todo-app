/**
 * Task type definition
 * Represents a todo item belonging to a user
 */
export interface Task {
  id: number;                    // Unique task identifier
  user_id: string;               // Owner's user ID (foreign key to User.id)
  title: string;                 // Task title (required)
  description: string | null;    // Task description (optional)
  completed: boolean;            // Completion status
  priority: 'low' | 'medium' | 'high' | null;  // Priority level (optional)
  due_date: string | null;       // ISO 8601 date string (optional)
  created_at: string;            // ISO 8601 timestamp of task creation
  updated_at: string;            // ISO 8601 timestamp of last update
}

/**
 * Task creation data
 * Data required to create a new task
 */
export interface TaskCreateData {
  title: string;                 // Task title (required)
  description?: string;          // Task description (optional)
  priority?: 'low' | 'medium' | 'high';  // Priority level (optional)
  due_date?: string;             // ISO 8601 date string (optional)
}

/**
 * Task update data
 * Data for updating an existing task (all fields optional)
 */
export interface TaskUpdateData {
  title?: string;                // Updated title (optional)
  description?: string;          // Updated description (optional)
  completed?: boolean;           // Updated completion status (optional)
  priority?: 'low' | 'medium' | 'high' | null;  // Updated priority (optional)
  due_date?: string | null;      // Updated due date (optional)
}
