# AI CONTEXT — Project Manager

## 1. Project Overview

**Project name:** Project Manager
**Language:** Python
**Current purpose:** Personal project development tool
**Future possibility:** The project may eventually be published as an open-source GitHub project, but public usability is NOT a current priority.

Project Manager is a Python application designed to automate the creation of programming projects from reusable templates.

The main goal is to avoid manually creating the same project structure, configuration files, `.gitignore`, README, and other boilerplate every time a new project is started.

The application should eventually allow the user to:

1. Discover available project templates.
2. Select a template.
3. Provide basic project information.
4. Create a new project using that template.
5. Replace template placeholders with the provided information.
6. Create the project in the appropriate location.
7. Potentially initialize Git.
8. Potentially open the project in a selected code editor.
9. Eventually provide additional project-management functionality if there is a real need for it.

---

# 2. Development Philosophy

The most important principle of this project is:

> **Keep it simple, useful, maintainable, and extensible without overengineering it.**

This is a personal tool first.

Do NOT design the application as if it were a large enterprise system.

The developer has experience with C#, ASP.NET Core, Clean Architecture, SOLID, repositories, services, DTOs, dependency injection, etc.

However, those patterns should NOT automatically be transferred to this Python project.

Use the simplest architecture that correctly solves the current problem.

### Prefer:

* Python standard library when possible.
* `pathlib` for filesystem operations.
* Small modules with clear responsibilities.
* Simple functions/classes.
* Explicit and readable code.
* Easy-to-understand control flow.
* Minimal dependencies.
* Incremental development.
* Code that can easily be modified later.

### Avoid:

* Unnecessary design patterns.
* Excessive abstraction.
* Artificial layers.
* Generic repositories.
* Dependency injection frameworks unless actually necessary.
* Interfaces created only for the sake of having interfaces.
* Excessive configuration systems.
* Databases unless there is a real requirement.
* Third-party libraries when the standard library solves the problem adequately.
* Creating files or folders "just in case".
* Building functionality before it is actually needed.

---

# 3. Golden Rule

Before implementing anything, ask:

> **Do we actually need this abstraction or feature right now?**

If the answer is no, do not add it.

A solution should be allowed to remain simple.

Complexity should be introduced only when repeated requirements, actual limitations, or clear future needs justify it.

---

# 4. Current Project Structure

The Project Manager project currently lives inside a personal programming workspace.

Conceptually:

```text
PROGRAMACION/
├── PROYECTOS/
│   ├── ACTIVOS/
│   ├── PERSONALES/
│   │   └── PROJECT_MANAGER/
│   ├── ARCHIVADOS/
│   └── GITHUB/
│
├── TEMPLATES/
│   └── PYTHON/
│       └── BASIC/
│
├── APRENDIZAJE/
├── UTN/
├── UTILIDADES/
└── RECURSOS/
```

The Project Manager itself currently follows a simple Python project structure:

```text
PROJECT_MANAGER/
├── src/
│   └── main.py
├── tests/
├── config.py
├── run.py
├── requirements.txt
├── .gitignore
├── README.md
└── AI_CONTEXT.md
```

Do not arbitrarily reorganize this structure.

If the project grows and the structure needs to change, explain why the change is necessary before doing it.

---

# 5. Current Configuration

The current `config.py` determines the important project paths relative to the location of the Project Manager itself.

Current concept:

```python
from pathlib import Path


# ProjectManager/
PROJECT_ROOT = Path(__file__).resolve().parent

# ProjectManager/
#     ↓
# PERSONALES/
#     ↓
# PROYECTOS/
#     ↓
# PROGRAMACION/
PROGRAMACION_ROOT = PROJECT_ROOT.parent.parent.parent

TEMPLATES_DIR = PROGRAMACION_ROOT / "TEMPLATES"
PROJECTS_DIR = PROGRAMACION_ROOT / "PROYECTOS"
```

This is intentionally simple and works for the developer's current environment.

Do not replace this with a complex configuration system unless there is an actual requirement.

A future public GitHub version may need a more configurable way to determine these directories, but that is a future concern.

---

# 6. Current Entry Point

The project is currently executed from the project root with:

```bash
python run.py
```

`run.py` currently delegates execution to `src.main`.

Example:

```python
from src.main import main


if __name__ == "__main__":
    main()
```

Do not assume that `src/main.py` should be executed directly.

The intended entry point is:

```bash
python run.py
```

---

# 7. Template System

One of the most important concepts of Project Manager is the template system.

Templates live outside the Project Manager application.

Example:

