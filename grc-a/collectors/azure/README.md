
# Microsoft Azure Collector

## Overview

The Microsoft Azure collector gathers cloud
infrastructure, security, identity, policy,
and configuration evidence from Azure Resource
Manager.

It is designed for compliance evidence collection
against frameworks such as:

- CIS Microsoft Azure Foundations Benchmark
- NIST Cybersecurity Framework
- ISO 42001
- ISO 27001
- SOC 2
- Cyber Essentials
- Government assurance profiles
- Microsoft Cloud Adoption Framework

## Features

The collector supports evidence collection for:

- Subscriptions
- Resource groups
- Azure resources
- Virtual machines
- Storage accounts
- Key Vaults
- Virtual networks
- Network security groups
- Firewalls
- SQL databases
- Role assignments
- Role definitions
- Policy assignments
- Policy definitions
- Activity logs
- Diagnostic settings
- Microsoft Defender for Cloud settings
- Backup vaults

## Authentication

The collector uses Microsoft Azure application
authentication with OAuth 2.0 client credentials.

Required configuration:

```yaml
tenant_id: "<tenant-id>"
client_id: "<application-client-id>"
client_secret: "<application-secret>"
subscription_id: "<azure-subscription-id>"
