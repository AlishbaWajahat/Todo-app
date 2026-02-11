# Quickstart Guide: Frontend UI & Profile Integration

**Feature**: 003-frontend-todo-ui
**Date**: 2026-02-06
**Purpose**: Step-by-step guide to set up and run the frontend application

---

## Prerequisites

Before starting, ensure you have:

- **Node.js 18+** installed ([Download](https://nodejs.org/))
- **npm** or **yarn** package manager
- **Backend API running** (Feature 002) at `http://localhost:8000`
- **Git** for version control
- **Code editor** (VS Code recommended)

---

## Initial Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

This will install:
- Next.js 16.0.1
- React 19.2.0
- Tailwind CSS 4
- TypeScript 5
- Better Auth (to be added)
- React Icons 5.5.0

### 3. Configure Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
# Copy example file
cp .env.example .env.local
```

Edit `.env.local` with your configuration:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key-here-min-32-chars
BETTER_AUTH_URL=http://localhost:3000

# JWT Configuration (must match backend)
JWT_SECRET=your-jwt-secret-here-min-32-chars
JWT_ALGORITHM=HS256

# Database URL (if Better Auth uses database)
DATABASE_URL=postgresql://user:password@host:port/database

# Environment
NODE_ENV=development
```

**Important**:
- `JWT_SECRET` must match the backend's `JWT_SECRET`
- `BETTER_AUTH_SECRET` should be a strong random string
- Never commit `.env.local` to version control

### 4. Generate Secure Secrets

Generate cryptographically secure secrets:

```bash
# Generate JWT_SECRET
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Generate BETTER_AUTH_SECRET
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

Copy the generated values to your `.env.local` file.

---

## Development

### Start Development Server

```bash
npm run dev
```

The application will start at **http://localhost:3000**

You should see:
```
▲ Next.js 16.0.1
- Local:        http://localhost:3000
- Ready in 2.3s
```

### Verify Backend Connection

1. Open http://localhost:3000
2. Check browser console for any API connection errors
3. Verify backend is running at http://localhost:8000
4. Test backend health: http://localhost:8000/health

---

## First-Time Setup Flow

### 1. Sign Up

1. Navigate to http://localhost:3000/signup
2. Enter email, password, and name
3. Click "Sign Up"
4. You should be automatically signed in and redirected to dashboard

### 2. Sign In

1. Navigate to http://localhost:3000/signin
2. Enter your email and password
3. Click "Sign In"
4. You should be redirected to http://localhost:3000/dashboard

### 3. Create Your First Task

1. On the dashboard, click "Add Task" or "New Task"
2. Enter task details:
   - Title: "My first task"
   - Description: "Testing the Todo app"
   - Priority: "High"
   - Due Date: Select a date
3. Click "Create Task"
4. Task should appear in your task list

### 4. Update Your Profile

1. Click on your avatar or "Profile" in the navigation
2. Update your name
3. Upload a profile picture (optional)
4. Click "Save"
5. Changes should persist after page refresh

---

## Testing Flows

### Authentication Flow

**Test Sign Up**:
```bash
# 1. Go to /signup
# 2. Enter: email=test@example.com, password=password123, name=Test User
# 3. Verify: Redirected to /dashboard with JWT token stored
# 4. Verify: User appears in backend database
```

**Test Sign In**:
```bash
# 1. Go to /signin
# 2. Enter: email=test@example.com, password=password123
# 3. Verify: Redirected to /dashboard
# 4. Verify: JWT token stored in cookies
```

**Test Session Persistence**:
```bash
# 1. Sign in
# 2. Refresh page (F5)
# 3. Verify: Still authenticated, no redirect to signin
# 4. Close browser and reopen
# 5. Verify: Still authenticated (if within token expiration)
```

**Test Logout**:
```bash
# 1. Click "Logout" button
# 2. Verify: Redirected to /signin
# 3. Verify: JWT token cleared
# 4. Try to access /dashboard
# 5. Verify: Redirected to /signin
```

### Task Management Flow

**Test Create Task**:
```bash
# 1. Go to /dashboard
# 2. Click "Add Task"
# 3. Fill form: title, description, priority, due_date
# 4. Click "Create"
# 5. Verify: Task appears in list
# 6. Verify: Task persists after page refresh
```

**Test Update Task**:
```bash
# 1. Click "Edit" on a task
# 2. Change title or other fields
# 3. Click "Save"
# 4. Verify: Changes reflected in list
# 5. Verify: Changes persist after refresh
```

**Test Complete Task**:
```bash
# 1. Click checkbox on a task
# 2. Verify: Task marked as completed (visual change)
# 3. Verify: Change persists after refresh
# 4. Click checkbox again
# 5. Verify: Task marked as incomplete
```

**Test Delete Task**:
```bash
# 1. Click "Delete" on a task
# 2. Confirm deletion in modal
# 3. Verify: Task removed from list
# 4. Verify: Task not in list after refresh
```

### Profile Management Flow

**Test View Profile**:
```bash
# 1. Click "Profile" in navigation
# 2. Verify: User info displayed (name, email, avatar)
# 3. Verify: Email is not editable
```

**Test Update Name**:
```bash
# 1. On profile page, change name
# 2. Click "Save"
# 3. Verify: Name updated in header
# 4. Verify: Change persists after logout/login
```

**Test Upload Avatar**:
```bash
# 1. Click on avatar placeholder
# 2. Select image file (JPEG/PNG, < 5MB)
# 3. Verify: Preview shows new image
# 4. Click "Save"
# 5. Verify: Avatar updated in header
# 6. Verify: Avatar persists after refresh
```

### Responsive Design Testing

**Test Mobile View**:
```bash
# 1. Open Chrome DevTools (F12)
# 2. Toggle device toolbar (Ctrl+Shift+M)
# 3. Select "iPhone 12 Pro" or similar
# 4. Verify: Layout adapts to mobile screen
# 5. Test all features work on mobile
```

**Test Tablet View**:
```bash
# 1. In DevTools, select "iPad" or similar
# 2. Test portrait and landscape orientations
# 3. Verify: Layout adapts appropriately
```

**Test Desktop View**:
```bash
# 1. Test on 1920x1080 resolution
# 2. Test on 1366x768 resolution
# 3. Verify: Layout looks good on both
```

---

## Troubleshooting

### Backend Connection Issues

**Problem**: "Failed to fetch" or "Network error"

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS is configured in backend
4. Check browser console for detailed errors

### Authentication Issues

**Problem**: "Authentication required" or constant redirects to signin

**Solutions**:
1. Clear browser cookies and localStorage
2. Verify `JWT_SECRET` matches between frontend and backend
3. Check JWT token expiration time
4. Verify Better Auth is configured correctly
5. Check browser console for JWT validation errors

### Build Errors

**Problem**: TypeScript errors or build failures

**Solutions**:
1. Delete `.next` folder: `rm -rf .next`
2. Delete `node_modules`: `rm -rf node_modules`
3. Reinstall dependencies: `npm install`
4. Clear npm cache: `npm cache clean --force`
5. Restart dev server: `npm run dev`

### Port Already in Use

**Problem**: "Port 3000 is already in use"

**Solutions**:
1. Kill process using port 3000:
   ```bash
   # Windows
   netstat -ano | findstr :3000
   taskkill /PID <PID> /F

   # Mac/Linux
   lsof -ti:3000 | xargs kill -9
   ```
2. Or use a different port:
   ```bash
   PORT=3001 npm run dev
   ```

### Environment Variables Not Loading

**Problem**: Environment variables are undefined

**Solutions**:
1. Verify `.env.local` exists in `frontend/` directory
2. Restart dev server after changing `.env.local`
3. Ensure variables start with `NEXT_PUBLIC_` for client-side access
4. Check for typos in variable names

---

## Development Commands

### Start Development Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
```

### Start Production Server
```bash
npm run start
```

### Run Linter
```bash
npm run lint
```

### Type Check
```bash
npx tsc --noEmit
```

### Format Code (if Prettier configured)
```bash
npx prettier --write .
```

---

## Project Structure Overview

```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Public auth pages
│   ├── (protected)/       # Protected pages
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── auth/             # Auth components
│   ├── tasks/            # Task components
│   ├── profile/          # Profile components
│   └── ui/               # Reusable UI components
├── lib/                   # Utilities and helpers
│   ├── api/              # API client
│   ├── auth/             # Auth utilities
│   ├── types/            # TypeScript types
│   └── utils/            # Helper functions
├── public/               # Static assets
├── .env.local            # Environment variables (not in git)
├── .env.example          # Environment template
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── tailwind.config.ts    # Tailwind config
└── next.config.ts        # Next.js config
```

---

## Next Steps

After completing the quickstart:

1. **Explore the Codebase**: Familiarize yourself with the project structure
2. **Read the Documentation**: Review `plan.md`, `research.md`, and `data-model.md`
3. **Test All Features**: Follow the testing flows above
4. **Customize the Theme**: Modify Tailwind config to adjust colors
5. **Add New Features**: Follow the spec-driven development process

---

## Useful Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Better Auth Documentation](https://better-auth.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)

---

## Getting Help

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review the **Backend API Documentation** (Feature 002)
3. Check browser console for error messages
4. Verify environment variables are set correctly
5. Ensure backend is running and accessible

---

**Ready to Start**: You're now ready to develop the frontend Todo application! 🚀
