<p align="center">
  <h1 align="center">AI-FlowCraft</h1>
  <p align="center">
    <strong>From a vague idea to a running full-stack website — 28 AI skills, seamlessly connected</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/version-1.1.1-blue" alt="Version" />
    <img src="https://img.shields.io/badge/skills-28-green" alt="Skills" />
    <img src="https://img.shields.io/badge/templates-24-cyan" alt="Templates" />
    <img src="https://img.shields.io/badge/test_scripts-25-purple" alt="Test Scripts" />
    <img src="https://img.shields.io/badge/license-Apache_2.0-orange" alt="License" />
  </p>
  <p align="center">
    <a href="#why">Why</a> ·
    <a href="#what">What</a> ·
    <a href="#features">Features</a> ·
    <a href="#skills-map">Skills Map</a> ·
    <a href="#supported-stacks">Tech Stacks</a> ·
    <a href="#quick-start">Quick Start</a> ·
    <a href="#architecture">Architecture</a> ·
    <a href="#comparison">Comparison</a> ·
    <a href="#faq">FAQ</a> ·
    <a href="#Star History">Star History</a>
  </p>
  <p align="center">
    English | <a href="README.md">中文</a>
  </p>
</p>

---

## Why · Why AI-FlowCraft

When building websites with AI, the root cause of failure is often **not that the AI isn't smart enough** — it's the **lack of systematic planning**.

> Toss a requirement at AI and ask it to write code — it drifts further off course with every step. Requirements aren't clear before coding starts. Architecture isn't settled before implementation begins. Tests aren't planned before going live. Every "good enough" decision plants the seeds for massive rework.

**Core problems AI-FlowCraft solves:**

| Pain Point | Status Quo | AI-FlowCraft's Solution |
|------------|-----------|------------------------|
| 🤷 Vague requirements → code immediately | AI writes code directly, results miss the mark | **Skill 1-2** Socratic questioning forces clarity before action |
| 🏗️ No design docs | Skip architecture, end up with messy, unmaintainable code | **Skill 3-9** Systematically produces architecture, DB, API, UX docs |
| 📏 No coding standards | AI-generated code is inconsistent in style and quality | **Skill 13-15** Auto-generates frontend/backend coding standards |
| 🧪 Testing is an afterthought | Bugs found after coding, fix cost grows exponentially | **Skill 20** TDD-first enforcement, **Skill 22-26** 5-layer test pyramid |
| 🔄 Cross-doc inconsistency | API docs don't match actual code, painful integration | Automated cross-doc consistency checks, AC traceable end-to-end |
| 🤖 AI oversteps bounds | Writing code during requirements, changing specs during testing | **Boundary guardrails** draw hard lines for each Skill |
| 🧠 AI loses context | AI forgets earlier discussions after long conversations, constant rework | **Document-driven programming** — every discussion produces docs, new windows auto-restore context via PROJECT-CONTEXT protocol |

---

## What · What is AI-FlowCraft

**AI-FlowCraft** is an **AI-assisted Skills workflow system for full-stack web development**.

It breaks down the entire process from "vague idea" to "tested delivery" into **28 specialized Skills**, each with a clear role, responsibilities, inputs/outputs, and quality baselines. Think of it as a virtual software development team — requirements analyst, architect, frontend/backend engineers, test engineers — each doing their job in a coordinated workflow.

**Recommended for use with Trae Solo software.**

```
A vague idea
  → Skill 1   Requirements discussion (Socratic questioning)
  → Skill 2   PRD generation (Acceptance Criteria)
  → Skill 3-9 System design (Architecture / DB / API / UX / Visual)
  → Skill 10-18 Standards & initialization (Coding standards / Project scaffold)
  → Skill 19-21 Feature development (Task planning / TDD coding / Stage reports)
  → Skill 22-26 Five-layer testing (Unit → Component → Integration → E2E → System)
  → A running full-stack website
```

---

## Features · Core Features

### 🎯 Document-Driven: Think Before You Code

