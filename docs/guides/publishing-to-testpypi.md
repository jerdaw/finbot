# Publishing to TestPyPI

This guide explains how to publish the finbot package to TestPyPI for testing before releasing to the production PyPI.

## Overview

TestPyPI is a separate instance of the Python Package Index (PyPI) designed for testing and experimentation. It allows you to:

- Test the package upload process without affecting the production PyPI
- Verify package metadata, dependencies, and installation
- Practice the release workflow in a safe environment
- Test package installation from a public repository

## Prerequisites

### 1. Create a TestPyPI Account

1. Visit [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)
2. Fill out the registration form with:
   - Username
   - Email address
   - Password
3. Verify your email address by clicking the link sent to your inbox
4. Enable two-factor authentication (2FA) for security:
   - Go to Account Settings → Two-factor authentication
   - Follow the instructions to set up 2FA with an authenticator app

### 2. Generate an API Token

API tokens are the recommended authentication method for uploading packages.

1. Log in to [https://test.pypi.org](https://test.pypi.org)
2. Go to Account Settings → API tokens
3. Click "Add API token"
4. Configure the token:
   - **Token name**: `finbot-github-actions` (or any descriptive name)
   - **Scope**: Select "Entire account" for initial testing
     - After first successful upload, create a project-specific token for better security
5. Click "Create token"
6. **IMPORTANT**: Copy the token immediately - it will only be shown once
   - Format: `pypi-AgEIcHlwaS5vcmc...` (starts with `pypi-`)
   - Store securely (you'll add it to GitHub Secrets next)

### 3. Add Token to GitHub Secrets

1. Go to your GitHub repository: [https://github.com/jerdaw/finbot](https://github.com/jerdaw/finbot)
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Create the secret:
   - **Name**: `TEST_PYPI_API_TOKEN`
   - **Value**: Paste the entire token (including the `pypi-` prefix)
5. Click "Add secret"

## Publishing Methods

### Method 1: Manual Workflow Dispatch (Recommended for Testing)

Trigger the workflow manually from the GitHub Actions UI.

**Steps:**

1. Go to Actions → Publish to TestPyPI
2. Click "Run workflow"
3. Optional: Enter a custom version (or leave empty to use version from `pyproject.toml`)
4. Click "Run workflow"
5. Monitor the workflow progress
6. Once complete, verify the package at [https://test.pypi.org/project/finbot/](https://test.pypi.org/project/finbot/)

**When to use:**
- Testing the publishing workflow
- Publishing a development version
- Manual quality checks before production release

### Method 2: Git Tag Push (Automated)

Trigger publishing automatically by pushing a tag with the `test-v*` prefix.

**Steps:**

```bash
# Create a test tag
git tag test-v1.0.0

# Push the tag to trigger the workflow
git push origin test-v1.0.0

# Or push all tags
git push --tags
```

**When to use:**
- Automated testing in CI/CD pipeline
- Consistent versioning with git tags
- Integration testing with version control

### Method 3: Local Publishing (For Development)

Publish directly from your local machine using `uv`.

**Steps:**

```bash
# Ensure you have the latest dependencies
uv sync

# Build the package
uv build

# Publish to TestPyPI
uv publish \
  --publish-url https://test.pypi.org/legacy/ \
  --token pypi-YOUR_TOKEN_HERE
```

**When to use:**
- Quick local testing
- Debugging build or upload issues
- Not recommended for production releases

## Testing the Published Package

### 1. Install from TestPyPI

After publishing, test the installation:

```bash
# Create a fresh virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from TestPyPI
# Note: --extra-index-url is needed because finbot's dependencies are on PyPI
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            finbot==1.0.0

# Verify installation
finbot --version
finbot status

# Test basic functionality
python -c "from finbot.config import settings; print(settings.project_name)"
```

### 2. Verify Package Metadata

Check the TestPyPI project page:

1. Visit [https://test.pypi.org/project/finbot/](https://test.pypi.org/project/finbot/)
2. Verify:
   - ✓ Version number matches expected version
   - ✓ Description and README render correctly
   - ✓ Project links (Homepage, Repository, Issues) work
   - ✓ Classifiers are accurate
   - ✓ License is correct
   - ✓ Dependencies are listed

### 3. Test Package Contents

Inspect the built package to ensure all necessary files are included:

```bash
# Download the wheel file
pip download --index-url https://test.pypi.org/simple/ \
              --no-deps \
              finbot==1.0.0

# Inspect wheel contents
unzip -l finbot-1.0.0-py3-none-any.whl

# Or inspect the source distribution
tar -tzf finbot-1.0.0.tar.gz
```

### 4. Run Tests

Test the installed package:

```bash
# Clone the repository for tests
git clone https://github.com/jerdaw/finbot.git
cd finbot

# Run tests against installed package
pytest tests/ -v
```

## Workflow Details

### Build Process

The workflow performs the following steps:

1. **Checkout**: Fetches the latest code from the repository
2. **Setup**: Installs `uv` and Python 3.13
3. **Dependencies**: Syncs all project dependencies
4. **Build**: Creates both wheel (`.whl`) and source distribution (`.tar.gz`)
5. **Verify**: Lists build artifacts for inspection
6. **Publish**: Uploads to TestPyPI using the API token
7. **Archive**: Stores build artifacts for 7 days

### Build Artifacts

The workflow produces:

- **Wheel**: `finbot-1.0.0-py3-none-any.whl` (binary distribution)
- **Source**: `finbot-1.0.0.tar.gz` (source distribution)

Both are uploaded to TestPyPI and available as GitHub workflow artifacts.

### Environment Variables

The workflow uses:

- `UV_PUBLISH_TOKEN`: TestPyPI API token (from GitHub Secrets)
- `--publish-url`: TestPyPI upload endpoint

## Versioning Strategy

### Current Version

The package version is defined in `pyproject.toml`:

```toml
[project]
name = "finbot"
version = "1.0.0"
```

### Version Management

**For TestPyPI testing:**

1. **Development versions**: Use `.devN` suffix
   ```toml
   version = "1.0.0.dev1"
   ```

2. **Release candidates**: Use `rcN` suffix
   ```toml
   version = "1.0.0rc1"
   ```

3. **Test tags**: Use `test-v` prefix
   ```bash
   git tag test-v1.0.0rc1
   ```

**Version bumping:**

```bash
# Edit pyproject.toml version manually, then:
git add pyproject.toml
git commit -m "Bump version to 1.0.1"
git tag test-v1.0.1
git push origin main test-v1.0.1
```

## Troubleshooting

### Common Issues

#### 1. "Invalid or non-existent authentication information"

**Cause**: Incorrect or missing API token

**Solution**:
- Verify the GitHub Secret `TEST_PYPI_API_TOKEN` is set correctly
- Ensure the token starts with `pypi-`
- Generate a new token if needed
- Check token scope includes upload permissions

#### 2. "File already exists"

**Cause**: Version already published to TestPyPI

**Solution**:
- TestPyPI does not allow re-uploading the same version
- Increment the version in `pyproject.toml`
- Use development versions (e.g., `1.0.0.dev2`) for testing

#### 3. "Metadata verification failed"

**Cause**: Invalid package metadata

**Solution**:
- Check `pyproject.toml` for syntax errors
- Validate required fields: name, version, description
- Ensure README.md exists and is valid Markdown
- Run `uv build` locally to test

#### 4. "Dependencies cannot be installed"

**Cause**: Dependencies not available on TestPyPI

**Solution**:
- Use `--extra-index-url https://pypi.org/simple/` when installing
- All finbot dependencies are on production PyPI, not TestPyPI
- This is normal behavior for TestPyPI testing

#### 5. "Package not found on TestPyPI"

**Cause**: Upload may still be processing

**Solution**:
- Wait 1-2 minutes for TestPyPI indexing
- Refresh the project page
- Check workflow logs for upload errors

## Security Best Practices

### API Token Security

- ✓ Never commit tokens to git
- ✓ Use GitHub Secrets for token storage
- ✓ Create project-scoped tokens (not account-wide) after first upload
- ✓ Rotate tokens periodically (every 90 days)
- ✓ Revoke unused or compromised tokens immediately

### Token Scope

**Initial upload** (first time):
- Use "Entire account" scope to create the project

**Subsequent uploads** (recommended):
1. After first successful upload, create a new token
2. Select scope: "Project: finbot"
3. Replace `TEST_PYPI_API_TOKEN` with the new project-scoped token

### 2FA Requirement

TestPyPI requires two-factor authentication for account security. Enable it in Account Settings before generating tokens.

## Differences Between TestPyPI and PyPI

| Feature | TestPyPI | PyPI |
|---------|----------|------|
| Purpose | Testing | Production |
| URL | test.pypi.org | pypi.org |
| Persistence | Packages may be deleted | Packages are permanent |
| Version reuse | Limited (cleared periodically) | Never allowed |
| Dependencies | Separate index | Main Python package index |
| Rate limits | More lenient | Stricter |
| Account | Separate from PyPI | Separate from TestPyPI |

## Next Steps

After successful TestPyPI testing:

1. ✓ Verify package installation and functionality
2. ✓ Review metadata and documentation on TestPyPI
3. ✓ Test all declared entry points (`finbot` CLI)
4. ✓ Validate dependencies install correctly
5. → Proceed to production PyPI release (see separate guide)

## Resources

- **TestPyPI**: [https://test.pypi.org](https://test.pypi.org)
- **TestPyPI Help**: [https://test.pypi.org/help/](https://test.pypi.org/help/)
- **Python Packaging Guide**: [https://packaging.python.org](https://packaging.python.org)
- **uv Documentation**: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
- **GitHub Actions**: [https://docs.github.com/en/actions](https://docs.github.com/en/actions)

## Support

For issues or questions:

- **Repository Issues**: [https://github.com/jerdaw/finbot/issues](https://github.com/jerdaw/finbot/issues)
- **TestPyPI Support**: [https://test.pypi.org/help/#support](https://test.pypi.org/help/#support)
- **Python Packaging Discourse**: [https://discuss.python.org/c/packaging/14](https://discuss.python.org/c/packaging/14)
