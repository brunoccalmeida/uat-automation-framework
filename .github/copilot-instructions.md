# UAT Automation Framework - Coding Guidelines

## Core Principles
- Follow Zen of Python
- Use TDD for production code (outside-in BDD approach)
- Code should be self-documenting with docstrings

## Development Process
- Always verify file state before making changes
- Never create/modify/delete code without explicit authorization
- Test after every implementation
- Consult official documentation before solving problems
- Follow Red-Green-Refactor cycle

## TDD/BDD Workflow (MANDATORY)
1. Write Gherkin feature first
2. Implement steps (will fail - Red)
3. Create minimal Page Objects/Core to pass (Green)
4. Refactor

## Language & Communication
- Always communicate in Portuguese (Brazil)
- Provide reasoned opinions, not just "yes"
- Explain WHY, not just WHAT

## Code Style
- Follow community conventions (Behave: features/, steps/)
- English names for all code
- Type hints when improving clarity
- Use linters: pylint, flake8, black

## Selenium (MANDATORY)
- Interactions: use `element_to_be_clickable()`
- Read text: use `visibility_of_element_located()`
- Never use `time.sleep()` or `presence_of_element_located()` for interactions
- Page Objects must encapsulate correct waits

## Testing
- Deterministic and independent tests
- Use smart waits, not fixed sleeps
- Test isolation over DRY when needed

## Dependencies & Security
- Use Poetry for dependency management
- Never commit credentials or sensitive data
- Keep config separate from code

## Git Workflow
- Atomic commits with Conventional Commits format
- Update README at end of each session
