# OpenSSF Scorecard

**Status:** Active
**Last Updated:** 2026-02-17
**Workflow:** `.github/workflows/scorecard.yml`
**Public Results:** [OpenSSF Scorecard Viewer](https://securityscorecards.dev/viewer/?uri=github.com/jerdaw/finbot)

## Overview

Finbot uses the [OpenSSF Scorecard](https://github.com/ossf/scorecard) to automatically assess security best practices. The scorecard runs weekly via GitHub Actions and publishes results to the OpenSSF public API.

**What is OpenSSF Scorecard?**
The Open Source Security Foundation (OpenSSF) Scorecard is an automated security tool that checks for common security risks in open source projects. It evaluates 18 different security practices and provides a score from 0-10 for each check.

## Scorecard Badge

[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/jerdaw/finbot/badge)](https://securityscorecards.dev/viewer/?uri=github.com/jerdaw/finbot)

The badge above shows the current overall security score. Click it to see detailed results for each check.

## How It Works

1. **Automated Scanning:** GitHub Action runs weekly (Sundays at 00:00 UTC)
2. **Security Checks:** Scorecard evaluates 18 security practices
3. **Results Publishing:** Results published to OpenSSF public API
4. **Badge Update:** Badge automatically updates with latest score
5. **SARIF Upload:** Results uploaded to GitHub Security tab for review

## Scorecard Checks Explained

### Critical Checks (High Priority)

#### 1. Branch-Protection (Weight: High)
**What it checks:** Branch protection rules on default branch

**Current Status:** ⚠️ Requires Manual Setup

**What we do:**
- Branch protection must be enabled manually in GitHub repository settings
- Recommended settings:
  - ✅ Require pull request reviews before merging
  - ✅ Require status checks to pass (CI tests)
  - ✅ Require branches to be up to date
  - ✅ Include administrators (optional)

**How to enable:**
1. Go to GitHub repository Settings > Branches
2. Click "Add branch protection rule"
3. Branch name pattern: `main`
4. Enable recommended settings above
5. Save changes

**Why it matters:** Prevents direct pushes to main branch, enforces code review, reduces accidental security issues.

#### 2. CI-Tests (Weight: High)
**What it checks:** Whether the project runs tests in CI

**Current Status:** ✅ Passing

**What we do:**
- GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push
- Runs 750+ unit and integration tests
- Runs linting (ruff) and formatting checks
- Runs type checking (mypy)

**Why it matters:** Automated testing catches bugs before they reach production.

#### 3. Code-Review (Weight: High)
**What it checks:** Whether code changes are reviewed before merging

**Current Status:** ⚠️ Depends on Workflow

**What we do:**
- If branch protection is enabled with PR reviews: ✅ Pass
- If direct pushes to main allowed: ❌ Fail

**Why it matters:** Code review catches security issues and bugs that automated tools miss.

#### 4. Maintained (Weight: High)
**What it checks:** Project shows signs of active maintenance

**Current Status:** ✅ Passing

**What we do:**
- Regular commits (within last 90 days)
- Active issue responses
- Recent releases

**Why it matters:** Unmaintained projects accumulate security vulnerabilities.

#### 5. Security-Policy (Weight: High)
**What it checks:** Project has a security policy (SECURITY.md)

**Current Status:** ✅ Passing

**What we do:**
- SECURITY.md file in repository root
- Defines supported versions
- Explains how to report vulnerabilities
- Sets response time expectations

**Why it matters:** Clear security policy helps researchers report issues responsibly.

#### 6. Vulnerabilities (Weight: High)
**What it checks:** Known vulnerabilities in dependencies

**Current Status:** ✅ Passing

**What we do:**
- Dependabot scans dependencies weekly
- GitHub Security Advisories enabled
- Vulnerabilities addressed promptly

**Why it matters:** Known vulnerabilities are easy targets for attackers.

### Important Checks (Medium Priority)

#### 7. Dependency-Update-Tool (Weight: Medium)
**What it checks:** Automated dependency updates enabled

**Current Status:** ✅ Passing

**What we do:**
- Dependabot enabled (`.github/dependabot.yml`)
- Weekly scans for dependency updates
- Automated PRs for security updates

**Why it matters:** Keeps dependencies current with security patches.

#### 8. License (Weight: Medium)
**What it checks:** Project has an OSI-approved license

**Current Status:** ✅ Passing

**What we do:**
- MIT License file in repository root
- License automatically detected by GitHub

**Why it matters:** Clear licensing protects users and contributors.

#### 9. Pinned-Dependencies (Weight: Medium)
**What it checks:** Dependencies pinned to specific versions/SHAs

**Current Status:** ⚠️ Partial

**What we do:**
- Python dependencies pinned in `pyproject.toml`
- GitHub Actions use version tags (`@v4`) instead of SHA hashes

**Improvement needed:**
- Pin GitHub Actions to SHA hashes for supply chain security
- Example: `uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1`

**Why it matters:** Prevents supply chain attacks through dependency confusion.

#### 10. SAST (Weight: Medium)
**What it checks:** Static Application Security Testing tools in use

**Current Status:** ⚠️ Partial

**What we do:**
- Ruff linter catches common security issues
- Mypy type checker finds type-related bugs
- Bandit security scanner (manual, not in CI)

**Improvement options:**
- Enable CodeQL via GitHub Security tab
- Add Bandit to CI pipeline
- Add Semgrep for advanced SAST

**Why it matters:** Automated security analysis catches vulnerabilities early.

#### 11. Token-Permissions (Weight: Medium)
**What it checks:** GitHub Actions workflows use minimal permissions

**Current Status:** ✅ Passing

**What we do:**
- All workflows declare explicit permissions
- Use `permissions: read-all` by default
- Elevate only when needed (e.g., `security-events: write`)

**Why it matters:** Limits damage if workflow is compromised.

### Optional Checks (Low Priority)

#### 12. CII-Best-Practices (Weight: Low)
**What it checks:** Project registered with CII Best Practices program

**Current Status:** ❌ Not Registered (Optional)

**What we do:**
- Not registered with CII Best Practices
- May register in future if project grows

**Why it matters:** Third-party validation of best practices, but optional for smaller projects.

#### 13. Contributors (Weight: Low)
**What it checks:** Project has multiple contributors

**Current Status:** ✅ Passing (Single Contributor)

**What we do:**
- Currently single maintainer
- Open to contributions (CONTRIBUTING.md exists)

**Why it matters:** Multiple contributors reduce single-point-of-failure risk. For single-maintainer projects, this is not a concern.

#### 14. Dangerous-Workflow (Weight: Low)
**What it checks:** No dangerous GitHub Actions patterns

**Current Status:** ✅ Passing

**What we do:**
- No `pull_request_target` triggers
- No uncontrolled script execution
- No secrets exposure

**Why it matters:** Prevents workflow-based attacks.

#### 15. Fuzzing (Weight: Low)
**What it checks:** Project uses fuzz testing

**Current Status:** ❌ Not Applicable

**What we do:**
- No fuzzing (not applicable for financial analysis tool)
- Fuzzing more relevant for parsers, compilers, network protocols

**Why it matters:** Fuzzing finds edge cases in input handling. Not critical for this project type.

#### 16. Signed-Releases (Weight: Low)
**What it checks:** Releases are cryptographically signed

**Current Status:** ❌ Not Implemented (Optional)

**What we do:**
- GitHub Releases exist but not GPG-signed
- May add signing in future

**Why it matters:** Prevents release tampering. Nice-to-have but not critical for open source Python package.

#### 17. Binary-Artifacts (Weight: Low)
**What it checks:** No checked-in binary files

**Current Status:** ✅ Passing

**What we do:**
- No binaries in version control
- All data files are text (parquet, CSV) or excluded (.gitignore)

**Why it matters:** Binary files can hide malware.

#### 18. Webhooks (Weight: Low)
**What it checks:** Webhooks use HTTPS and secrets

**Current Status:** ✅ Passing

**What we do:**
- No webhooks configured
- If added, would use HTTPS with secrets

**Why it matters:** Prevents webhook hijacking.

## Current Score Prediction

Based on current implementation, expected score:

| Category | Checks Passing | Checks Partial | Checks Failing |
| --- | --- | --- | --- |
| **Critical** | 4 | 2 | 0 |
| **Important** | 4 | 2 | 0 |
| **Optional** | 3 | 0 | 5 |
| **Total** | **11** | **4** | **5** |

**Estimated Score:** 6.5-7.5 / 10

## Improvement Roadmap

### Short Term (1-2 months)
- [ ] Enable branch protection on main branch (user action)
- [ ] Pin GitHub Actions to SHA hashes
- [ ] Add CodeQL to CI (optional)

### Medium Term (3-6 months)
- [ ] Add Bandit security scanner to CI
- [ ] Improve code review process documentation
- [ ] Consider GPG signing releases

### Long Term (6-12 months)
- [ ] Register with CII Best Practices (if project grows)
- [ ] Add multiple maintainers/contributors
- [ ] Implement advanced SAST (Semgrep, etc.)

## How to Improve Your Score

### For Repository Owners

**Quick Wins (15 minutes):**
1. Enable branch protection:
   - Settings > Branches > Add rule
   - Require PR reviews before merging
   - Require status checks to pass

**Medium Effort (1-2 hours):**
1. Pin GitHub Actions to SHA hashes:
   - Replace `@v4` with `@<sha> # v4`
   - See [dependency pinning guide](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

2. Enable CodeQL:
   - Security tab > Enable CodeQL
   - Automatically scans for vulnerabilities

**Longer Term:**
1. Add security scanner to CI (Bandit, Semgrep)
2. Implement GPG release signing
3. Register with CII Best Practices

### For Contributors

- Follow secure coding practices
- Report security issues via SECURITY.md process
- Review security documentation before contributing

## Frequently Asked Questions

**Q: Why is the score not 10/10?**
A: Some checks require manual setup (branch protection) or are optional for this project type (fuzzing, signed releases). We prioritize security practices that provide the most value for this project.

**Q: How often does the score update?**
A: The scorecard runs weekly (Sundays at 00:00 UTC). Results appear within 24-48 hours.

**Q: Are the results public?**
A: Yes, scorecard results are published to the OpenSSF public API. This transparency helps users assess the project's security posture.

**Q: What if a check doesn't apply to this project?**
A: Some checks (like fuzzing) are not relevant for all project types. We document why certain checks don't apply and focus on meaningful security improvements.

**Q: Can I run the scorecard locally?**
A: Yes, install the [scorecard CLI](https://github.com/ossf/scorecard#using-the-cli) and run:
```bash
scorecard --repo=github.com/jerdaw/finbot
```

## Resources

- [OpenSSF Scorecard Repository](https://github.com/ossf/scorecard)
- [Scorecard Checks Documentation](https://github.com/ossf/scorecard/blob/main/docs/checks.md)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [CII Best Practices](https://bestpractices.coreinfrastructure.org/)

## Reporting Security Issues

If you find a security issue in Finbot, please report it via the process described in [SECURITY.md](../../SECURITY.md).

For issues with the scorecard itself, please report to the [OpenSSF Scorecard project](https://github.com/ossf/scorecard/issues).

---

**Last Scorecard Run:** Check [OpenSSF Viewer](https://securityscorecards.dev/viewer/?uri=github.com/jerdaw/finbot) for latest results.
