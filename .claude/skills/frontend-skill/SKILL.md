---
name: frontend-page-building
description: Build responsive Next.js pages with App Router, server/client components, Tailwind CSS styling, and TypeScript.
---

# Next.js App Router Frontend with Tailwind CSS

**Tech Stack:** Next.js 16+ (App Router) + Tailwind CSS + TypeScript

## Instructions

1. **App Router Structure**
   - Use file-based routing in `app/` directory
   - Create `page.tsx` for routes
   - Use `layout.tsx` for shared layouts
   - Implement `loading.tsx` for loading states
   - Create `error.tsx` for error boundaries
   - Use route groups with `(folder)` for organization

2. **Server vs Client Components**
   - Use Server Components by default (no 'use client')
   - Add 'use client' only when needed:
     - Event handlers (onClick, onChange)
     - State (useState, useReducer)
     - Effects (useEffect)
     - Browser APIs (localStorage, window)
   - Fetch data in Server Components
   - Pass data from Server to Client Components as props

3. **Tailwind CSS Styling**
   - Use utility-first approach with Tailwind classes
   - Design mobile-first with responsive breakpoints (sm:, md:, lg:, xl:)
   - Use Tailwind's color palette and spacing scale
   - Create custom components with consistent styling
   - Use Tailwind's dark mode utilities if needed
   - Avoid inline styles; prefer Tailwind utilities

4. **Components & Layouts**
   - Build reusable UI components
   - Use semantic HTML5 elements
   - Implement responsive grid/flex layouts
   - Create consistent spacing and typography
   - Use Next.js Image component for optimized images
   - Implement proper accessibility (ARIA labels, semantic HTML)

5. **Data Fetching & API Integration**
   - Fetch data in Server Components with async/await
   - Use fetch with proper caching strategies
   - Call backend APIs with proper error handling
   - Include JWT tokens in Authorization headers
   - Handle loading and error states
   - Use React Suspense for streaming

6. **Forms & User Input**
   - Use Server Actions for form submissions (recommended)
   - Implement client-side validation
   - Show loading states during submission
   - Display error messages clearly
   - Use controlled components for complex forms

## Best Practices
- Use Server Components by default
- Design mobile-first with Tailwind
- Use TypeScript for type safety
- Implement proper error boundaries
- Optimize images with Next.js Image
- Use semantic and accessible HTML
- Keep components small and focused
- Handle loading and error states
- Use environment variables for API URLs

## Example Structure

```tsx
// app/page.tsx (Server Component - Home Page)
import { TodoList } from '@/components/TodoList'

async function getTodos() {
  const res = await fetch('http://localhost:8000/api/v1/todos', {
    cache: 'no-store' // or 'force-cache' for static
  })
  if (!res.ok) throw new Error('Failed to fetch todos')
  return res.json()
}

export default async function HomePage() {
  const todos = await getTodos()

  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          My Todos
        </h1>
        <TodoList todos={todos} />
      </div>
    </main>
  )
}

// app/layout.tsx (Root Layout)
import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Todo App',
  description: 'Full-stack todo application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="bg-white shadow-sm border-b">
          <div className="container mx-auto px-4 py-4">
            <h1 className="text-xl font-semibold">Todo App</h1>
          </div>
        </nav>
        {children}
      </body>
    </html>
  )
}

// app/loading.tsx (Loading UI)
export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
    </div>
  )
}

// components/TodoList.tsx (Client Component)
'use client'

import { useState } from 'react'

interface Todo {
  id: number
  title: string
  completed: boolean
}

export function TodoList({ todos }: { todos: Todo[] }) {
  const [items, setItems] = useState(todos)

  const toggleTodo = async (id: number) => {
    // API call to toggle todo
    const response = await fetch(`/api/todos/${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` // JWT token
      },
      body: JSON.stringify({ completed: !items.find(t => t.id === id)?.completed })
    })

    if (response.ok) {
      setItems(items.map(item =>
        item.id === id ? { ...item, completed: !item.completed } : item
      ))
    }
  }

  return (
    <div className="space-y-2">
      {items.map((todo) => (
        <div
          key={todo.id}
          className="flex items-center gap-3 p-4 bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow"
        >
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={() => toggleTodo(todo.id)}
            className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
          />
          <span className={`flex-1 ${todo.completed ? 'line-through text-gray-400' : 'text-gray-900'}`}>
            {todo.title}
          </span>
        </div>
      ))}
    </div>
  )
}

// components/AddTodoForm.tsx (Server Action)
'use client'

import { useFormStatus } from 'react-dom'

function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <button
      type="submit"
      disabled={pending}
      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      {pending ? 'Adding...' : 'Add Todo'}
    </button>
  )
}

export function AddTodoForm() {
  async function addTodo(formData: FormData) {
    'use server'

    const title = formData.get('title')
    // Call API to add todo
  }

  return (
    <form action={addTodo} className="flex gap-2 mb-6">
      <input
        type="text"
        name="title"
        placeholder="What needs to be done?"
        required
        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <SubmitButton />
    </form>
  )
}
```

## Tailwind Configuration

```js
// tailwind.config.js
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Custom colors if needed
      },
    },
  },
  plugins: [],
}
```

## Responsive Design Patterns

```tsx
// Mobile-first responsive design
<div className="
  grid
  grid-cols-1        // 1 column on mobile
  sm:grid-cols-2     // 2 columns on small screens
  md:grid-cols-3     // 3 columns on medium screens
  lg:grid-cols-4     // 4 columns on large screens
  gap-4
">
  {/* Grid items */}
</div>

// Responsive text sizes
<h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold">
  Responsive Heading
</h1>

// Responsive padding
<div className="p-4 sm:p-6 md:p-8 lg:p-12">
  Content
</div>
```
