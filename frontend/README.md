# Todo App - Frontend

A modern, multi-user todo application built with Next.js 16, React 19, TypeScript, and Tailwind CSS 4.

## Features

- **Authentication**: Secure JWT-based authentication with Better Auth
- **Task Management**: Create, read, update, delete tasks with priorities and due dates
- **Profile Management**: Update user profile and avatar
- **Responsive Design**: Mobile-first design that works on all devices
- **Accessibility**: WCAG 2.1 Level AA compliant
- **Real-time Updates**: Optimistic UI updates for instant feedback

## Tech Stack

- **Framework**: Next.js 16.0.1 (App Router)
- **UI Library**: React 19.2.0
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS 4
- **Authentication**: Better Auth (JWT)
- **Icons**: React Icons 5.5.0

## Prerequisites

- Node.js 18+ installed
- Backend API running (see backend README)
- npm or yarn package manager

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd "Todo-app Phase-II/frontend"
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env.local
   ```

4. **Edit `.env.local`** with your configuration:
   ```env
   # Backend API URL
   NEXT_PUBLIC_API_URL=http://localhost:8000

   # Better Auth Configuration
   BETTER_AUTH_SECRET=your-secret-key-here-change-in-production
   BETTER_AUTH_URL=http://localhost:3000

   # JWT Configuration (must match backend)
   JWT_SECRET=your-jwt-secret-here-must-match-backend
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION=86400
   ```

## Development

1. **Start the development server**:
   ```bash
   npm run dev
   ```

2. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

3. **Sign up for an account**:
   - Click "Sign up" on the landing page
   - Enter your email, password, and optional name
   - You'll be redirected to the dashboard

## Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Authentication pages
│   │   ├── signin/page.tsx
│   │   └── signup/page.tsx
│   ├── (protected)/              # Protected pages (require auth)
│   │   ├── dashboard/page.tsx
│   │   ├── profile/page.tsx
│   │   └── tasks/
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Home page (redirects)
│   ├── error.tsx                 # Global error boundary
│   └── not-found.tsx             # 404 page
├── components/                   # React components
│   ├── auth/                     # Authentication components
│   ├── tasks/                    # Task management components
│   ├── profile/                  # Profile components
│   ├── ui/                       # Reusable UI components
│   └── layout/                   # Layout components
├── lib/                          # Utilities and helpers
│   ├── api/                      # API client functions
│   ├── auth/                     # Authentication utilities
│   ├── hooks/                    # Custom React hooks
│   └── types/                    # TypeScript type definitions
├── public/                       # Static assets
├── middleware.ts                 # Next.js middleware (route protection)
├── tailwind.config.ts            # Tailwind CSS configuration
└── next.config.ts                # Next.js configuration
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Features Guide

### Authentication

1. **Sign Up**:
   - Navigate to `/signup`
   - Enter email, password, and optional name
   - Submit to create account

2. **Sign In**:
   - Navigate to `/signin`
   - Enter email and password
   - Submit to authenticate

3. **Sign Out**:
   - Click user avatar in header
   - Select "Sign Out" from dropdown

### Task Management

1. **Create Task**:
   - Click "New Task" button on dashboard
   - Fill in title (required), description, priority, and due date
   - Click "Create Task"

2. **View Tasks**:
   - Dashboard shows all your tasks
   - Filter by: All, Active, Completed
   - Sort by: Date Created, Last Updated, Due Date, Priority

3. **Complete Task**:
   - Click checkbox next to task title
   - Task is marked complete with visual feedback

4. **Edit Task**:
   - Click edit icon on task card
   - Update task details
   - Click "Save Changes"

5. **Delete Task**:
   - Click delete icon on task card
   - Confirm deletion in modal

### Profile Management

1. **View Profile**:
   - Click "Profile" in navigation
   - View your name, email, and avatar

2. **Update Name**:
   - Edit name field
   - Click "Save Changes"

3. **Upload Avatar**:
   - Click avatar or drag and drop image
   - Preview shown before saving
   - Click "Save Changes" to upload

## Responsive Design

The application is fully responsive and works on:
- **Mobile**: 320px and up
- **Tablet**: 768px and up
- **Desktop**: 1024px and up

## Accessibility

- Keyboard navigation supported (Tab, Enter, Escape)
- Screen reader compatible
- ARIA labels on all interactive elements
- Skip-to-content link for keyboard users
- WCAG 2.1 Level AA color contrast

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Cannot connect to backend API

**Problem**: API requests fail with network errors

**Solution**:
1. Ensure backend server is running on `http://localhost:8000`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS is enabled on backend

### Authentication not persisting

**Problem**: User is logged out after page refresh

**Solution**:
1. Check browser localStorage for `auth_token`
2. Verify JWT token is not expired
3. Ensure `JWT_SECRET` matches backend configuration

### Images not loading

**Problem**: Avatar images show broken image icon

**Solution**:
1. Check image URL in user profile
2. Verify backend serves images correctly
3. Check Next.js image configuration in `next.config.ts`

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is part of a hackathon submission.

## Support

For issues or questions, please open an issue in the repository.
