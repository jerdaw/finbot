# TestPyPI Setup Instructions

Follow these steps to enable TestPyPI publishing for finbot.

## Step 1: Create TestPyPI Account

1. Visit https://test.pypi.org/account/register/
2. Fill out registration form:
   - Choose a username
   - Enter your email address
   - Create a strong password
3. Click "Create account"
4. Check your email and verify your address

## Step 2: Enable Two-Factor Authentication (Required)

1. Log in to https://test.pypi.org
2. Go to Account Settings → Two-factor authentication
3. Set up 2FA using one of these methods:
   - Authenticator app (recommended): Google Authenticator, Authy, 1Password, etc.
   - Security key (FIDO U2F)
4. Save your recovery codes in a secure location

## Step 3: Generate API Token

1. Go to https://test.pypi.org/manage/account/#api-tokens
2. Click "Add API token"
3. Configure the token:
   - **Token name**: `finbot-github-actions`
   - **Scope**: Select "Entire account" (for first-time setup)
4. Click "Create token"
5. **IMPORTANT**: Copy the token immediately
   - It starts with `pypi-`
   - Format: `pypi-AgEIcHlwaS5vcmc...`
   - It will only be shown once

## Step 4: Add Token to GitHub Secrets

1. Go to https://github.com/jerdaw/finbot/settings/secrets/actions
2. Click "New repository secret"
3. Configure the secret:
   - **Name**: `TEST_PYPI_API_TOKEN`
   - **Value**: Paste the entire token (including `pypi-` prefix)
4. Click "Add secret"

## Step 5: Verify Setup

Run the validation script to ensure everything is configured correctly:

```bash
./scripts/test_testpypi_workflow.sh
```

All checks should pass.

## Step 6: Test the Workflow

Try publishing to TestPyPI:

### Option A: Manual Trigger (Recommended for First Test)

1. Go to https://github.com/jerdaw/finbot/actions/workflows/publish-testpypi.yml
2. Click "Run workflow" button
3. Leave version empty (uses pyproject.toml version)
4. Click "Run workflow"
5. Monitor the workflow progress

### Option B: Tag-Based Trigger

```bash
# Create a test tag
git tag test-v1.0.0

# Push the tag
git push origin test-v1.0.0
```

## Step 7: Verify Publication

1. Check the workflow completed successfully in GitHub Actions
2. Visit https://test.pypi.org/project/finbot/
3. Verify the package appears with the correct version

## Step 8: Test Installation

```bash
# Create a test virtual environment
python -m venv test-env
source test-env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            finbot==1.0.0

# Test the installation
finbot --version
finbot status

# Clean up
deactivate
rm -rf test-env
```

## Troubleshooting

### "Invalid or non-existent authentication information"

- Verify `TEST_PYPI_API_TOKEN` is set correctly in GitHub Secrets
- Ensure the token includes the `pypi-` prefix
- Token may have expired - generate a new one

### "File already exists"

- You cannot re-upload the same version to TestPyPI
- Increment the version in `pyproject.toml`
- Use development versions for testing: `1.0.0.dev1`, `1.0.0.dev2`, etc.

### "Package not found on TestPyPI"

- Wait 1-2 minutes for indexing to complete
- Check the workflow logs for upload errors
- Verify the workflow completed successfully

### Workflow doesn't trigger

- Ensure the tag starts with `test-v` (e.g., `test-v1.0.0`)
- Check GitHub Actions is enabled for the repository
- Verify you have push permissions

## Security Best Practices

- Never commit API tokens to git
- Use project-scoped tokens after first upload (more secure than account-wide)
- Rotate tokens every 90 days
- Revoke unused tokens immediately
- Store recovery codes securely offline

## Next Steps

After successful TestPyPI setup and testing, you can:

1. Configure production PyPI publishing (separate guide)
2. Set up automated release workflows
3. Create project-scoped tokens (recommended for production)

## Resources

- TestPyPI Home: https://test.pypi.org
- TestPyPI Help: https://test.pypi.org/help/
- Full Publishing Guide: [publishing-to-testpypi.md](publishing-to-testpypi.md)
- Quick Reference: [testpypi-quick-reference.md](testpypi-quick-reference.md)
