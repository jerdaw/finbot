# Security Policy

## Supported Versions

We release updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting Issues

If you discover a security issue in Finbot, please report it responsibly.

### How to Report

**Email:** jeremyjdawson@gmail.com
**Subject:** `[SECURITY] Brief description of the issue`

Please include:
- Description of the issue
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

### What to Expect

- **Acknowledgment:** Within 48 hours
- **Initial Assessment:** Within 7 days
- **Resolution Timeline:** Varies by severity

### Scope

Issues we address:
- Dependency CVEs in third-party packages
- API key exposure risks
- Data handling issues
- Code safety concerns
- Unsafe deserialization

### Out of Scope

The following are NOT in scope:
- Financial advice or investment outcomes (see DISCLAIMER.md)
- Theoretical financial risks
- Data accuracy issues (this is research software)
- Missing features or functionality

### Disclosure Policy

- Please do not publicly disclose the issue until we've addressed it
- We will credit you in release notes unless you prefer anonymity
- We aim to release fixes within 30 days for high-severity issues

## Best Practices

When using Finbot:

1. **API Keys:** Store API keys in environment variables or `.env` files
2. **Data Sources:** Validate data from external sources
3. **Dependencies:** Keep dependencies updated with `uv sync`
4. **Sandboxing:** Run backtests in isolated environments
5. **Code Review:** Review custom strategies before deployment

Thank you for helping keep Finbot secure!