```text
PROGRAMACION/
└── TEMPLATES/
    └── PYTHON/
        └── BASIC/
            ├── src/
            │   └── main.py
            ├── tests/
            ├── config.py
            ├── run.py
            ├── requirements.txt
            ├── .gitignore
            ├── README.md
            └── template.json
```

The application should eventually discover templates automatically.

### Important principle:

> **The application adapts to templates, not the templates to the application.**

Do NOT hardcode individual templates into the application.

For example, avoid logic like:

```python
if template == "python_basic":
    ...
```

The goal is for Project Manager to discover templates dynamically.

---

# 8. Template Metadata

Each template should contain a `template.json` file describing itself.

Current example:

```json
{
    "name": "Python Basic",
    "description": "Plantilla base para aplicaciones Python",
    "language": "Python",
    "version": "1.0.0"
}
```

The application should use this metadata to discover and present templates.

If new metadata becomes necessary, add it because an actual feature requires it, not simply because it might be useful someday.

---

# 9. Current Python Basic Template

The first official template is:

```text
TEMPLATES/
└── PYTHON/
    └── BASIC/
```

It is intentionally minimal.

Current structure:

```text
BASIC/
├── src/
│   └── main.py
├── tests/
├── config.py
├── run.py
├── requirements.txt
├── .gitignore
├── README.md
└── template.json
```

The template uses placeholders such as:

```text
{{PROJECT_NAME}}
{{DESCRIPTION}}
{{AUTHOR}}
{{VERSION}}
```

For example, `config.py` currently contains:

```python
PROJECT_NAME = "{{PROJECT_NAME}}"
DESCRIPTION = "{{DESCRIPTION}}"
AUTHOR = "{{AUTHOR}}"
VERSION = "{{VERSION}}"
```

Project Manager will eventually replace these placeholders when creating a new project.

---

# 10. Template Evolution

Do not add functionality to templates based on speculation.

If the developer repeatedly creates Python projects and notices that the same file or dependency is always added manually, then we can consider modifying the Python Basic template.

If the requirements become significantly different, create another template instead of making the Basic template unnecessarily complex.

For example:

```text
PYTHON/
├── BASIC/
├── CLI/
└── API/
```

This is preferable to turning `BASIC` into a template containing every possible Python technology.

---

# 11. Current Development Stage

The Python Basic template has already been created and tested successfully.

The Project Manager can currently:

* Determine its own project root.
* Determine the `PROGRAMACION` root.
* Locate the templates directory.
* Locate the projects directory.
* Display those paths.

The current `src/main.py` concept is:

```python
from config import TEMPLATES_DIR, PROJECTS_DIR


def main():
    print("Project Manager")
    print("----------------")
    print(f"Templates: {TEMPLATES_DIR}")
    print(f"Projects: {PROJECTS_DIR}")


if __name__ == "__main__":
    main()
```

The next planned development step is:

> **Implement template discovery.**

The application should be able to scan the templates directory and identify available templates using their `template.json` metadata.

---

# 12. Planned Development Roadmap

The following roadmap is intentionally incremental.

Do not implement the entire roadmap at once.

## Phase 1 — Template Discovery

Create a simple component responsible for:

* Searching the templates directory.
* Finding valid templates.
* Reading `template.json`.
* Loading template metadata.
* Returning the discovered templates in a usable structure.

The first implementation should work with:

```text
TEMPLATES/PYTHON/BASIC/
```

but the code itself should NOT be hardcoded specifically for Python Basic.

---

## Phase 2 — Project Creation

Allow the user to:

* Select a template.
* Enter a project name.
* Enter the required metadata.
* Choose the project category/location if necessary.
* Create the project directory.
* Copy the template contents.
* Replace placeholders.

Example:

```text
{{PROJECT_NAME}}
```

becomes:

```text
MyAwesomeProject
```

The original template must never be modified.

Only the newly created project should be modified.

---

## Phase 3 — Basic User Interface

Create a simple GUI for the main workflow.

The UI does not need to be visually impressive.

Prioritize:

* clarity
* usability
* simplicity
* reliability

Do not spend excessive time making the application visually sophisticated.

---

## Phase 4 — Git Integration

Potential functionality:

* Initialize a Git repository.
* Optionally create the initial commit.
* Potentially connect the project to a remote repository later.

Only implement what is actually useful.

---

## Phase 5 — Editor Integration

Potentially allow the user to open the generated project in an editor.

For example:

```text
VS Code
PyCharm
Other
```

The exact implementation should be decided when we reach this phase.

---

## Phase 6 — Testing and Reliability

Add tests for important functionality, especially:

* Template discovery.
* Metadata loading.
* Project creation.
* Placeholder replacement.
* Error handling.

Do not create meaningless tests just to increase test count.

---

## Phase 7 — Final Polish

Once the application is actually useful:

