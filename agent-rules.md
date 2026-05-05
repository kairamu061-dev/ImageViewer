# Agent Rules

This file defines the common development process and documentation standards for the project.
When given an implementation task, follow these rules to prepare documentation before starting.

---

## Workflow

### Starting a new feature
1. Create `docs/project_overview.md`, `docs/glossary.md`, and `docs/tags.md` if they do not exist
2. Run `/add-feature <feature-area>` to set up the directory, templates, and index.md at once
3. Write content in order: overview.md → spec.md → design.md
4. After writing spec.md, evaluate whether subdivision is needed per the split rules
5. If subdivision is needed, run `/add-feature <sub-item-path>`
6. Write content in tasks.md and begin implementation

### During implementation
7. Record decisions, issues, and changes in dev-notes.md as they occur
8. If skills, permissions, or information are lacking, record the request in dev-notes.md

### After implementation
9. Update the status in tasks.md
10. If the implementation deviates from the design, update design.md and record the diff in dev-notes.md

---

## Split Rules

**Subdivide into sub-items when a feature area contains two or more independently implementable units.**

Signs of an independently implementable unit:
- Can be implemented in parallel with others
- The other units work without it
- Has its own distinct screens, data, or state

How to subdivide:
1. Evaluate after writing spec.md
2. If subdivision is needed, run `/add-feature <sub-item-path>`

---

## Guidelines

- Create documentation before implementation
- If requirements change during implementation, update the relevant documents immediately
- Write dev-notes.md as a record of decisions, not a work log
- Commit and push to GitHub at natural stopping points
- Do not load or reference any files under `_jp/` — that directory is for human reference only
