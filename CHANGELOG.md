# Changelog

All notable changes to AI-FlowCraft will be documented in this file.

## [V1.1.0] - 2026-05-12

### Added

#### New Directories
- `examples/` directory in test-related Skills (22-26) with test example files:
  - `test-examples.md` (Skill 22)
  - `component-test-examples.md` (Skill 23)
  - `integration-test-examples.md` (Skill 24)
  - `e2e-test-examples.md` (Skill 25)
  - `system-test-examples.md` (Skill 26)
- `CHANGELOG.md` in `resources/` directory of Skill 26-test-system
- `.zip` archive files for each Skill (28 total)

#### New Sections in SKILL.md
- **Usage Scenarios** section: Defines when to use each Skill
- **Not Applicable Scenarios** subsection: Guides users to the correct Skill
- **Instructions** section: Clarifies required inputs and outputs
- **Interaction Guidelines** section in test-related Skills

#### New Rules in GUARDRAILS.md
- **Rule 9**: Implementation and Design Document Consistency
  - Code produced during implementation phase must be consistent with design documents
  - Covers API paths, response formats, data model fields, and business rules
  - Any inconsistency must be recorded as a deviation
- **Section 7**: Global Failure Handling
  - Handling when prerequisites are not met
  - Handling errors during execution
  - Handling unexpected output

#### New Features in Test Skills (22-26)
- **Rule 12**: Design Document Driven Business Rule Coverage
  - Read "Service Layer Business Rules" from backend technical design
  - Write at least one positive test and one exception/boundary test for each rule
  - Add "Business Rule Coverage" section in test reports

### Changed

#### Directory Structure
- `assets/` → `templates/` (template files directory)
- `scripts/` → `resources/` (test scripts directory)

#### SKILL.md Format
- Simplified YAML frontmatter (removed `allowed-tools`, `metadata` fields)
- Reorganized section hierarchy:
  - "Project Context Protocol" and "Guardrails" became subsections of "Description"
  - "Workflow" became a subsection of "Instructions"
- Removed standalone "Document Quality Assurance" section in Skill 1

#### README.md
- Updated project structure diagram to include V1 version directory
- Updated file statistics table format

### Fixed
- Improved consistency in Skill documentation structure
- Better guidance for users on when to use each Skill

---

## [V1.0.1] - 2026-05-03

### Added
- Initial release of AI-FlowCraft with 28 professional Skills
- Complete workflow system from requirements to testing
- Document-driven development approach
- AC (Acceptance Criteria) traceability across all stages
- Guardrails mechanism for each Skill
- TDD-driven development process
- Five-layer testing pyramid
- Multi-tech stack support

### Skills Included
- **Project Startup (Skill 1-18)**: Requirements clarification, PRD generation, system architecture, database design, API design, etc.
- **Feature Development (Skill 19-21)**: Task planning, implementation, stage reporting
- **Testing (Skill 22-26)**: Unit, component, integration, E2E, and system testing
- **On-Demand (Skill 27-28)**: Feature evolution, bugfix workflow

### Documentation
- 28 SKILL.md files
- 24 output templates
- 25 test scripts
- 2 global protocol files (GUARDRAILS.md, PROJECT-CONTEXT.md)
- Chinese and English README files

---

## Version Summary

| Version | Date | Description |
|---------|------|-------------|
| V1.1.0 | 2026-05-12 | Directory restructuring, SKILL.md format optimization, new features |
| V1.0.1 | 2026-05-03 | Initial release with 28 Skills |