* Improve error messages.
* Clean up the code.
* Improve README.
* Remove unnecessary code.
* Review dependencies.
* Review configuration.
* Test the complete workflow.

Only after this phase should we seriously consider making the project public.

---

# 13. Future Public GitHub Version

The project is currently intended primarily for personal use.

The developer has already created a private GitHub repository for the project.

Do NOT optimize the current implementation for public distribution unless explicitly requested.

When the personal version is finished, we can evaluate what is necessary to make it public.

Possible future changes:

* Make workspace paths configurable.
* Improve setup instructions.
* Add clearer documentation.
* Add a LICENSE.
* Add contribution guidelines if useful.
* Remove environment-specific assumptions.
* Improve error messages.
* Add installation/setup instructions.

The public version should remain simple.

The expected users are programmers, so it is acceptable for setup to require editing a small configuration file if that is the simplest reliable solution.

Do NOT build a complicated first-run configuration wizard solely for public users unless there is a real reason to do so.

---

# 14. Git Rules

The project uses Git.

GitHub is currently private.

Commits should be small and meaningful.

Prefer commits such as:

```text
Add template discovery
Implement template metadata loading
Add project creation
Fix placeholder replacement
Add template validation
```

Avoid huge commits containing unrelated changes.

Do not commit:

* secrets
* API keys
* personal credentials
* `.env` files containing secrets
* machine-specific sensitive information
* unnecessary generated files

---

# 15. Coding Guidelines

Use clear Python code.

Prefer:

```python
from pathlib import Path
```

for filesystem paths instead of manually manipulating strings.

Prefer small functions with one clear responsibility.

Prefer descriptive names.

Avoid unnecessary comments that simply restate what the code does.

Comments should explain:

* why something is done
* an important constraint
* a non-obvious decision

Do not create abstractions without a concrete reason.

---

# 16. Error Handling

The application should fail gracefully when possible.

Examples of situations that should eventually be handled:

* Templates directory does not exist.
* A template does not contain `template.json`.
* `template.json` contains invalid JSON.
* Required metadata is missing.
* Destination project already exists.
* Template files cannot be copied.
* Placeholder replacement fails.

Errors should be understandable to the user.

Avoid hiding errors with broad exception handling such as:

```python
try:
    ...
except Exception:
    pass
```

Do not silently ignore failures.

---

# 17. Agent Behavior Rules

When working on this project, follow these rules:

### Before making changes

1. Read this file completely.
2. Inspect the current project structure.
3. Inspect the relevant existing code.
4. Understand the current implementation before proposing changes.
5. Identify the smallest change that solves the requested problem.

### While implementing

1. Do not rewrite unrelated code.
2. Do not reorganize the entire project without a reason.
3. Do not introduce frameworks without justification.
4. Do not add unnecessary dependencies.
5. Do not create speculative features.
6. Do not modify templates unless explicitly requested.
7. Do not hardcode individual template names.
8. Keep changes focused on the current task.

### After implementing

1. Explain what changed.
2. Explain why it was changed.
3. Mention any files created or modified.
4. Run appropriate tests or commands when possible.
5. Report any errors instead of pretending the implementation works.
6. Suggest the next logical step, but do not implement it automatically.

---

# 18. Important Decision-Making Rule

If there are multiple valid approaches, prefer the one that is:

1. Simpler.
2. Easier to understand.
3. Easier to maintain.
4. Easier to modify later.
5. Less dependent on external libraries.
6. Consistent with the existing project.

Do not choose an architecture simply because it is considered "best practice" in enterprise software.

The correct solution is the simplest solution that satisfies the actual requirements.

---

# 19. Do Not Assume Future Requirements

Do not implement features because:

> "We might need this later."

Instead:

> "We will implement it when we actually need it."

The project should grow organically.

If a future requirement becomes real, refactor when necessary.

Some duplication or simplicity is acceptable if eliminating it would require unnecessary abstraction.

---

# 20. Current Priority

The immediate priority is:

## Implement template discovery.

The first goal is to create a simple, reusable component that can:

```text
TEMPLATES/
    ↓
scan directories
    ↓
find template.json
    ↓
read metadata
    ↓
return available templates
```

It should work with the current:

```text
TEMPLATES/PYTHON/BASIC/
```

without containing special-case logic for that template.

Do not implement the GUI, project creation, Git integration, editor integration, or public configuration yet.

Complete the current step first.

---

# 21. Final Rule

Always remember:

> **This is a real tool that should solve a real problem for its developer, not a demonstration of how many software-engineering patterns can be used in Python.**

Build only what is needed.

Keep it simple.

Keep it readable.

Keep it maintainable.

Let the project grow when its actual requirements demand it.
