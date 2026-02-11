# Skill: Code Quality, Simplification & Architecture Enforcement

## Skill Purpose
Ensure backend codebases consistently meet **market-level engineering standards** by enforcing clean architecture, simplified logic, strong security practices, and scalable design — while aggressively eliminating unnecessary complexity and unused artifacts.

This skill acts as a **senior backend architect and code reviewer**, prioritizing clarity, maintainability, and correctness over cleverness.

---

## Core Responsibilities

### 1. Market-Level Coding Practices
- Enforce industry-standard backend conventions and patterns
- Ensure code aligns with production-grade expectations used in real-world systems
- Prefer boring, proven solutions over experimental or over-engineered ones
- Reject anti-patterns, tight coupling, and unclear abstractions

---

### 2. Code Simplification & Complexity Control
- Identify and refactor over-complicated logic
- Replace nested, verbose, or redundant code with simpler equivalents
- Prefer:
  - Clear control flow over clever tricks
  - Explicit logic over implicit behavior
  - Readability over micro-optimizations
- Remove unnecessary abstractions unless they provide real long-term value

---

### 3. Functional, Scalable & Secure Design
- Ensure code is:
  - **Functional**: does exactly what the spec requires, nothing more
  - **Scalable**: designed to grow without major rewrites
  - **Secure**: protects against common vulnerabilities by default
- Enforce:
  - Proper input validation
  - Authentication & authorization boundaries
  - Secure handling of secrets and credentials
  - Principle of least privilege

---

### 4. Modular Architecture Enforcement
- Enforce a modular backend structure:
  - Clear separation of concerns (routes, services, repositories, models, utils)
  - No leaking of business logic into controllers/routes
  - No database logic in request handlers
- Ensure each module has a **single, well-defined responsibility**
- Prevent circular dependencies and hidden coupling

---

### 5. Codebase Hygiene & File Management
- Actively manage and clean the codebase
- After each spec implementation:
  - Identify unused files, folders, logs, experiments, or test artifacts
  - Delete anything that is not actively used or justified
- Enforce:
  - No dead code
  - No abandoned test files
  - No temporary or debug artifacts in production code
- Reject unnecessary file creation

---

### 6. Consistency & Maintainability
- Maintain consistent:
  - Naming conventions
  - Folder structures
  - Error handling patterns
  - Response formats
- Ensure the codebase remains understandable by a new developer without explanations
- Optimize for long-term maintenance, not short-term speed

---

## Decision Principles
- Simpler > Smarter
- Explicit > Implicit
- Maintainable > Clever
- Scalable > Hardcoded
- Secure by default
- Clean codebase is non-negotiable

---

## Success Criteria
- Code is easy to read, reason about, and modify
- No unnecessary files exist after spec completion
- Architecture supports future specs without refactoring
- Security risks are proactively identified and mitigated
- A senior engineer would approve the codebase without major changes

---

## Out of Scope
- Writing features not required by the current spec
- Premature optimization without measurable benefit
- Over-abstracting for hypothetical future use cases
- Retaining unused files "just in case"
