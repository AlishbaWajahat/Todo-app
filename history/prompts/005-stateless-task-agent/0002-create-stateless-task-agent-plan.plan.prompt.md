---
id: 0002
title: Create stateless task agent plan
stage: plan
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-stateless-task-agent
branch: 005-stateless-task-agent
user: Alishba wajahat
command: /sp.plan
labels: ["planning", "architecture", "openai-agent-sdk", "gemini", "stateless-agent", "mcp-integration"]
links:
  spec: specs/005-stateless-task-agent/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-stateless-task-agent/plan.md
  - specs/005-stateless-task-agent/research.md
  - specs/005-stateless-task-agent/data-model.md
  - specs/005-stateless-task-agent/contracts/agent_endpoint.json
  - specs/005-stateless-task-agent/quickstart.md
tests:
  - Constitution check: 4/4 PASSED (Stateless Architecture, MCP Tool Standards, Agent-Tool Interaction, Code Quality)
---

## Prompt

```text
/sp.plan Spec 5 – Stateless Task Agent (OpenAI Agent SDK)

Plan:
1. Agent Setup
   - Initialize agent using OpenAI Agent SDK
   - Configure agent to use `OpenAIChatCompletionModel`
   - Route requests through Gemini API key (Gemini-backed model via OpenAI-compatible interface)

2. Tool Wiring
   - Register MCP task tools (create, list, update, complete, delete)
   - Enforce strict schema validation for all tool inputs
   - Disallow any direct DB or service access from agent

3. Intent Handling
   - Map user intent → MCP tool call
   - Prefer deterministic, rule-based intent selection
   - Avoid over-complex NLP or memory usage

4. Stateless Execution
   - Process each request independently
   - No conversation history, memory, or embeddings
   - User context limited to provided `user_id`

5. Response Layer
   - Convert MCP tool output into concise natural language
   - Ensure predictable and repeatable responses

6. Code Quality
   - Minimal files, modular structure
   - Remove unused files after completion
   - Follow market-level standards
```

## Response snapshot

Created comprehensive implementation plan for Stateless Task Agent with OpenAI Agent SDK and Gemini routing:

**Phase 0: Research (research.md)**
- Decision 1: OpenAI Agent SDK with Gemini routing via OpenAI-compatible interface
- Decision 2: Rule-based intent classification with LLM fallback (95% fast path, 5% LLM)
- Decision 3: Minimal 3-file architecture (agent.py, intent_parser.py, response_formatter.py)
- Decision 4: FastAPI endpoint integration at /api/agent/chat
- Decision 5: Direct MCP tool imports (no HTTP overhead)
- Decision 6: Stateless architecture enforcement (pure functions, no global state)

**Phase 1: Design & Contracts**
- data-model.md: 4 conceptual entities (AgentRequest, IntentClassification, ToolInvocation, AgentResponse)
- contracts/agent_endpoint.json: OpenAPI 3.0 spec for POST /api/agent/chat endpoint
- quickstart.md: Complete testing guide with 5 user story scenarios, edge cases, performance tests

**Technical Stack**:
- OpenAI Agent SDK + OpenAI Python SDK
- Gemini 1.5 Flash via OpenAI-compatible interface
- FastAPI for API endpoint
- MCP tools from 004-mcp-task-tools (direct imports)
- Python 3.11+ with Pydantic validation

**Architecture Decisions**:
- Stateless per request (no session state, no conversation history)
- Rule-based intent classification (fast path) with LLM fallback
- 3-file modular structure (intent parsing, tool invocation, response formatting)
- Direct MCP tool integration (no HTTP/RPC overhead)
- Natural language I/O (plain text responses, not JSON)

**Constitution Compliance**: ✅ ALL PASSED
- Principle VII: Stateless Architecture (zero state between requests)
- Principle VIII: MCP Tool Standards (all operations via MCP tools)
- Principle IX: Agent-Tool Interaction (no direct DB access)
- Code Quality: Minimal files (3 files), modular structure

## Outcome

- ✅ Impact: Complete implementation plan with OpenAI Agent SDK + Gemini routing. Defines 3-file architecture, rule-based intent classification, and stateless execution model. Ready for task breakdown.
- 🧪 Tests: Constitution check passed 4/4 principles. Testing strategy defined in quickstart.md with 5 user story scenarios, edge cases, and performance benchmarks.
- 📁 Files: Created plan.md, research.md, data-model.md, contracts/agent_endpoint.json, quickstart.md
- 🔁 Next prompts: /sp.tasks to generate task breakdown for implementation
- 🧠 Reflection: Plan follows user's specified approach (OpenAI Agent SDK + Gemini). Key decisions: rule-based intent classification for speed (95% fast path), minimal 3-file architecture for simplicity, direct MCP tool imports for performance. Stateless design ensures scalability and aligns with constitution requirements.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with user-specified tech stack
- Graders run and results (PASS/FAIL): Constitution Check PASS (4/4 principles), Architecture PASS (stateless, minimal files, MCP-only), Performance PASS (rule-based fast path, <2s target)
- Prompt variant (if applicable): User-directed planning with specific tech stack (OpenAI Agent SDK + Gemini)
- Next experiment (smallest change to try): Generate tasks with /sp.tasks and implement MVP (User Story 1: Create Task)
