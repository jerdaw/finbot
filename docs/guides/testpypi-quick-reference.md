# TestPyPI Quick Reference

Quick commands and workflows for publishing to TestPyPI.

## One-Time Setup

```bash
# 1. Create TestPyPI account
# → Visit: https://test.pypi.org/account/register/

# 2. Enable 2FA
# → Account Settings → Two-factor authentication

# 3. Generate API token
# → Account Settings → API tokens → Add API token
# → Name: finbot-github-actions
# → Scope: Entire account (initially)

# 4. Add token to GitHub Secrets
# → GitHub repo → Settings → Secrets → Actions
# → Name: TEST_PYPI_API_TOKEN
# → Value: pypi-XXXXXXXXXXXXXXXX
```

## Publishing via GitHub Actions (Recommended)

### Manual Trigger

```bash
# Go to GitHub Actions → Publish to TestPyPI → Run workflow
```

### Tag Trigger

```bash
# Create and push test tag
git tag test-v1.0.0
git push origin test-v1.0.0
```

## Publishing Locally

```bash
# Build package
uv build

# Publish to TestPyPI
uv publish \
  --publish-url https://test.pypi.org/legacy/ \
  --token pypi-YOUR_TOKEN_HERE
```

## Testing Installation

```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            finbot==1.0.0

# Verify installation
finbot --version
finbot status

# Test import
python -c "from finbot.config import settings; print(settings.project_name)"
```

## Version Bumping

```bash
# Edit version in pyproject.toml
vim pyproject.toml  # Change version = "1.0.0" to "1.0.1"

# Commit and tag
git add pyproject.toml
git commit -m "Bump version to 1.0.1"
git tag test-v1.0.1
git push origin main test-v1.0.1
```

## Common Version Formats

```toml
# Development version
version = "1.0.0.dev1"

# Release candidate
version = "1.0.0rc1"

# Production version
version = "1.0.0"
```

## Verification Checklist

After publishing, verify:

- [ ] Package appears at https://test.pypi.org/project/finbot/
- [ ] Version number is correct
- [ ] README renders properly
- [ ] Project links work (Homepage, Repository, Issues)
- [ ] Installation succeeds with `pip install`
- [ ] CLI command works: `finbot --version`
- [ ] Basic imports work: `from finbot.config import settings`

## Troubleshooting

| Error | Solution |
|-------|----------|
| Invalid authentication | Check `TEST_PYPI_API_TOKEN` secret is set correctly |
| File already exists | Increment version in `pyproject.toml` |
| Dependencies not found | Use `--extra-index-url https://pypi.org/simple/` |
| Package not found | Wait 1-2 minutes for indexing |

## URLs

- **TestPyPI**: https://test.pypi.org
- **Project page**: https://test.pypi.org/project/finbot/
- **Account settings**: https://test.pypi.org/manage/account/
- **API tokens**: https://test.pypi.org/manage/account/#api-tokens

## Next Steps

After successful TestPyPI testing → Publish to production PyPI (see separate guide)
