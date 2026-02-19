#!/usr/bin/env bash
# Generate changelog from git history using git-changelog
#
# Usage:
#   ./scripts/generate_changelog.sh                  # Generate full changelog
#   ./scripts/generate_changelog.sh v1.0.0..         # Generate since v1.0.0
#   ./scripts/generate_changelog.sh --help           # Show help

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
OUTPUT_FILE="CHANGELOG_GENERATED.md"
FILTER=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "Generate changelog from git history using git-changelog"
            echo ""
            echo "Usage:"
            echo "  $0 [options] [filter]"
            echo ""
            echo "Options:"
            echo "  -o, --output FILE    Output file (default: CHANGELOG_GENERATED.md)"
            echo "  -h, --help           Show this help message"
            echo ""
            echo "Filter:"
            echo "  Git revision range (e.g., v1.0.0.. or HEAD~10..)"
            echo ""
            echo "Examples:"
            echo "  $0                   # Generate full changelog"
            echo "  $0 v1.0.0..          # Generate since v1.0.0"
            echo "  $0 -o CHANGES.md     # Output to CHANGES.md"
            exit 0
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            FILTER="$1"
            shift
            ;;
    esac
done

echo -e "${GREEN}Generating changelog from git history...${NC}"

# Build command
CMD="uv run git-changelog --config-file .git-changelog.toml --output $OUTPUT_FILE"

if [[ -n "$FILTER" ]]; then
    CMD="$CMD --filter-commits $FILTER"
    echo -e "${YELLOW}Using filter: $FILTER${NC}"
fi

# Run git-changelog
eval "$CMD"

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✓ Changelog generated to $OUTPUT_FILE${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Review the generated changelog: less $OUTPUT_FILE"
    echo "2. Manually merge relevant sections into CHANGELOG.md"
    echo "3. Update release notes as needed"
    echo ""
    echo -e "${YELLOW}Note:${NC}"
    echo "- git-changelog only recognizes conventional commit formats"
    echo "- Current commits without conventional prefixes will be omitted"
    echo "- Consider using conventional commits going forward (already configured)"
    echo "- See CONTRIBUTING.md for conventional commit guidelines"
else
    echo -e "${RED}✗ Changelog generation failed${NC}"
    exit 1
fi