No jumping straight into code. AI-FlowCraft forces complete design documents first (PRD, architecture, database, API, interaction design) — each goes through a **two-phase quality check** ensuring depth first, then correctness. At the same time, documents serve as AI's "external memory" — every discussion produces a documented record, and new windows auto-restore context via the PROJECT-CONTEXT protocol, **completely solving the AI context loss problem**.

### 🔄 AC Traceability Across the Full Chain

Acceptance Criteria born in the requirements doc flow through API design, technical specs, task planning, TDD coding, and test cases. Every AC has a unique ID and is fully traceable — ensuring "what was requested" = "what was coded" = "what was tested."

### 🛡️ Boundary Guardrails

Hard lines for every Skill. No code during requirements. No spec changes during testing. No architecture changes during coding. AI's "over-helpfulness" is the workflow's biggest enemy — in this system, **blind compliance = process destruction**.

### 🧪 TDD-Driven Development

Mandatory **Red → Green → Refactor** cycle during coding. Write failing tests first, write minimal code to pass, refactor under test protection. UI changes must be verified in a real browser — no "looks about right" hand-waving.

### 📐 Multi-Stack Support

Not tied to any framework. One workflow adapts to 4 frontend frameworks, 6 backend languages, 7 ORMs, 6 databases. Stack-specific rules are annotated with `（仅 XXX 项目适用）` so AI only executes rules relevant to your project.

### 🔍 Automated Quality Checks

Built-in Python scripts automatically check cross-document consistency — field names, API paths, page lists, response formats — any mismatch is caught.

---

## Skills Map · Skills Overview

28 Skills organized into 4 categories by development phase:

### 📋 Project Setup (Skill 1-18, execute once per project)

| # | Skill | Role | Output |
|---|-------|------|--------|
| 1 | Requirements Discussion | Requirements Analyst | Requirements discussion record |
| 2 | PRD Generation | Product Planner | Product requirements doc + Acceptance Criteria |
| 3 | System Architecture | System Architect | Tech stack + System architecture design |
| 4 | Information Architecture | Information Architect | Information architecture diagram (site map) |
| 5 | Data Model Convention | Data Model Designer | Data model field conventions |
| 6 | Interaction Design | Interaction Designer | Interaction design document |
| 7 | Database Design | Database Architect | ER diagram + DDL SQL |
| 8 | API Design | API Designer | API interface document |
| 9 | Design Spec | Visual Designer | Design Token + Visual spec |
| 10 | Backend Tech Design | Backend Architect | Feature-level backend technical spec |
| 11 | Frontend Tech Design | Frontend Architect | Feature-level frontend technical spec |
| 12 | Project Structure | Project Structure Engineer | Directory structure definition |
| 13 | Frontend Standards | Frontend Standards Engineer | Frontend coding standards |
| 14 | Backend Standards | Backend Standards Engineer | Backend coding standards |
| 15 | Collaboration Standards | Collaboration Engineer | Frontend-backend collaboration standards |
| 16 | Environment Config | Environment Config Engineer | Environment & configuration document |
| 17 | Roadmap Planning | Technical Product Manager | Milestones + development order |
| 18 | Project Initialization | Project Init Engineer | Project scaffold code |

### 💻 Feature Development (Skill 19-21, repeat per feature)

| # | Skill | Role | Output |
|---|-------|------|--------|
| 19 | Task Planning | Task Planning Engineer | Vertical slice task list |
| 20 | Implementation | Senior Developer | Code + Tests (TDD) |
| 21 | Stage Report | Quality Report Analyst | Stage completion report |

### 🧪 Test Safety Net (Skill 22-26, inside-out five layers)

| # | Skill | Test Level | Coverage |
|---|-------|-----------|----------|
| 22 | Unit Testing | Functions/Methods | Business logic, utilities, data transforms |
| 23 | Component Testing | UI Components | Render output, user interaction, state changes |
| 24 | Integration Testing | API + Database | Interface integration, data consistency, transactions |
| 25 | E2E Testing | User Flows | Core business flows, page navigation |
| 26 | System Testing | Full Chain | Security scanning, performance testing, compatibility |

