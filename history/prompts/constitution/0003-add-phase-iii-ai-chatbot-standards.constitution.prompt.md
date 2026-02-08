---
id: 0003
title: Add Phase III AI Chatbot Standards to Constitution
stage: constitution
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: /sp.constitution
labels: ["constitution", "phase-iii", "ai-chatbot", "mcp", "stateless-architecture", "testable-standards"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

Review and improve .specify/memory/constitution.md for Phase III (AI-powered Todo Chatbot).

Ensure all standards are:
- Testable (no vague rules)
- Enforceable during review
- Suitable for agentic + MCP architecture

Must cover:
- Stateless backend guarantees (no in-memory chat or tool state)
- MCP tool standards:
  - Tools are stateless and DB-backed
  - Explicit input/output schemas
  - user_id ownership enforced
- Agent rules:
  - Agent must use MCP tools for all task mutations
  - No direct DB access from agent logic
  - Action confirmations required
- Conversation persistence:
  - History rebuilt from DB per request
  - Server restart must not break chats
- Security:
  - JWT required for all chat/tool calls
  - user_id must match authenticated user
- Code hygiene:
  - No unused files or artifacts
  - Modular, single-responsibility structure

Check for:
- Unrealistic or non-hackathon-safe standards
- Missing enforcement criteria

Output:
- Updated, concise Constitution
- All rules measurable
- 2–3 concrete improvement

## Response snapshot

Updated constitution from v1.1.0 to v1.2.0 with comprehensive Phase III (AI-powered Todo Chatbot) standards.

**Added Three New Principles:**
1. **Principle VII: Stateless Architecture (NON-NEGOTIABLE)** - No in-memory state, database-backed persistence, server restart resilience
2. **Principle VIII: MCP Tool Standards (NON-NEGOTIABLE)** - Stateless tools, explicit Pydantic schemas, user_id enforcement
3. **Principle IX: Agent-Tool Interaction Rules** - Agent must use MCP tools, no direct DB access, action confirmations

**Enhanced Existing Principles:**
- Principle III (Security): Added Phase III chatbot security requirements (JWT for chat/tool calls)
- Principle IV (Technology Stack): Added Claude SDK, MCP, and chatbot stack components

**Added Phase III Compliance Checks:**
- Stateless Architecture Verification (no in-memory state, DB-backed persistence, server restart tests)
- MCP Tool Verification (schema validation, statelessness, user ownership enforcement)
- Agent-Tool Interaction Verification (no direct DB access, tool usage compliance, action confirmations)
- Conversation Persistence Verification (database schema, history reconstruction, cross-request consistency)
- Code Hygiene Verification (no unused files, modular structure, automated checks)

**Updated Definition of Done:**
- Added Phase III criteria (8 functional requirements, 8 technical requirements, 5 stateless architecture requirements, 5 MCP tool requirements, 5 security requirements, 5 code hygiene requirements)
- Separated Phase II and Phase III out-of-scope items

**Updated Technology Stack:**
- Added AI Chatbot Stack (Anthropic Claude SDK, MCP, streaming, Pydantic schemas)
- Added Phase III prohibitions (no other AI providers, no LangChain, no in-memory storage)

**Updated Development Workflow:**
- Added Phase III multi-agent coordination order
- Added Phase III specific guidelines (tools before chat, stateless verification, persistence testing)

All new standards are testable with explicit PASS/FAIL criteria and enforcement mechanisms.

## Outcome

- ✅ Impact: Constitution now provides comprehensive, testable standards for Phase III AI chatbot implementation with MCP architecture
- 🧪 Tests: All new principles include explicit verification checks with PASS/FAIL criteria
- 📁 Files: Updated .specify/memory/constitution.md (v1.1.0 → v1.2.0)
- 🔁 Next prompts: Ready for Phase III spec creation (/sp.specify), plan generation (/sp.plan), and task breakdown (/sp.tasks)
- 🧠 Reflection: Constitution now enforces stateless architecture, MCP tool standards, and agent-tool separation - critical for scalable, maintainable AI chatbot implementation

## Evaluation notes (flywheel)

- Failure modes observed: None - all standards are measurable and enforceable
- Graders run and results (PASS/FAIL): Manual review - PASS (all placeholders filled, version incremented, sync report complete)
- Prompt variant (if applicable): constitution-phase-iii-v1
- Next experiment (smallest change to try): Validate constitution compliance during Phase III implementation with automated checks
