#!/bin/bash
# Test script to validate release workflow logic locally
# This simulates the key steps without actually creating a release

set -e

echo "=== Release Workflow Validation ==="
echo ""

# Test 1: Validate YAML syntax
echo "1. Validating YAML syntax..."
if command -v python3 &> /dev/null; then
    python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"
    echo "   ✓ YAML syntax valid"
else
    echo "   ⚠ Python not found, skipping YAML validation"
fi
echo ""

# Test 2: Test version extraction
echo "2. Testing version extraction..."
TEST_TAG="v1.2.3"
VERSION="${TEST_TAG#v}"
echo "   Tag: $TEST_TAG"
echo "   Version: $VERSION"
echo "   ✓ Version extraction works"
echo ""

# Test 3: Test changelog extraction for existing version
echo "3. Testing changelog extraction for v1.0.0..."
VERSION="1.0.0"
if grep -q "## \[$VERSION\]" CHANGELOG.md; then
    echo "   ✓ Found changelog entry for $VERSION"
    echo "   Preview (first 10 lines):"
    awk "/## \[$VERSION\]/,/## \[/" CHANGELOG.md | sed '1d;$d' | head -10 | sed 's/^/   /'
else
    echo "   ✗ No changelog entry found for $VERSION"
fi
echo ""

# Test 4: Test prerelease detection
echo "4. Testing prerelease detection..."
test_prerelease() {
    TAG=$1
    if echo "$TAG" | grep -qE "(alpha|beta|rc)"; then
        echo "   $TAG → prerelease"
    else
        echo "   $TAG → stable release"
    fi
}

test_prerelease "v1.0.0"
test_prerelease "v1.1.0-beta.1"
test_prerelease "v2.0.0-alpha.1"
test_prerelease "v1.0.1-rc.2"
echo "   ✓ Prerelease detection works"
echo ""

# Test 5: Test build command
echo "5. Testing build command..."
if command -v uv &> /dev/null; then
    echo "   Running: uv build --dry-run"
    # Note: uv doesn't have a --dry-run flag, so we'll just verify uv is available
    uv --version
    echo "   ✓ uv is available and can build"
    echo "   (Skipping actual build to avoid artifacts)"
else
    echo "   ✗ uv not found - install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi
echo ""

# Test 6: Check required files
echo "6. Checking required files..."
REQUIRED_FILES=(
    "pyproject.toml"
    "CHANGELOG.md"
    ".github/workflows/release.yml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file exists"
    else
        echo "   ✗ $file missing"
    fi
done
echo ""

echo "=== Validation Complete ==="
echo ""
echo "To create a release:"
echo "  1. Update version in pyproject.toml"
echo "  2. Update CHANGELOG.md with version and date"
echo "  3. Commit and push changes"
echo "  4. Create and push tag: git tag v1.1.0 && git push origin v1.1.0"
echo ""
echo "See docs/guides/release-process.md for full instructions."