### 🔧 Always Available (Skill 27-28, any time)

| # | Skill | Scenario | Description |
|---|-------|----------|-------------|
| 27 | Feature Evolution | Modify/extend existing features | < 30% incremental update, > 70% recommend full re-run |
| 28 | Bug Fix | Code behavior doesn't match requirements | Determine if it's a real bug first, minimal change fix |

---

## Supported Stacks · Tech Stack Support

AI-FlowCraft adapts to multiple tech stacks through a "scope annotation" mechanism. Stack-specific rules are annotated with `（仅 XXX 项目适用）`, and AI only executes rules matching your project.

### Frontend

| Category | Supported Technologies |
|----------|----------------------|
| **Frameworks** | React 18+, Vue 3+, Angular 17+, Svelte 4+, Next.js 14+, Nuxt 3+, Astro 4+ |
| **Language** | TypeScript 5+ (strict mode enforced) |
| **Build Tools** | Vite 5+, Webpack 5+, Turbopack |
| **Styling** | TailwindCSS 3+, CSS Modules, Styled Components, UnoCSS |
| **State Management** | Zustand, Redux Toolkit, Pinia, NgRx, MobX |
| **Test Frameworks** | Vitest, Jest, React Testing Library, Vue Test Utils |
| **E2E Frameworks** | Playwright, Cypress |

### Backend

| Category | Supported Technologies |
|----------|----------------------|
| **Languages/Frameworks** | Node.js (NestJS / Express / Fastify), Python (Django / FastAPI), Go (Gin / Echo), Java (Spring Boot), Rust (Actix-web / Axum), C# (.NET 8+) |
| **ORMs** | Prisma, TypeORM, Drizzle ORM, SQLAlchemy, GORM, Entity Framework Core |
| **Databases** | PostgreSQL, MySQL, SQLite, MongoDB, Redis, Elasticsearch |
| **Auth** | JWT, Session, OAuth 2.0 |
| **API Styles** | REST, GraphQL, gRPC |
| **Message Queues** | RabbitMQ, Kafka, Redis Streams |

### Project Type Adaptation

| Project Type | Skills to Skip |
|-------------|---------------|
| Backend-only API | Skill 4, 6, 9, 11, 13 |
| Frontend-only App | Skill 7, 8, 14 |
| Single-feature project | Can merge Skill 2-9 |

---

## Quick Start

### Prerequisites

- An AI coding assistant (Trae Solo)
- Import this repository's Skill files into your AI workspace
- The `specs/` folder and its 4 files (`GUARDRAILS.md`, `PROJECT-CONTEXT.md`, `validate_consistency.py`, `report_config.py`) must exist before starting a project

### Three Steps to Start a New Project

**Step 1: Clarify Requirements**

```
"Use Skill 1 to help me clarify requirements, I want to build..."
```

AI will use Socratic questioning to turn your vague idea into a clear project description.

**Step 2: Generate PRD**

```
"Use Skill 2 to generate PRD"
```

AI will produce a product requirements document with Acceptance Criteria. Complex projects will automatically generate separate docs per feature.

**Step 3: Follow the Workflow**

```
"Use Skill 3 to design system architecture"
```

Then execute Skills 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 17 → 18 in order to complete all design and project initialization.

### Feature Development Loop

```
"Use Skill 19 to plan tasks" → "Use Skill 20 to implement" → "Use Skill 21 to generate report"
```

Repeat this loop for each feature.

### Test Safety Net

```
"Use Skill 22 to start unit testing"
```

Execute Skills 22 → 23 → 24 → 25 → 26 from inside out for five-layer testing.

> 💡 **Tip**: Try to complete the project setup phase (Skill 1-18) in a single conversation window to avoid context loss.

---

## Architecture · Design Philosophy

### Five Core Mechanisms

#### 1. Boundary Guardrails

Every Skill has clear responsibility boundaries. AI must self-check before generating any response:

- **Scope Check**: Is the user's request within the current Skill's responsibilities?
- **Artifact Check**: Am I about to generate documentation/plans, or executable code/operations?

