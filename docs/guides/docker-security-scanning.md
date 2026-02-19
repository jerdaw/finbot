# Docker Security Scanning Guide

## Overview

This guide documents the automated Docker container security scanning process for Finbot. We use [Trivy](https://trivy.dev/) by Aqua Security to scan both the Dockerfile configuration and the built Docker images for vulnerabilities in base images, OS packages, and Python dependencies.

## Scanning Process

### Automated CI Scanning

The `docker-security-scan` job in `.github/workflows/ci.yml` runs on every push and pull request to the main branch. It performs:

1. **Dockerfile Configuration Scan**: Checks Dockerfile for misconfigurations and security issues
2. **Image Vulnerability Scan**: Scans the built image for CVEs in:
   - Base image (python:3.13-slim)
   - OS packages (Debian)
   - Python packages (from uv.lock)
3. **SARIF Upload**: Sends results to GitHub Security tab for tracking
4. **Artifact Upload**: Stores detailed reports as CI artifacts

### Scan Execution Steps

```yaml
# 1. Build the Docker image
docker build -t finbot:${{ github.sha }} .

# 2. Scan Dockerfile configuration
trivy config Dockerfile

# 3. Scan built image for vulnerabilities
trivy image finbot:${{ github.sha }}

# 4. Upload results to GitHub Security
# 5. Generate and store detailed reports
```

### Severity Levels

Trivy categorizes vulnerabilities into severity levels:

| Severity | Description | CI Behavior |
|----------|-------------|-------------|
| **CRITICAL** | Immediate security risk requiring urgent action | ❌ Fails CI build |
| **HIGH** | Significant security risk requiring prompt action | ❌ Fails CI build |
| **MEDIUM** | Moderate security risk requiring attention | ⚠️ Warning (does not fail) |
| **LOW** | Minor security risk or hardening opportunity | ⚠️ Warning (does not fail) |

**Note**: The CI is configured to fail on CRITICAL and HIGH vulnerabilities (`exit-code: '1'`), but continues on MEDIUM and LOW to avoid blocking development on minor issues.

### Ignore Unfixed Vulnerabilities

The scan is configured with `ignore-unfixed: true`, which means:
- Only vulnerabilities with available fixes are reported
- Known issues without patches are logged but don't fail the build
- This reduces noise while maintaining security awareness

## Understanding Scan Results

### Viewing Results

**In GitHub Actions:**
1. Go to Actions tab → Select workflow run → Click "docker-security-scan" job
2. Expand scan steps to see table output
3. Download "docker-security-report" artifact for detailed JSON/SARIF reports

**In GitHub Security:**
1. Go to Security tab → Code scanning alerts → Trivy
2. View detailed CVE information, affected packages, and remediation advice

**Locally:**
```bash
# Scan Dockerfile configuration
docker run --rm -v $(pwd):/app aquasec/trivy config /app/Dockerfile

# Build and scan image
docker build -t finbot:local .
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image finbot:local

# Generate JSON report
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image -f json -o trivy-report.json finbot:local
```

### Report Format

**Table Format (Console Output)**:
```
finbot:sha256 (debian 13.0)
================================
Total: 5 (CRITICAL: 1, HIGH: 2, MEDIUM: 2, LOW: 0)

┌───────────────┬────────────────┬──────────┬─────────────────┬───────────────┬───────────────────────┐
│   Library     │ Vulnerability  │ Severity │ Installed Ver.  │ Fixed Version │        Title          │
├───────────────┼────────────────┼──────────┼─────────────────┼───────────────┼───────────────────────┤
│ libssl3       │ CVE-2024-12345 │ CRITICAL │ 3.0.11-1        │ 3.0.12-1      │ OpenSSL buffer overflow│
└───────────────┴────────────────┴──────────┴─────────────────┴───────────────┴───────────────────────┘
```

**SARIF Format (GitHub Security)**:
- Integrated into GitHub Security tab
- Provides detailed CVE descriptions
- Links to vulnerability databases (NVD, GitHub Advisory)
- Shows affected file paths and remediation guidance

**JSON Format (Detailed Analysis)**:
- Complete vulnerability metadata
- CVSS scores and vectors
- Detailed descriptions
- References to security advisories

## Addressing Vulnerabilities

### Step-by-Step Remediation

#### 1. Review Scan Results

Check the CI job output or GitHub Security tab for findings:
```bash
# Download artifact from CI
gh run download <run-id> -n docker-security-report

# View JSON report locally
cat trivy-report.json | jq '.Results[] | select(.Vulnerabilities)'
```

#### 2. Identify Vulnerability Source

Vulnerabilities come from three sources:

**A. Base Image (python:3.13-slim)**
- CVEs in the Python base image or Debian OS packages
- Solution: Update to newer base image tag

**B. OS Packages**
- Debian packages installed in the container
- Solution: Update Dockerfile to install patched versions

**C. Python Dependencies**
- Packages from `pyproject.toml` and `uv.lock`
- Solution: Update Python dependencies

#### 3. Update Base Image

If vulnerability is in the base image:

```dockerfile
# Current
FROM python:3.13-slim AS builder

# Updated (use latest patch)
FROM python:3.13.2-slim AS builder

# Or try newer minor version
FROM python:3.14-slim AS builder
```

Check [Python Docker Hub](https://hub.docker.com/_/python) for latest secure tags.

#### 4. Update Python Dependencies

If vulnerability is in Python packages:

```bash
# Update all dependencies
uv lock --upgrade

# Update specific package
uv lock --upgrade-package <package-name>

# Review changes
git diff uv.lock
```

Then rebuild the Docker image and rescan:
```bash
docker build -t finbot:patched .
trivy image finbot:patched
```

#### 5. Update OS Packages (Advanced)

If vulnerability is in Debian packages and not fixed by base image update, you may need to:

```dockerfile
# Add explicit package update in Dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libssl3=3.0.12-1 \
    && rm -rf /var/lib/apt/lists/*
```

**Warning**: This approach should be used sparingly and only when:
- Base image hasn't released a fix yet
- Vulnerability is CRITICAL or HIGH severity
- You understand the dependency implications

#### 6. Document Exception (If Needed)

For unfixable vulnerabilities or false positives, create a `.trivyignore` file:

```bash
# .trivyignore
# CVE-2024-12345: False positive - code path not exposed
CVE-2024-12345

# CVE-2024-67890: Waiting for upstream fix, low exploitability
CVE-2024-67890
```

Add rationale in this documentation or a separate security log.

### Testing Changes

After remediation:

```bash
# Rebuild image
docker build -t finbot:fixed .

# Run Trivy scan
trivy image finbot:fixed

# Verify no CRITICAL/HIGH vulnerabilities
trivy image --severity CRITICAL,HIGH finbot:fixed

# Test image functionality
docker run --rm finbot:fixed --help
docker run --rm finbot:fixed status
```

## Base Image Update Strategy

### Current Base Image

- **Image**: `python:3.13-slim`
- **OS**: Debian 13 (Trixie/Sid)
- **Python**: 3.13.x
- **Size**: ~140 MB

### Update Frequency

**Recommended schedule**:
- **Weekly**: Check for new patch versions (3.13.1 → 3.13.2)
- **Monthly**: Review security advisories and force update if needed
- **Immediate**: For CRITICAL vulnerabilities with available fixes

**Automated checks**:
```bash
# Check current image digest
docker pull python:3.13-slim
docker inspect python:3.13-slim | jq '.[0].Id'

# Compare with tracked digest in CI
```

### Update Process

1. **Test new image locally**:
   ```bash
   # Update Dockerfile
   FROM python:3.13.2-slim AS builder

   # Build and test
   docker build -t finbot:test .
   docker run --rm finbot:test status
   uv run pytest tests/
   ```

2. **Run security scan**:
   ```bash
   trivy image finbot:test
   ```

3. **Update Dockerfile**:
   ```bash
   git checkout -b update-base-image
   # Edit Dockerfile
   git add Dockerfile
   git commit -m "Update Python base image to 3.13.2-slim for security patches"
   ```

4. **Create PR and verify CI**:
   - CI will run full security scan
   - Review GitHub Security tab for changes
   - Merge if all checks pass

### Alternative Base Images

If `python:3.13-slim` has persistent security issues, consider:

| Image | Pros | Cons |
|-------|------|------|
| `python:3.13-alpine` | Smaller size, musl libc (fewer CVEs) | Compatibility issues, slower builds |
| `python:3.13-bookworm` | Debian stable (slower updates) | Larger size, older packages |
| `gcr.io/distroless/python3` | Minimal attack surface | More complex build, limited tooling |

## Security Best Practices

### Implemented in Finbot

✅ **Multi-stage build**: Reduces final image size and attack surface
✅ **Non-root user**: Runs as `finbot:finbot` (UID/GID 1000)
✅ **Minimal base image**: Uses `-slim` variant
✅ **No cache in production**: `RUN rm -rf /var/lib/apt/lists/*`
✅ **Pinned dependencies**: `uv.lock` ensures reproducible builds
✅ **Separate data volume**: `/app/finbot/data` mounted externally

### Additional Recommendations

🔒 **Scan images before deployment**:
```bash
# In production pipeline
trivy image --severity CRITICAL,HIGH --exit-code 1 finbot:${VERSION}
```

🔒 **Sign and verify images**:
```bash
# Sign with cosign (future enhancement)
cosign sign finbot:${VERSION}
```

🔒 **Use specific tags, not `:latest`**:
```dockerfile
# Bad
FROM python:3.13-slim

# Good
FROM python:3.13.2-slim@sha256:abc123...
```

🔒 **Enable Docker Content Trust**:
```bash
export DOCKER_CONTENT_TRUST=1
```

🔒 **Regular dependency updates**:
```bash
# Monthly audit
uv lock --upgrade
trivy image finbot:dev
```

## CI Configuration Reference

### Job Configuration

```yaml
docker-security-scan:
  name: Docker Security Scan
  runs-on: ubuntu-latest

  steps:
    - name: Checkout code
      uses: actions/checkout@v6

    - name: Build Docker image
      run: docker build -t finbot:${{ github.sha }} .

    - name: Run Trivy scanner
      uses: aquasecurity/trivy-action@0.29.0
      with:
        image-ref: 'finbot:${{ github.sha }}'
        format: 'sarif'
        output: 'trivy-results.sarif'
        severity: 'CRITICAL,HIGH,MEDIUM,LOW'
        exit-code: '1'           # Fail on CRITICAL/HIGH
        ignore-unfixed: true     # Skip unfixable CVEs

    - name: Upload to GitHub Security
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: 'trivy-results.sarif'
```

### Configuration Options

| Option | Value | Description |
|--------|-------|-------------|
| `scan-type` | `config` / `image` | Scan Dockerfile or image |
| `format` | `table` / `json` / `sarif` | Output format |
| `severity` | `CRITICAL,HIGH,MEDIUM,LOW` | Severity levels to scan |
| `exit-code` | `0` / `1` | Fail build on findings |
| `ignore-unfixed` | `true` / `false` | Skip CVEs without fixes |
| `timeout` | `5m` | Scanner timeout |
| `cache-dir` | `.trivycache/` | Cache database location |

## Troubleshooting

### Common Issues

**Issue**: Scan fails with "database download error"
```bash
# Solution: Clear Trivy cache
rm -rf ~/.cache/trivy
```

**Issue**: Too many false positives
```bash
# Solution: Use .trivyignore file
echo "CVE-2024-12345" >> .trivyignore
```

**Issue**: CI timeout on scan
```yaml
# Solution: Increase timeout
with:
  timeout: '10m'
```

**Issue**: SARIF upload fails
```bash
# Solution: Check SARIF file size (max 10MB)
ls -lh trivy-results.sarif
```

### Debug Commands

```bash
# Run verbose scan
trivy image --debug finbot:latest

# Test specific vulnerability database
trivy image --skip-db-update finbot:latest

# Check Trivy version
trivy version

# Clear all caches
trivy clean --all
```

## Initial Security Report

### Baseline Scan (2026-02-17)

**Image**: `finbot:local` built from commit `d07c3e9`

**Base Image**:
- `python:3.13-slim`
- Debian 13 (Trixie/Sid)
- Last updated: 2026-02-XX

**Scan Summary**:
```bash
# Run scan to generate baseline
docker build -t finbot:baseline .
trivy image finbot:baseline > docs/security/baseline-scan-2026-02-17.txt
```

**Expected Results**:
- Python 3.13 is actively maintained (no major CVEs expected)
- Debian Trixie/Sid receives regular security updates
- Python dependencies managed via `uv.lock` (pinned versions)

**Next Actions**:
1. Review scan output in CI after first run
2. Document any CRITICAL/HIGH findings in this section
3. Create remediation plan for identified issues
4. Establish monthly review schedule

### Historical Findings

| Date | CVE | Severity | Package | Status |
|------|-----|----------|---------|--------|
| 2026-02-17 | N/A | N/A | N/A | Initial baseline scan |

_(Update this table as vulnerabilities are discovered and remediated)_

## References

### Tools

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Trivy GitHub Action](https://github.com/aquasecurity/trivy-action)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [NIST NVD](https://nvd.nist.gov/)

### Related Documentation

- `Dockerfile`: Multi-stage build configuration
- `.github/workflows/ci.yml`: CI pipeline with security scanning
- `docs/guides/pre-commit-hooks-usage.md`: Pre-commit security checks
- `pyproject.toml`: Python dependency specifications

### Security Contacts

- **Project Maintainer**: See `pyproject.toml` for contact information
- **Security Issues**: Report via GitHub Security Advisories
- **CVE Tracking**: GitHub Security tab → Code scanning alerts

---

**Last Updated**: 2026-02-17
**Document Version**: 1.0
**Reviewed By**: Initial creation
