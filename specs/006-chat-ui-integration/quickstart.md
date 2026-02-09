# Quickstart Guide: Chat UI & End-to-End Integration

**Feature**: 006-chat-ui-integration
**Date**: 2026-02-09
**Purpose**: Integration scenarios and testing guide
**Approach**: OpenAI ChatKit Integration

## Overview

This guide provides step-by-step integration scenarios for testing the chat UI end-to-end. Each scenario demonstrates a complete user flow from frontend to backend.

**Implementation Note**: This feature uses **OpenAI ChatKit** (`@openai/chatkit-react`) for the chat interface. ChatKit handles message rendering, state management, auto-scroll, loading states, and error display automatically. We only implement JWT authentication and theme styling.

## Prerequisites

Before testing, ensure:
- ✅ Backend server running on `http://localhost:8000`
- ✅ Frontend server running on `http://localhost:3000`
- ✅ User is logged in with valid JWT token
- ✅ Agent endpoint responding at POST `/api/v1/agent/chat`
- ✅ Database contains test user account

## Scenario 1: Happy Path - Basic Chat Interaction

**Objective**: Verify basic message sending and receiving works end-to-end.

**Steps**:
1. Navigate to `http://localhost:3000/chat`
2. Verify chat interface loads (empty message list, input field, send button)
3. Type "Hello" in the input field
4. Press Enter or click Send button
5. Verify user message appears immediately with "sending" status
6. Wait for agent response (should appear within 2 seconds)
7. Verify agent message appears with helpful guidance

**Expected Results**:
- User message: "Hello"
- User message status changes: sending → sent
- Agent response: "I can only help with task management. Try 'create a task' or 'show my tasks'."
- No errors displayed
- Input field cleared after sending

**API Calls**:
```
POST /api/v1/agent/chat
Headers: Authorization: Bearer {jwt_token}
Body: { "user_id": "user-123", "message": "Hello" }

Response 200:
{
  "response": "I can only help with task management. Try 'create a task' or 'show my tasks'.",
  "metadata": {
    "intent": "UNKNOWN",
    "tool_called": null,
    "confidence": 0.45,
    "execution_time_ms": 12
  }
}
```

---

## Scenario 2: Create Task via Chat

**Objective**: Verify task creation works through natural language.

**Steps**:
1. Navigate to `http://localhost:3000/chat`
2. Type "Create a task to buy milk" in the input field
3. Press Enter
4. Wait for agent response
5. Navigate to dashboard to verify task was created
6. Return to chat and type "Show my tasks"
7. Verify the new task appears in the list

**Expected Results**:
- User message: "Create a task to buy milk"
- Agent response: "Task created: buy milk"
- Task appears in dashboard with title "buy milk"
- "Show my tasks" includes the new task

**API Calls**:
```
POST /api/v1/agent/chat
Body: { "user_id": "user-123", "message": "Create a task to buy milk" }

Response 200:
{
  "response": "Task created: buy milk",
  "metadata": {
    "intent": "CREATE",
    "tool_called": "add_task",
    "confidence": 0.95,
    "execution_time_ms": 234
  }
}
```

**Backend Flow**:
```
Frontend → Agent Endpoint → Intent Parser (CREATE)
         → MCP add_task tool → Backend Task API
         → Database INSERT → Response
```

---

## Scenario 3: List Tasks via Chat

**Objective**: Verify task listing works through natural language.

**Prerequisites**: Create 3 test tasks via dashboard or API.

**Steps**:
1. Navigate to `http://localhost:3000/chat`
2. Type "Show my tasks" in the input field
3. Press Enter
4. Wait for agent response
5. Verify all tasks are listed with correct titles

**Expected Results**:
- User message: "Show my tasks"
- Agent response: "You have 3 tasks: 1) Buy milk 2) Call dentist 3) Finish report"
- All task titles match database records
- Completed tasks show ✓ indicator

**API Calls**:
```
POST /api/v1/agent/chat
Body: { "user_id": "user-123", "message": "Show my tasks" }

Response 200:
{
  "response": "You have 3 tasks: 1) ✓Buy milk 2) Call dentist 3) Finish report",
  "metadata": {
    "intent": "LIST",
    "tool_called": "list_tasks",
    "confidence": 0.98,
    "execution_time_ms": 156
  }
}
```

**Backend Flow**:
```
Frontend → Agent Endpoint → Intent Parser (LIST)
         → MCP list_tasks tool → Backend Task API
         → Database SELECT WHERE user_id = ? → Response
```

---

## Scenario 4: Complete Task via Chat

**Objective**: Verify task completion works through natural language.

**Prerequisites**: Create a test task with ID 1.