If the user asks for code during the requirements phase, AI refuses and guides back — not with "sorry I can't", but with professionalism: "To avoid premature technical details causing rework, let's first confirm [business logic]..."

#### 2. Project Context Protocol

Forces AI to establish project context before executing any Skill. 6 core documents are mandatory reading: PRD, Tech Stack, System Architecture, Information Architecture, Data Model, Project Structure.

> Spend 5 minutes reading docs, save 2 hours of rework.

#### 3. AC Traceability

```
Skill 2 PRD produces AC → Skill 8 API maps AC → Skill 10/11 Tech spec maps AC
→ Skill 19 Tasks inherit AC → Skill 20 TDD verifies AC → Skill 22-26 Test coverage
```

AC format: `{FEATURE}-AC-{NUMBER}` (e.g., `AUTH-AC-001`), covering three scenarios: Happy Path / Edge & Error / Business Rules.

#### 4. Document Quality Check Loop

Two-phase check after every document is produced:

- **Phase A (Deep Refinement)**: Review depth, completeness, actionability chapter by chapter, min 2 / max 5 loops
- **Phase B (Bug Check)**: Check internal consistency, cross-doc consistency, AC coverage, placeholder residue, min 1 / max 3 loops

Make content good enough first, then make it error-free.

#### 5. TDD-Driven Development

Mandatory Red-Green-Refactor cycle during coding:

- **RED**: Write failing tests first
- **GREEN**: Write minimal code to pass tests
- **REFACTOR**: Optimize under test protection

TDD passing ≠ task complete. Tasks with UI changes must be verified in a real browser.

### Project Structure

```text
ai-flowcraft/
├── README.md                                  ← English docs
├── README.md                                  ← Chinese docs
├── assets/                                    ← Project assets
│   └── logo.jpg                               ← Project logo
├── specs/                                     ← Global protocols + utility scripts
│   ├── GUARDRAILS.md                          ← Boundary guardrail rules
│   ├── PROJECT-CONTEXT.md                     ← Project context protocol
│   ├── validate_consistency.py                ← Cross-document consistency checker
│   └── report_config.py                       ← Test report config
└── skills/                                    ← 28 Skills
    ├── project/                               ← Project setup (Skill 1-18)
    │   ├── 1-project-requirements-clarification/
    │   ├── 2-project-prd-generation/
    │   ├── ...
    │   └── 18-project-initialization/
    ├── feature/                               ← Feature dev + testing (Skill 19-28)
    │   ├── 19-feature-task-planning/
    │   ├── 20-feature-implementation/
    │   ├── ...
    │   └── 28-bugfix-workflow/
```

### File Statistics

| Type | Count | Description |
|------|-------|-------------|
| SKILL.md | 28 | Skill definition files (role, workflow, baseline rules) |
| Output templates (assets/) | 24 | Document templates for Skill 1-21, 27-28 |
| Test scripts (scripts/) | 25 | Python scripts for Skill 22-26 (5 each) |
| Utility scripts (specs/) | 2 | Cross-doc checker + report config |
| Global protocols (specs/) | 2 | GUARDRAILS + PROJECT-CONTEXT |
| **Total** | **81 files** | |

### Runtime Output

When you develop a project with AI-FlowCraft, it produces:

```text
{your-project}/
├── specs/                          ← Project planning docs (19+)
│   ├── Product Requirements.md
│   ├── System Architecture.md, Tech Stack.md
│   ├── Information Architecture.md, Data Model Conventions.md
│   ├── Interaction Design.md, Database Design.md
│   ├── API Interface Doc.md, Design Spec.md
│   ├── Project Structure.md, Frontend/Backend Coding Standards.md
│   ├── Collaboration Standards.md, Environment Config.md
│   ├── Development Roadmap.md
│   └── features/                   ← Feature-level docs
│       ├── {feature-name}.md
│       ├── {feature-name}_backend-tech-spec.md
│       ├── {feature-name}_frontend-tech-spec.md
│       └── {feature-name}_task-plan.md
├── src/                            ← Your source code
│   ├── frontend/                   ← Frontend project
│   └── backend/                    ← Backend project
└── docs/                           ← Development records
    ├── dev-records/                ← Init records, slice completion records
    ├── test-reports/               ← Unit/Component/Integration/E2E/System test reports
    └── bugfix-records/             ← Bug fix documents
```

