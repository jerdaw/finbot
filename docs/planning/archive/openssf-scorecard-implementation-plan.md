# OpenSSF Scorecard Implementation Plan

**Item:** Priority 5, Item 43
**Status:** ✅ Complete
**Date Started:** 2026-02-17
**Date Completed:** 2026-02-17
**Completion Summary:** `docs/planning/openssf-scorecard-completion-summary.md`

## Overview

Implement OpenSSF (Open Source Security Foundation) Scorecard to validate security and best practices. The Scorecard provides automated security checks for open source projects and generates a public badge showing the project's security posture.

## What is OpenSSF Scorecard?

OpenSSF Scorecard is a tool that:
- Automatically checks security best practices for open source projects
- Provides a score (0-10) across multiple security checks
- Generates a badge showing the overall score
- Runs via GitHub Actions on a schedule
- Publishes results to the OpenSSF API

**Scorecard Checks (18 total):**
1. Branch-Protection
2. CI-Tests
3. CII-Best-Practices
4. Code-Review
5. Contributors
6. Dangerous-Workflow
7. Dependency-Update-Tool
8. Fuzzing
9. License
10. Maintained
11. Pinned-Dependencies
12. SAST
13. Security-Policy
14. Signed-Releases
15. Token-Permissions
16. Vulnerabilities
17. Webhooks
18. Binary-Artifacts

## Prerequisites Check

Before implementing, verify these prerequisites are met:
- ✅ LICENSE file exists (Item 1)
- ✅ SECURITY.md exists (Item 4)
- ✅ CODE_OF_CONDUCT.md exists (Item 5)
- ✅ CONTRIBUTING.md exists (Item 6)
- ✅ GitHub Actions CI exists (.github/workflows/ci.yml)
- ✅ Dependabot enabled (Priority 0, Item 6)

## Implementation Phases

### Phase 1: Add OpenSSF Scorecard GitHub Action ✅
1. Create `.github/workflows/scorecard.yml`
2. Configure to run weekly (Sundays at 00:00 UTC)
3. Add GITHUB_TOKEN permissions
4. Enable results publishing to OpenSSF API
5. Upload results as artifacts

### Phase 2: Configure Branch Protection (Manual)
**User Action Required:**
1. Go to GitHub repository Settings > Branches
2. Add branch protection rule for `main`:
   - Require pull request reviews before merging
   - Require status checks to pass before merging
   - Include administrators (optional but recommended)

This is required for Branch-Protection check to pass.

### Phase 3: Address Scorecard Findings
1. Review initial scorecard results
2. Identify low-hanging fruit improvements
3. Address critical security issues
4. Document items that cannot be addressed (and why)

### Phase 4: Add Scorecard Badge to README
1. Add OpenSSF Scorecard badge to README.md
2. Link badge to OpenSSF results page
3. Add brief explanation of what the badge represents

### Phase 5: Documentation
1. Document scorecard setup in docs/security/
2. Create docs/security/openssf-scorecard.md explaining:
   - What each check means
   - Current status of each check
   - Roadmap for improvements
   - Why certain checks may not apply

### Phase 6: Verification
1. Wait for first scorecard run (weekly schedule)
2. Review results and score
3. Verify badge displays correctly
4. Document any issues

## Expected Scorecard Results (Predictions)

Based on current repository state, expected check results:

| Check | Expected Score | Reason |
| --- | --- | --- |
| Branch-Protection | 0/10 | No branch protection rules (requires manual setup) |
| CI-Tests | 10/10 | GitHub Actions CI runs tests |
| CII-Best-Practices | 0/10 | Not registered with CII (optional) |
| Code-Review | 10/10 | All commits via PRs (if enforced) or 0/10 (if direct pushes) |
| Contributors | 10/10 | Single contributor (low risk) |
| Dangerous-Workflow | 10/10 | No dangerous patterns detected |
| Dependency-Update-Tool | 10/10 | Dependabot enabled |
| Fuzzing | 0/10 | No fuzzing (not applicable for this project type) |
| License | 10/10 | LICENSE file exists |
| Maintained | 10/10 | Recent commits |
| Pinned-Dependencies | 7-9/10 | GitHub Actions use @v* tags (should pin to SHA) |
| SAST | 5-7/10 | Ruff linting but no dedicated SAST tool |
| Security-Policy | 10/10 | SECURITY.md exists |
| Signed-Releases | 0/10 | Releases not GPG signed (optional) |
| Token-Permissions | 10/10 | GitHub Actions use minimal permissions |
| Vulnerabilities | 10/10 | No known vulnerabilities |
| Webhooks | 10/10 | No insecure webhooks |
| Binary-Artifacts | 10/10 | No checked-in binaries |

**Estimated Initial Score:** 6.5-7.5 / 10

## Critical vs Optional Checks

### Critical (Should Address):
- Branch-Protection: Enable branch protection (manual)
- Pinned-Dependencies: Pin GitHub Actions to SHA (automated)
- SAST: Consider adding CodeQL or similar

### Optional (May Skip):
- CII-Best-Practices: Registration not required
- Fuzzing: Not applicable for financial analysis tool
- Signed-Releases: Nice-to-have but not critical
- Code-Review: Depends on workflow (single maintainer)

## Implementation Steps

### Step 1: Create Scorecard Workflow
Create `.github/workflows/scorecard.yml` with:
- Weekly schedule (cron: '0 0 * * 0')
- Publish to OpenSSF API
- Upload SARIF results
- Minimal token permissions

### Step 2: User Manual Actions
**User must manually:**
1. Enable branch protection on main branch
2. Review first scorecard results
3. Optionally: Enable CodeQL (via GitHub Security tab)

### Step 3: Address Findings
Based on first run:
- Pin GitHub Actions to SHA hashes
- Add any missing security policies
- Document why certain checks don't apply

### Step 4: Add Badge
Add to README.md:
```markdown
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/jerdaw/finbot/badge)](https://securityscorecards.dev/viewer/?uri=github.com/jerdaw/finbot)
```

## Success Criteria

- [ ] Scorecard workflow created and runs successfully
- [ ] Initial score > 6.0 / 10
- [ ] Badge added to README
- [ ] Documentation complete
- [ ] Critical security issues addressed
- [ ] User knows how to enable branch protection

## Estimated Time

- Phase 1: 30 minutes (automated workflow)
- Phase 2: 10 minutes (user manual setup)
- Phase 3: 1-2 hours (address findings)
- Phase 4: 10 minutes (add badge)
- Phase 5: 1-2 hours (documentation)
- Phase 6: 15 minutes (verification)

**Total:** 3-5 hours

## Resources

- [OpenSSF Scorecard](https://github.com/ossf/scorecard)
- [Scorecard Checks](https://github.com/ossf/scorecard/blob/main/docs/checks.md)
- [GitHub Action](https://github.com/ossf/scorecard-action)
- [Best Practices Guide](https://bestpractices.coreinfrastructure.org/)

## Notes

- Scorecard results are public (published to OpenSSF API)
- First run may take 24-48 hours to appear on API
- Score updates weekly
- Some checks may not be relevant for all projects
- Document limitations transparently