**Steps**:
1. Navigate to `http://localhost:3000/chat`
2. Type "Complete task 1" in the input field
3. Press Enter
4. Wait for agent response
5. Type "Show my tasks" to verify completion
6. Navigate to dashboard to verify task is marked complete

**Expected Results**:
- User message: "Complete task 1"
- Agent response: "Marked 'buy milk' as done"
- Task shows as completed in subsequent "Show my tasks"
- Task is marked complete in dashboard

**API Calls**:
```
POST /api/v1/agent/chat
Body: { "user_id": "user-123", "message": "Complete task 1" }

Response 200:
{
  "response": "Marked 'buy milk' as done",
  "metadata": {
    "intent": "COMPLETE",
    "tool_called": "complete_task",
    "confidence": 0.92,
    "execution_time_ms": 189
  }
}
```

**Backend Flow**:
```
Frontend → Agent Endpoint → Intent Parser (COMPLETE)
         → identify_task (validate task_id belongs to user)
         → MCP complete_task tool → Backend Task API
         → Database UPDATE SET completed = true WHERE id = ? AND user_id = ?
         → Response
```

---

## Scenario 5: Update Task via Chat

**Objective**: Verify task updates work through natural language.

**Prerequisites**: Create a test task with ID 3 titled "Buy milk".

**Steps**:
1. Navigate to `http://localhost:3000/chat`
2. Type "Change task 3 to 'Buy organic milk'" in the input field
3. Press Enter
4. Wait for agent response
5. Type "Show my tasks" to verify update
6. Navigate to dashboard to verify title changed

**Expected Results**:
- User message: "Change task 3 to 'Buy organic milk'"
- Agent response: "Updated 'Buy milk' to 'Buy organic milk'"
- Task title updated in subsequent "Show my tasks"
- Task title updated in dashboard

**API Calls**:
```
POST /api/v1/agent/chat
Body: { "user_id": "user-123", "message": "Change task 3 to 'Buy organic milk'" }

Response 200:
{
  "response": "Updated 'Buy milk' to 'Buy organic milk'",
  "metadata": {
    "intent": "UPDATE",
    "tool_called": "update_task",
    "confidence": 0.89,
    "execution_time_ms": 201
  }
}
```

---

## Scenario 6: Delete Task via Chat

**Objective**: Verify task deletion works through natural language.

**Prerequisites**: Create a test task with ID 5.

**Steps**:
1. Navigate to `http://localhost:3000/chat`
2. Type "Delete task 5" in the input field
3. Press Enter
4. Wait for agent response
5. Type "Show my tasks" to verify deletion
6. Navigate to dashboard to verify task is gone

**Expected Results**:
- User message: "Delete task 5"
- Agent response: "Deleted task 'buy groceries'" (80% success rate)
- Task removed from subsequent "Show my tasks"
- Task removed from dashboard

**Known Limitation**: DELETE operation has 80% success rate due to parameter extraction issues. If deletion fails, try using task ID instead of task title.

**API Calls**:
```
POST /api/v1/agent/chat
Body: { "user_id": "user-123", "message": "Delete task 5" }

Response 200:
{
  "response": "Deleted task 'buy groceries'",
  "metadata": {
    "intent": "DELETE",
    "tool_called": "delete_task",
    "confidence": 0.91,
    "execution_time_ms": 178
  }
}
```

---

## Scenario 7: Network Error Handling

**Objective**: Verify graceful error handling when network fails.

**Steps**:
1. Navigate to `http://localhost:3000/chat`
2. Stop the backend server
3. Type "Show my tasks" in the input field
4. Press Enter
5. Wait for error message
6. Verify error is user-friendly
7. Restart backend server
8. Click "Retry" button (if provided) or send message again
9. Verify request succeeds

**Expected Results**:
- User message appears with "sending" status
- After timeout, status changes to "error"
- Error message displayed: "Connection failed. Please check your internet."
- Retry option available
- After retry, request succeeds

**Error Display**:
```
[User message with error indicator]
❌ Connection failed. Please check your internet.
[Retry button]
```

---

## Scenario 8: Authentication Token Expiry

**Objective**: Verify handling of expired JWT tokens.

**Steps**:
1. Navigate to `http://localhost:3000/chat`
2. Manually expire JWT token (or wait for natural expiry)
3. Type "Show my tasks" in the input field
4. Press Enter
5. Wait for 401 response
6. Verify redirect to login page
7. Log in again
8. Verify redirect back to chat page

**Expected Results**:
- Request returns 401 Unauthorized
- Error message: "Your session has expired. Please log in again."
- User redirected to login page
- After login, user redirected back to chat

**API Calls**:
```
POST /api/v1/agent/chat
Headers: Authorization: Bearer {expired_token}

Response 401:
{
  "detail": "Invalid or expired token",
  "code": "EXPIRED_TOKEN"
}
```

---

## Scenario 9: Validation Error

