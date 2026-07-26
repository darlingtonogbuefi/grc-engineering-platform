# Contributing Guidelines

Thank you for contributing to the GRC Engineering Platform.

This project follows software engineering best practices and encourages consistent, high-quality contributions.

---

# Development Principles

All contributions should be:

- Tested
- Documented
- Version controlled
- Peer reviewed
- Secure by design

---

# Adding a Capability

Create a new capability under:

```text
capabilities/<domain>/<capability-name>/
```

Required files:

```text
metadata.yml
mapping.yml
collectors.yml
validation.yml
evidence.yml
README.md
tests/
```

---

# Collector Requirements

Collectors must:

- Be read-only by default
- Use supported Microsoft APIs
- Produce JSON output
- Validate against schemas
- Include documentation
- Include automated tests
- Handle errors gracefully

---

# Testing

Before submitting changes, run:

```powershell
./scripts/Test-All.ps1
```

All tests must pass.

---

# Pull Requests

Every pull request should include:

- Description of changes
- Framework impact
- Evidence impact
- Validation impact
- Testing completed
- Security considerations

---

# Coding Standards

- Use descriptive naming
- Document public functions
- Prefer reusable modules
- Follow PowerShell best practices
- Keep collectors idempotent
- Avoid breaking existing capability interfaces