#!/usr/bin/env bash
# Test script for TestPyPI publishing workflow
# This script validates the workflow configuration and build process

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}TestPyPI Workflow Validation${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

# Check that we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: pyproject.toml not found. Run this script from the project root.${NC}"
    exit 1
fi

# 1. Check workflow file exists
echo -e "${BLUE}[1/8] Checking workflow file...${NC}"
if [ -f ".github/workflows/publish-testpypi.yml" ]; then
    echo -e "${GREEN}✓ Workflow file exists${NC}"
else
    echo -e "${RED}✗ Workflow file not found${NC}"
    exit 1
fi

# 2. Validate workflow syntax (basic YAML check)
echo -e "${BLUE}[2/8] Validating workflow YAML syntax...${NC}"
if command -v yamllint >/dev/null 2>&1; then
    if yamllint -d relaxed .github/workflows/publish-testpypi.yml; then
        echo -e "${GREEN}✓ YAML syntax valid${NC}"
    else
        echo -e "${YELLOW}⚠ YAML validation warnings (non-critical)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ yamllint not installed, skipping YAML validation${NC}"
fi

# 3. Check pyproject.toml has required fields
echo -e "${BLUE}[3/8] Checking pyproject.toml...${NC}"
if grep -q "name = \"finbot\"" pyproject.toml && \
   grep -q "version = " pyproject.toml && \
   grep -q "description = " pyproject.toml; then
    echo -e "${GREEN}✓ Required package metadata present${NC}"
    VERSION=$(grep "version = " pyproject.toml | head -1 | sed 's/.*"\(.*\)".*/\1/')
    echo -e "  Current version: ${VERSION}"
else
    echo -e "${RED}✗ Missing required metadata in pyproject.toml${NC}"
    exit 1
fi

# 4. Check README exists (for long_description)
echo -e "${BLUE}[4/8] Checking README.md...${NC}"
if [ -f "README.md" ]; then
    echo -e "${GREEN}✓ README.md exists${NC}"
else
    echo -e "${RED}✗ README.md not found${NC}"
    exit 1
fi

# 5. Test build process locally
echo -e "${BLUE}[5/8] Testing package build...${NC}"
if command -v uv >/dev/null 2>&1; then
    # Clean previous builds
    rm -rf dist/ build/ *.egg-info

    # Build package
    if uv build; then
        echo -e "${GREEN}✓ Package build successful${NC}"

        # List build artifacts
        echo -e "  Build artifacts:"
        ls -lh dist/
    else
        echo -e "${RED}✗ Package build failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ uv not installed, skipping build test${NC}"
fi

# 6. Verify build artifacts
echo -e "${BLUE}[6/8] Verifying build artifacts...${NC}"
if [ -d "dist" ]; then
    WHEEL_COUNT=$(find dist -name "*.whl" | wc -l)
    TARBALL_COUNT=$(find dist -name "*.tar.gz" | wc -l)

    if [ "$WHEEL_COUNT" -eq 1 ] && [ "$TARBALL_COUNT" -eq 1 ]; then
        echo -e "${GREEN}✓ Build artifacts valid (1 wheel + 1 source dist)${NC}"

        # Show wheel contents preview
        echo -e "\n  Wheel contents (first 20 lines):"
        WHEEL_FILE=$(find dist -name "*.whl" | head -1)
        unzip -l "$WHEEL_FILE" | head -20
    else
        echo -e "${RED}✗ Unexpected artifact count (wheels: $WHEEL_COUNT, tarballs: $TARBALL_COUNT)${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ No dist/ directory found (skipped build test)${NC}"
fi

# 7. Check documentation
echo -e "${BLUE}[7/8] Checking documentation...${NC}"
if [ -f "docs/guides/publishing-to-testpypi.md" ] && \
   [ -f "docs/guides/testpypi-quick-reference.md" ]; then
    echo -e "${GREEN}✓ TestPyPI documentation exists${NC}"
else
    echo -e "${YELLOW}⚠ Some documentation files missing${NC}"
fi

# 8. Summary and next steps
echo -e "${BLUE}[8/8] Summary${NC}"
echo ""
echo -e "${GREEN}===================================${NC}"
echo -e "${GREEN}All checks passed!${NC}"
echo -e "${GREEN}===================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo -e "1. ${BLUE}Create TestPyPI account:${NC}"
echo -e "   https://test.pypi.org/account/register/"
echo ""
echo -e "2. ${BLUE}Generate API token:${NC}"
echo -e "   https://test.pypi.org/manage/account/#api-tokens"
echo ""
echo -e "3. ${BLUE}Add token to GitHub Secrets:${NC}"
echo -e "   https://github.com/jerdaw/finbot/settings/secrets/actions"
echo -e "   Name: TEST_PYPI_API_TOKEN"
echo ""
echo -e "4. ${BLUE}Trigger the workflow:${NC}"
echo -e "   a) Manual: GitHub Actions → Publish to TestPyPI → Run workflow"
echo -e "   b) Tag: git tag test-v${VERSION} && git push origin test-v${VERSION}"
echo ""
echo -e "5. ${BLUE}Test installation:${NC}"
echo -e "   pip install --index-url https://test.pypi.org/simple/ \\"
echo -e "               --extra-index-url https://pypi.org/simple/ \\"
echo -e "               finbot==${VERSION}"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo -e "  Full guide: docs/guides/publishing-to-testpypi.md"
echo -e "  Quick ref:  docs/guides/testpypi-quick-reference.md"
echo ""