**Objective**: Verify input validation works correctly.

**Steps**:
1. Navigate to `http://localhost:3000/chat`
2. Type a message longer than 1000 characters
3. Try to send
4. Verify validation error displayed
5. Shorten message to under 1000 characters
6. Send successfully

**Expected Results**:
- Send button disabled when message > 1000 chars
- Error message: "Message must be between 1 and 1000 characters"
- After shortening, send button enabled
- Message sends successfully

---

## Scenario 10: Multiple Messages in Sequence

**Objective**: Verify chat handles multiple messages correctly.

**Steps**:
1. Navigate to `http://localhost:3000/chat`
2. Send "Create a task to buy milk"
3. Wait for response
4. Send "Create a task to call dentist"
5. Wait for response
6. Send "Show my tasks"
7. Wait for response
8. Verify all messages appear in correct order
9. Verify auto-scroll works for each new message

**Expected Results**:
- All 6 messages appear (3 user, 3 agent)
- Messages in chronological order
- Auto-scroll to bottom after each message
- No duplicate messages
- No missing messages

---

## Performance Testing

### Latency Test

**Objective**: Verify p95 latency < 2 seconds.

**Steps**:
1. Send 100 messages to agent endpoint
2. Record response time for each
3. Calculate 95th percentile
4. Verify p95 < 2000ms

**Expected Results**:
- p95 latency < 2000ms
- Average latency < 500ms
- No timeouts (all requests complete within 30s)

### Load Test

**Objective**: Verify chat handles 100+ messages without performance degradation.

**Steps**:
1. Navigate to `http://localhost:3000/chat`
2. Send 100 messages (can use script to automate)
3. Verify all messages render correctly
4. Verify scrolling remains smooth (60fps)
5. Verify no memory leaks (check browser DevTools)

**Expected Results**:
- All 100 messages render correctly
- Scrolling remains smooth
- No browser lag or freezing
- Memory usage stable (no leaks)

---

## Troubleshooting

### Issue: Agent not responding

**Symptoms**: User message sent but no agent response appears.

**Checks**:
1. Verify backend server is running
2. Check browser console for errors
3. Check network tab for 500 errors
4. Verify JWT token is valid
5. Check backend logs for errors

**Solution**: Restart backend server, refresh page, log in again.

---

### Issue: Messages not appearing

**Symptoms**: User sends message but it doesn't appear in chat.

**Checks**:
1. Check browser console for React errors
2. Verify messages array is updating (React DevTools)
3. Check for JavaScript errors

**Solution**: Refresh page, clear browser cache.

---

### Issue: Auto-scroll not working

**Symptoms**: New messages appear but chat doesn't scroll to bottom.

**Checks**:
1. Verify scrollIntoView is being called
2. Check if user has scrolled up (auto-scroll disabled)
3. Check for CSS overflow issues

**Solution**: Scroll to bottom manually, refresh page.

---

### Issue: DELETE operation failing

**Symptoms**: "Delete task X" returns "Task not found" error.

**Known Limitation**: DELETE operation has 80% success rate due to parameter extraction issues.

**Workaround**: Use task ID instead of task title: "Delete task 5" instead of "Delete buy groceries".

---

## Testing Checklist

Use this checklist to verify all scenarios:

- [ ] Scenario 1: Happy Path - Basic Chat Interaction
- [ ] Scenario 2: Create Task via Chat
- [ ] Scenario 3: List Tasks via Chat
- [ ] Scenario 4: Complete Task via Chat
- [ ] Scenario 5: Update Task via Chat
- [ ] Scenario 6: Delete Task via Chat
- [ ] Scenario 7: Network Error Handling
- [ ] Scenario 8: Authentication Token Expiry
- [ ] Scenario 9: Validation Error
- [ ] Scenario 10: Multiple Messages in Sequence
- [ ] Performance: Latency Test (p95 < 2s)
- [ ] Performance: Load Test (100+ messages)
- [ ] Mobile: Test on mobile device (320px width)
- [ ] Tablet: Test on tablet device (768px width)
- [ ] Desktop: Test on desktop (1024px+ width)
- [ ] Theme: Verify colors match existing UI
- [ ] Theme: Verify fonts match existing UI
- [ ] Theme: Verify spacing matches existing UI
- [ ] Accessibility: Keyboard navigation works
- [ ] Accessibility: Screen reader support
- [ ] Security: XSS prevention (test with `<script>alert('xss')</script>`)
- [ ] Security: User isolation (cannot access other users' tasks)

---

## Next Steps

After completing quickstart testing:
1. Document any bugs or issues found
2. Create GitHub issues for bugs
3. Update spec if requirements change
4. Proceed to `/sp.tasks` to generate task breakdown
5. Execute tasks via `/sp.implement` using Frontend Agent
