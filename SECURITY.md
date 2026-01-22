# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

PromptShield takes security seriously. If you discover a vulnerability, please follow these steps:

1.  **Do NOT** open a public issue on GitHub.
2.  Email the security team at `security@promptshield.com`.
3.  Include a detailed description of the vulnerability and steps to reproduce.
4.  We will acknowledge your report within 48 hours and provide a timeline for a fix.

## AI Safety & Secure Installation

For developers working on PromptShield, we have established specific protocols to mitigate AI-assisted coding risks (Prompt Injection, Package Hallucination, etc.).

Please read **[SAFE_INSTALL.md](SAFE_INSTALL.md)** before contributing or installing dependencies.

## Secrets Management

-   We use **Gitleaks** to prevent secrets from being committed.
-   Configuration is managed via `backend/config.py` and environment variables.
-   Never commit `.env` files.

## Incident Response

In the event of a data breach or confirmed vulnerability:
1.  We will patch the vulnerability immediately.
2.  We will rotate any compromised secrets (API keys, DB credentials).
3.  We will notify affected users via email.
