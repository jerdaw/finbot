#!/bin/bash
# Docker Security Scan Script
# Runs Trivy security scanner on finbot Docker image
# Usage: ./scripts/run_docker_security_scan.sh [tag]

set -e

TAG="${1:-latest}"
IMAGE_NAME="finbot:${TAG}"
TIMESTAMP=$(date +%Y-%m-%d)
REPORT_DIR="docs/security"
BASELINE_FILE="${REPORT_DIR}/baseline-scan-${TIMESTAMP}.txt"
JSON_FILE="${REPORT_DIR}/trivy-report-${TIMESTAMP}.json"
SARIF_FILE="${REPORT_DIR}/trivy-results-${TIMESTAMP}.sarif"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Finbot Docker Security Scanner ===${NC}"
echo -e "Image: ${IMAGE_NAME}"
echo -e "Date: ${TIMESTAMP}"
echo ""

# Create report directory if it doesn't exist
mkdir -p "${REPORT_DIR}"

# Step 1: Build Docker image
echo -e "${BLUE}Step 1: Building Docker image...${NC}"
docker build -t "${IMAGE_NAME}" .
echo -e "${GREEN}✓ Image built successfully${NC}"
echo ""

# Step 2: Scan Dockerfile configuration
echo -e "${BLUE}Step 2: Scanning Dockerfile configuration...${NC}"
docker run --rm -v "$(pwd):/app" aquasec/trivy config /app/Dockerfile
echo -e "${GREEN}✓ Dockerfile scan complete${NC}"
echo ""

# Step 3: Scan image for vulnerabilities (table format)
echo -e "${BLUE}Step 3: Scanning image for vulnerabilities (table format)...${NC}"
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image --severity CRITICAL,HIGH,MEDIUM,LOW \
  "${IMAGE_NAME}" | tee "${BASELINE_FILE}"
echo -e "${GREEN}✓ Image scan complete${NC}"
echo -e "Report saved to: ${BASELINE_FILE}"
echo ""

# Step 4: Generate JSON report
echo -e "${BLUE}Step 4: Generating JSON report...${NC}"
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image --format json --output /dev/stdout \
  "${IMAGE_NAME}" > "${JSON_FILE}"
echo -e "${GREEN}✓ JSON report generated${NC}"
echo -e "Report saved to: ${JSON_FILE}"
echo ""

# Step 5: Generate SARIF report (for GitHub Security)
echo -e "${BLUE}Step 5: Generating SARIF report...${NC}"
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image --format sarif --output /dev/stdout \
  "${IMAGE_NAME}" > "${SARIF_FILE}"
echo -e "${GREEN}✓ SARIF report generated${NC}"
echo -e "Report saved to: ${SARIF_FILE}"
echo ""

# Step 6: Summary statistics
echo -e "${BLUE}Step 6: Generating summary...${NC}"
CRITICAL_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length' "${JSON_FILE}")
HIGH_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="HIGH")] | length' "${JSON_FILE}")
MEDIUM_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="MEDIUM")] | length' "${JSON_FILE}")
LOW_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="LOW")] | length' "${JSON_FILE}")
TOTAL_COUNT=$((CRITICAL_COUNT + HIGH_COUNT + MEDIUM_COUNT + LOW_COUNT))

echo ""
echo -e "${BLUE}=== Vulnerability Summary ===${NC}"
echo -e "Total vulnerabilities: ${TOTAL_COUNT}"
echo -e "${RED}  CRITICAL: ${CRITICAL_COUNT}${NC}"
echo -e "${YELLOW}  HIGH:     ${HIGH_COUNT}${NC}"
echo -e "${YELLOW}  MEDIUM:   ${MEDIUM_COUNT}${NC}"
echo -e "  LOW:      ${LOW_COUNT}"
echo ""

# Step 7: Check if build should fail
if [ "${CRITICAL_COUNT}" -gt 0 ] || [ "${HIGH_COUNT}" -gt 0 ]; then
    echo -e "${RED}❌ Build FAILED: CRITICAL or HIGH vulnerabilities detected${NC}"
    echo -e "Review the report and remediate before deploying:"
    echo -e "  ${BASELINE_FILE}"
    exit 1
else
    echo -e "${GREEN}✅ Build PASSED: No CRITICAL or HIGH vulnerabilities detected${NC}"
    if [ "${MEDIUM_COUNT}" -gt 0 ] || [ "${LOW_COUNT}" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Warning: MEDIUM or LOW vulnerabilities detected${NC}"
        echo -e "Consider reviewing these for hardening purposes."
    fi
fi

echo ""
echo -e "${BLUE}=== Reports Generated ===${NC}"
echo -e "  Table:  ${BASELINE_FILE}"
echo -e "  JSON:   ${JSON_FILE}"
echo -e "  SARIF:  ${SARIF_FILE}"
echo ""
echo -e "${GREEN}Scan complete!${NC}"
