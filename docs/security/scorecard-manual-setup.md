# OpenSSF Scorecard Manual Setup Guide

**For Repository Owner**
**Estimated Time:** 10-15 minutes

## Overview

The OpenSSF Scorecard workflow has been created and will run automatically. However, some security improvements require manual configuration in GitHub's web interface. This guide walks you through the required and recommended manual steps.

## Required: Enable Branch Protection

Branch protection is the most important manual step. It prevents accidental or malicious direct pushes to the main branch and enforces code review.

### Step-by-Step Instructions

1. **Navigate to Repository Settings**
   - Go to https://github.com/jerdaw/finbot
   - Click "Settings" tab (top right)
   - If you don't see Settings, you need admin permissions

2. **Access Branch Protection Rules**
   - In left sidebar, click "Branches" (under "Code and automation")
   - Find "Branch protection rules" section
   - Click "Add branch protection rule" or "Add rule"

3. **Configure Branch Name Pattern**
   - Branch name pattern: `main`
   - This will protect your main/default branch

4. **Enable Required Settings** (Recommended)

   ✅ **Require a pull request before merging**
   - Check this box
   - Under it, check:
     - "Require approvals" (minimum 1 approval)
     - "Dismiss stale pull request approvals when new commits are pushed"

   ✅ **Require status checks to pass before merging**
   - Check this box
   - Search for and select status checks:
     - `test (3.13)` (from CI workflow)
     - Any other critical checks you want to require
   - Check "Require branches to be up to date before merging"

   ✅ **Require conversation resolution before merging**
   - Check this box (ensures all review comments are addressed)

   ⚠️ **Do not allow bypassing the above settings** (Optional but Recommended)
   - If checked, even admins must follow the rules
   - Recommended for maximum security
   - Can be unchecked if you occasionally need to make urgent hotfixes

5. **Additional Recommended Settings**

   ✅ **Require linear history**
   - Prevents merge commits, keeps history clean

   ✅ **Require deployments to succeed before merging** (Optional)
   - Only if you have deployment workflows
   - Can skip for now

   ✅ **Lock branch** (Not Recommended)
   - Makes branch read-only
   - Only use for archived branches

6. **Save Changes**
   - Scroll to bottom
   - Click "Create" or "Save changes"
   - Branch protection is now active!

### Verification

After enabling branch protection:

1. Try to push directly to main (should fail):
   ```bash
   # This should be rejected
   git push origin main
   ```

   You should see an error like:
   ```
   remote: error: GH006: Protected branch update failed
   ```

2. Create a pull request instead:
   ```bash
   git checkout -b feature-branch
   # Make changes
   git commit -m "Test change"
   git push origin feature-branch
   # Create PR via GitHub web interface
   ```

3. PR should show required checks and approvals

### What This Improves

Enabling branch protection improves your OpenSSF Scorecard in these checks:
- **Branch-Protection:** 0/10 → 8-10/10 ⬆️
- **Code-Review:** May improve to 10/10 (if all commits via PRs)
- **Overall Score:** Estimated +1.0 to +1.5 points

## Optional: Enable CodeQL (SAST)

CodeQL is GitHub's semantic code analysis tool. It finds security vulnerabilities automatically.

### Step-by-Step Instructions

1. **Navigate to Security Tab**
   - Go to https://github.com/jerdaw/finbot
   - Click "Security" tab
   - Click "Code scanning" in left sidebar

2. **Set up CodeQL**
   - Click "Set up code scanning" or "Explore workflows"
   - Find "CodeQL Analysis"
   - Click "Set up this workflow"

3. **Review Workflow File**
   - GitHub generates `.github/workflows/codeql.yml`
   - Default settings are usually fine for Python projects
   - Adjust schedule if desired (default: weekly)

4. **Commit Workflow**
   - Click "Start commit"
   - Commit directly to main or create PR
   - CodeQL will run on next push

### What This Improves

Enabling CodeQL improves your OpenSSF Scorecard in these checks:
- **SAST:** 5-7/10 → 10/10 ⬆️
- **Overall Score:** Estimated +0.5 to +0.8 points

## Optional: Pin GitHub Actions to SHA Hashes

For maximum supply chain security, pin GitHub Actions to specific SHA commits instead of version tags.

