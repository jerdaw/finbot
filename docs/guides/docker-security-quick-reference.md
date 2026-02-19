# Docker Security Scanning - Quick Reference

## Quick Commands

```bash
# Full automated scan with reports
./scripts/run_docker_security_scan.sh

# Manual scan (if Docker available)
docker build -t finbot:test .
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image finbot:test

# Scan specific severity levels only
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image --severity CRITICAL,HIGH finbot:test
```

## CI Integration

Security scan runs automatically on every push/PR to main. Check:
- Actions tab → docker-security-scan job
- Security tab → Code scanning alerts

## Severity Quick Guide

| Level | Action | Example |
|-------|--------|---------|
| CRITICAL | Fix immediately, blocks deployment | Remote code execution, SQL injection |
| HIGH | Fix in next release | Authentication bypass, data exposure |
| MEDIUM | Fix when convenient | Information disclosure, DoS |
| LOW | Review for hardening | Minor configuration issues |

## Common Tasks

### Update Base Image

```bash
# 1. Check latest tag
docker pull python:3.13-slim

# 2. Update Dockerfile
FROM python:3.13.2-slim AS builder

# 3. Test
docker build -t finbot:test .
./scripts/run_docker_security_scan.sh test

# 4. Commit
git commit -am "Update base image to 3.13.2-slim"
```

### Update Python Dependencies

```bash
# 1. Update lock file
uv lock --upgrade

# 2. Rebuild and test
docker build -t finbot:test .
./scripts/run_docker_security_scan.sh test

# 3. Commit
git commit -am "Update dependencies for security patches"
```

### Ignore False Positive

```bash
# 1. Create .trivyignore
echo "CVE-2024-12345" > .trivyignore

# 2. Add comment
echo "# CVE-2024-12345: False positive, code path not exposed" >> .trivyignore

# 3. Commit with explanation
git add .trivyignore
git commit -m "Ignore CVE-2024-12345 (false positive)"
```

### View CI Reports

```bash
# Download latest scan results
gh run list --workflow=ci.yml --limit 1
gh run download <run-id> -n docker-security-report

# Extract and view
tar -xzf docker-security-report.tar.gz
cat trivy-report.json | jq '.Results[].Vulnerabilities[]'
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Database download error" | `rm -rf ~/.cache/trivy` |
| CI timeout | Increase timeout in workflow |
| Too many false positives | Use `.trivyignore` file |
| SARIF upload failed | Check file size < 10MB |

## Key Files

```
.github/workflows/ci.yml          # CI configuration
Dockerfile                        # Container definition
.trivyignore.example              # Ignore pattern template
scripts/run_docker_security_scan.sh  # Manual scan script
docs/guides/docker-security-scanning.md  # Full documentation
docs/security/                    # Scan reports directory
```

## Resources

- [Full Documentation](docker-security-scanning.md)
- [Trivy Docs](https://aquasecurity.github.io/trivy/)
- [NVD Database](https://nvd.nist.gov/)
- [GitHub Security Tab](https://github.com/jer/finbot/security)

---

For detailed information, see [Docker Security Scanning Guide](docker-security-scanning.md).
