# Security Policy

## Reporting Vulnerabilities

Please report security vulnerabilities privately.

Do **not** publicly disclose vulnerabilities until they have been investigated and remediated.

---

# Sensitive Data

Never commit:

- Passwords
- API Keys
- Tokens
- Certificates
- Client secrets
- Production evidence
- Personal information
- Tenant configuration exports

---

# Evidence Protection

Evidence repositories should implement:

- Encryption at rest
- Encryption in transit
- Multi-Factor Authentication (MFA)
- Least privilege access
- Role-Based Access Control (RBAC)
- Retention policies
- Audit logging

---

# Secure Development

Recommended controls include:

- Secret scanning
- Dependency scanning
- Static code analysis
- Code review
- Automated testing
- Branch protection
- Signed commits (recommended)
- Security validation in CI/CD

---

# Supported Versions

| Version | Supported |
|----------|-----------|
| 0.1.x | ✅ |