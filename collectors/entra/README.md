# Microsoft Entra ID Collector

## Overview

The Microsoft Entra ID collector gathers security,
identity, and configuration evidence from Microsoft
Graph.

It is designed for compliance evidence collection
against frameworks such as:

- CIS Microsoft 365 Foundations Benchmark
- NIST Cybersecurity Framework
- ISO 27001
- SOC 2
- Cyber Essentials
- Government assurance profiles

## Features

The collector supports evidence collection for:

- Users
- Groups
- Devices
- Applications
- Enterprise applications
- Service principals
- Directory roles
- Authentication methods
- Sign-in logs
- Audit logs
- Conditional Access policies
- Identity Protection
- Privileged Identity Management

## Authentication

The collector uses Microsoft Entra application
authentication with OAuth 2.0 client credentials.

Required configuration:

```yaml
tenant_id: "<tenant-id>"
client_id: "<application-client-id>"
client_secret: "<application-secret>"
```

Required Microsoft Graph permission:

```
https://graph.microsoft.com/.default
```

The Azure application registration must be granted
the required Microsoft Graph application permissions
with administrator consent.

## Structure

```
entra/
├── auth.py
├── client.py
├── collector.py
├── manifest.yml
├── queries/
├── normalizers/
├── profiles/
└── tests/
```

## Usage

Example:

```python
collector = EntraCollector(
    manifest=manifest,
    evidence_writer=evidence_writer,
    normalizer=normalizer,
    validator=validator,
    config=config,
)

collector.connect()

users = collector.execute(
    "/users"
)
```

## Profiles

The collector includes compliance profiles:

```
profiles/
├── baseline.yml
├── caf.yml
├── cis.yml
├── cyberessentials.yml
├── full.yml
├── govassure.yml
├── iso27001.yml
├── nist.yml
└── soc2.yml
```

Profiles define which evidence queries are
required for each compliance framework.

## Error Handling

The collector uses the shared collector exception
hierarchy:

- `AuthenticationError`
- `ClientError`
- `RateLimitError`
- `EvidenceError`
- `ValidationError`

Microsoft Graph throttling responses are handled
through the common retry mechanism.

## Development

Run tests:

```bash
pytest collectors/entra/tests
```

Run linting:

```bash
ruff check collectors/entra
```

Format code:

```bash
ruff format collectors/entra
```

## License

Internal collector module.