### Why This Matters

Version tags (like `@v4`) can be moved by repository owners, potentially introducing malicious code. SHA hashes are immutable.

### How to Pin Actions

**Before (version tag):**
```yaml
- uses: actions/checkout@v4
```

**After (SHA hash with comment):**
```yaml
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
```

### Finding SHA Hashes

1. Go to the action's GitHub repository
2. Find the specific release (e.g., v4.1.1)
3. Copy the commit SHA
4. Add as comment for human readability

### Automated Tool

Use [pin-github-action](https://github.com/mheap/pin-github-action):
```bash
npx pin-github-action .github/workflows/*.yml
```

### What This Improves

Pinning actions improves your OpenSSF Scorecard:
- **Pinned-Dependencies:** 7-9/10 → 10/10 ⬆️
- **Overall Score:** Estimated +0.2 to +0.5 points

## Monitoring Scorecard Results

### When Will Results Appear?

- **First Run:** After workflow runs for the first time (weekly schedule or manual trigger)
- **Publishing Delay:** Results take 24-48 hours to appear on OpenSSF API
- **Badge Update:** Badge updates automatically when results publish

### How to Check Results

1. **GitHub Actions Tab**
   - Go to https://github.com/jerdaw/finbot/actions
   - Find "OpenSSF Scorecard" workflow
   - Click latest run to see results

2. **OpenSSF Public Viewer**
   - Visit https://securityscorecards.dev/viewer/?uri=github.com/jerdaw/finbot
   - Shows detailed breakdown of all checks
   - Updates weekly

3. **GitHub Security Tab**
   - Go to https://github.com/jerdaw/finbot/security
   - Click "Code scanning"
   - View Scorecard SARIF results

### Manually Triggering Scorecard

Don't want to wait for the weekly schedule?

1. Go to https://github.com/jerdaw/finbot/actions
2. Click "OpenSSF Scorecard" workflow
3. Click "Run workflow" dropdown
4. Click "Run workflow" button
5. Wait a few minutes for results

## Troubleshooting

### Badge Not Showing

**Problem:** OpenSSF Scorecard badge shows "unknown" or doesn't load

**Solution:**
- Wait 24-48 hours after first workflow run
- Verify workflow ran successfully in Actions tab
- Check that `publish_results: true` is set in workflow
- Ensure repository is public

### Branch Protection Not Working

**Problem:** Can still push directly to main

**Solution:**
- Verify rule is saved and enabled
- Check rule applies to correct branch (`main`)
- Ensure you're not an admin with bypass enabled
- Try from a different branch/PR

### Low Score

**Problem:** Score is lower than expected

**Solution:**
- Review detailed results on OpenSSF viewer
- See [docs/security/openssf-scorecard.md](openssf-scorecard.md) for improvement tips
- Some checks may not apply to your project (documented)
- Focus on critical checks first (Branch-Protection, Code-Review, Security-Policy)

## Summary Checklist

### Required (10 minutes)
- [ ] Enable branch protection on main branch
  - [ ] Require PR reviews before merging
  - [ ] Require status checks to pass
  - [ ] Require conversation resolution
- [ ] Verify branch protection works (test push fails)

### Recommended (30 minutes)
- [ ] Enable CodeQL code scanning
- [ ] Pin GitHub Actions to SHA hashes
- [ ] Review first scorecard results
- [ ] Document any checks that don't apply

### Monitoring (Ongoing)
- [ ] Check scorecard results weekly
- [ ] Address new security findings promptly
- [ ] Update documentation as needed

## Expected Results

After completing required and recommended steps:

| Before | After |
| --- | --- |
| ~6.5-7.5 / 10 | ~8.0-8.5 / 10 |

**Major Improvements:**
- Branch-Protection: 0 → 8-10
- Code-Review: Variable → 10
- SAST: 5-7 → 10
- Pinned-Dependencies: 7-9 → 10

## Questions?

- **Scorecard Issues:** https://github.com/ossf/scorecard/issues
- **Finbot Security:** See [SECURITY.md](../../SECURITY.md)
- **Documentation:** See [docs/security/openssf-scorecard.md](openssf-scorecard.md)

---

**Last Updated:** 2026-02-17
