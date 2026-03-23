#!/bin/bash
# Docker Security Scan Script
# Runs Trivy security scanner on Finbot CLI and API Docker images
# Usage: ./scripts/run_docker_security_scan.sh [tag]

set -euo pipefail

TAG="${1:-latest}"
TIMESTAMP=$(date +%Y-%m-%d)
REPORT_DIR="docs/security"
CLI_IMAGE_NAME="finbot-cli:${TAG}"
API_IMAGE_NAME="finbot-api:${TAG}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Finbot Docker Security Scanner ===${NC}"
echo -e "CLI image: ${CLI_IMAGE_NAME}"
echo -e "API image: ${API_IMAGE_NAME}"
echo -e "Date: ${TIMESTAMP}"
echo ""

mkdir -p "${REPORT_DIR}"

scan_image() {
    local image_label="$1"
    local image_name="$2"
    local dockerfile_path="$3"
    local baseline_file="${REPORT_DIR}/baseline-scan-${image_label}-${TIMESTAMP}.txt"
    local json_file="${REPORT_DIR}/trivy-report-${image_label}-${TIMESTAMP}.json"
    local sarif_file="${REPORT_DIR}/trivy-results-${image_label}-${TIMESTAMP}.sarif"

    echo -e "${BLUE}Building ${image_label} image...${NC}"
    docker build -t "${image_name}" -f "${dockerfile_path}" .
    echo -e "${GREEN}✓ ${image_label} image built successfully${NC}"
    echo ""

    echo -e "${BLUE}Scanning ${dockerfile_path} configuration...${NC}"
    docker run --rm -v "$(pwd):/app" aquasec/trivy config "/app/${dockerfile_path}"
    echo -e "${GREEN}✓ ${image_label} Dockerfile scan complete${NC}"
    echo ""

    echo -e "${BLUE}Scanning ${image_label} image for vulnerabilities (table format)...${NC}"
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
      aquasec/trivy image --severity CRITICAL,HIGH,MEDIUM,LOW \
      "${image_name}" | tee "${baseline_file}"
    echo -e "${GREEN}✓ ${image_label} image scan complete${NC}"
    echo -e "Report saved to: ${baseline_file}"
    echo ""

    echo -e "${BLUE}Generating ${image_label} JSON report...${NC}"
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
      aquasec/trivy image --format json --output /dev/stdout \
      "${image_name}" > "${json_file}"
    echo -e "${GREEN}✓ ${image_label} JSON report generated${NC}"
    echo -e "Report saved to: ${json_file}"
    echo ""

    echo -e "${BLUE}Generating ${image_label} SARIF report...${NC}"
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
      aquasec/trivy image --format sarif --output /dev/stdout \
      "${image_name}" > "${sarif_file}"
    echo -e "${GREEN}✓ ${image_label} SARIF report generated${NC}"
    echo -e "Report saved to: ${sarif_file}"
    echo ""
}

scan_image "cli" "${CLI_IMAGE_NAME}" "Dockerfile"
scan_image "api" "${API_IMAGE_NAME}" "web/Dockerfile.backend"

echo -e "${BLUE}Generating combined summary...${NC}"
CLI_CRITICAL_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length' "${REPORT_DIR}/trivy-report-cli-${TIMESTAMP}.json")
CLI_HIGH_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="HIGH")] | length' "${REPORT_DIR}/trivy-report-cli-${TIMESTAMP}.json")
CLI_MEDIUM_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="MEDIUM")] | length' "${REPORT_DIR}/trivy-report-cli-${TIMESTAMP}.json")
CLI_LOW_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="LOW")] | length' "${REPORT_DIR}/trivy-report-cli-${TIMESTAMP}.json")
API_CRITICAL_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length' "${REPORT_DIR}/trivy-report-api-${TIMESTAMP}.json")
API_HIGH_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="HIGH")] | length' "${REPORT_DIR}/trivy-report-api-${TIMESTAMP}.json")
API_MEDIUM_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="MEDIUM")] | length' "${REPORT_DIR}/trivy-report-api-${TIMESTAMP}.json")
API_LOW_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="LOW")] | length' "${REPORT_DIR}/trivy-report-api-${TIMESTAMP}.json")

CRITICAL_COUNT=$((CLI_CRITICAL_COUNT + API_CRITICAL_COUNT))
HIGH_COUNT=$((CLI_HIGH_COUNT + API_HIGH_COUNT))
MEDIUM_COUNT=$((CLI_MEDIUM_COUNT + API_MEDIUM_COUNT))
LOW_COUNT=$((CLI_LOW_COUNT + API_LOW_COUNT))
TOTAL_COUNT=$((CRITICAL_COUNT + HIGH_COUNT + MEDIUM_COUNT + LOW_COUNT))

echo ""
echo -e "${BLUE}=== Vulnerability Summary ===${NC}"
echo -e "Total vulnerabilities: ${TOTAL_COUNT}"
echo -e "${RED}  CRITICAL: ${CRITICAL_COUNT}${NC}"
echo -e "${YELLOW}  HIGH:     ${HIGH_COUNT}${NC}"
echo -e "${YELLOW}  MEDIUM:   ${MEDIUM_COUNT}${NC}"
echo -e "  LOW:      ${LOW_COUNT}"
echo ""
echo -e "By image:"
echo -e "  CLI -> CRITICAL: ${CLI_CRITICAL_COUNT}, HIGH: ${CLI_HIGH_COUNT}, MEDIUM: ${CLI_MEDIUM_COUNT}, LOW: ${CLI_LOW_COUNT}"
echo -e "  API -> CRITICAL: ${API_CRITICAL_COUNT}, HIGH: ${API_HIGH_COUNT}, MEDIUM: ${API_MEDIUM_COUNT}, LOW: ${API_LOW_COUNT}"
echo ""

if [ "${CRITICAL_COUNT}" -gt 0 ] || [ "${HIGH_COUNT}" -gt 0 ]; then
    echo -e "${RED}❌ Build FAILED: CRITICAL or HIGH vulnerabilities detected${NC}"
    echo -e "Review the report and remediate before deploying:"
    echo -e "  ${REPORT_DIR}/baseline-scan-cli-${TIMESTAMP}.txt"
    echo -e "  ${REPORT_DIR}/baseline-scan-api-${TIMESTAMP}.txt"
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
echo -e "  CLI Table:  ${REPORT_DIR}/baseline-scan-cli-${TIMESTAMP}.txt"
echo -e "  CLI JSON:   ${REPORT_DIR}/trivy-report-cli-${TIMESTAMP}.json"
echo -e "  CLI SARIF:  ${REPORT_DIR}/trivy-results-cli-${TIMESTAMP}.sarif"
echo -e "  API Table:  ${REPORT_DIR}/baseline-scan-api-${TIMESTAMP}.txt"
echo -e "  API JSON:   ${REPORT_DIR}/trivy-report-api-${TIMESTAMP}.json"
echo -e "  API SARIF:  ${REPORT_DIR}/trivy-results-api-${TIMESTAMP}.sarif"
echo ""
echo -e "${GREEN}Scan complete!${NC}"