---

## Comparison · How It Compares

| Dimension | AI-FlowCraft | .cursorrules | .windsurfrules | CLAUDE.md |
|-----------|-------------|-------------|---------------|----------|
| **Positioning** | Complete dev workflow (28 Skills) | AI coding behavior rules | AI coding behavior rules | AI coding behavior rules |
| **Coverage** | Requirements → Design → Code → Test | Code only | Code only | Code only |
| **Skill Count** | 28 | 1 file | 1 file | 1 file |
| **Document Output** | 19+ design documents | None | None | None |
| **Process Control** | Boundary guardrails + forced phase ordering | None | None | None |
| **Quality Assurance** | Two-phase doc checks + AC traceability + automated validation | None | None | None |
| **Test Strategy** | Five-layer test pyramid | None | None | None |
| **Cross-Doc Consistency** | Python script auto-validation | None | None | None |

> **In one sentence**: .cursorrules tells AI *how to write code*. AI-FlowCraft tells AI *how to build a project* — from figuring out what to build, to writing and testing every line correctly.

---

## FAQ · Frequently Asked Questions

### Does it support non-English projects?

Yes. All Skill document templates, interaction prompts, and output filenames support any language including Chinese, Japanese, Korean, etc. Specify your preferred language during the requirements discussion phase.

### Can I use only some Skills?

Yes. The 28 Skills are modular:

- Only need requirements analysis? Run Skill 1-2
- Only need design documents? Run Skill 3-9
- Only want TDD coding? Run Skill 19-20
- Only need test coverage? Run Skill 22-26

We recommend running the full workflow at least once to experience the value of the complete process.

### Does it work for non-fullstack projects?

Yes. Built-in project type adaptation:

- **Backend-only API**: Automatically skips frontend Skills (4, 6, 9, 11, 13)
- **Frontend-only App**: Automatically skips backend Skills (7, 8, 14)
- **Single-feature project**: Can merge Skill 2-9 to simplify

### Must I follow the order strictly?

The project setup phase (Skill 1-18) should follow order since later Skills depend on earlier outputs. Feature development (Skill 19-21) and testing (Skill 22-26) phases can be executed on demand.

### Does it conflict with AI coding tools (Cursor / Copilot)?

No. AI-FlowCraft operates at the workflow level and is tool-agnostic. You can use Claude + AI-FlowCraft in Cursor, or Copilot + AI-FlowCraft in VS Code. AI-FlowCraft defines *what to do, in what order, to what standard* — not *which tool to use*.

### How long does a project take?

Depends on complexity:

- **Simple project** (single feature): Skill 1-18 under 1 hour of conversation, feature dev by actual code volume
- **Medium project** (5-10 features): Skill 1-18 ~2-3 hours of conversation
- **Complex project** (10+ features): Split across multiple sessions, focus on one phase per session

> Note: Project setup (Skill 1-18) is a one-time investment. Each subsequent feature only needs the Skill 19-21 loop.

### How do I handle AI context window limits?

- Project setup (Skill 1-18): Keep in a **single conversation window**
- Feature development: **Open new windows per feature** — AI auto-reads project docs via PROJECT-CONTEXT protocol
- Each design document is independently readable — new windows don't need chat history

## Star History

<a href="https://www.star-history.com/?repos=zlh12331%2FAI-FlowCraft&type=timeline&logscale=&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=zlh12331/AI-FlowCraft&type=timeline&theme=dark&logscale&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=zlh12331/AI-FlowCraft&type=timeline&logscale&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=zlh12331/AI-FlowCraft&type=timeline&logscale&legend=top-left" />
 </picture>
</a>

---

## License

[Apache License 2.0](LICENSE)

---

<p align="center">
  Build your next full-stack project with AI-FlowCraft ⚡
</p>
