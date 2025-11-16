#!/bin/bash
# Verify signatures and provenance for Coordination Trilemma artifacts
# Requires: cosign, docker

set -e

REPO="realnedsanders/Coordination-Trilemma"
IMAGE="ghcr.io/${REPO}/latex:latest"

echo "🔐 Coordination Trilemma Security Verification"
echo "================================================"
echo ""

# Check if cosign is installed
if ! command -v cosign &> /dev/null; then
    echo "❌ cosign not found. Please install it:"
    echo "   macOS: brew install cosign"
    echo "   Linux: https://docs.sigstore.dev/cosign/installation/"
    exit 1
fi

# Verify Docker image signature
echo "1️⃣  Verifying Docker image signature..."
echo "   Image: ${IMAGE}"
echo ""

if cosign verify \
    --certificate-identity-regexp="^https://github.com/${REPO}" \
    --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
    "${IMAGE}" > /dev/null 2>&1; then
    echo "   ✅ Docker image signature verified!"
else
    echo "   ❌ Docker image signature verification failed!"
    exit 1
fi
echo ""

# Verify SLSA provenance attestation
echo "2️⃣  Verifying SLSA provenance attestation..."
if cosign verify-attestation \
    --certificate-identity-regexp="^https://github.com/${REPO}" \
    --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
    --type slsaprovenance \
    "${IMAGE}" > /dev/null 2>&1; then
    echo "   ✅ SLSA provenance attestation verified!"
else
    echo "   ❌ SLSA provenance verification failed!"
    exit 1
fi
echo ""

# Verify SBOM attestation
echo "3️⃣  Verifying SBOM attestation..."
if cosign verify-attestation \
    --certificate-identity-regexp="^https://github.com/${REPO}" \
    --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
    --type spdx \
    "${IMAGE}" > /dev/null 2>&1; then
    echo "   ✅ SBOM attestation verified!"
else
    echo "   ⚠️  SBOM attestation verification failed (may not be available yet)"
fi
echo ""

# Display image metadata
echo "4️⃣  Image metadata (OCI labels):"
docker inspect "${IMAGE}" | jq -r '.[0].Config.Labels | to_entries[] | select(.key | startswith("org.opencontainers.image")) | "   \(.key): \(.value)"'
echo ""

# PDF verification (if files exist)
if [ -f "main.pdf" ] && [ -f "main.pdf.cosign.bundle" ]; then
    echo "5️⃣  Verifying PDF signature..."
    if cosign verify-blob --bundle main.pdf.cosign.bundle \
        --certificate-identity-regexp="^https://github.com/${REPO}" \
        --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
        main.pdf > /dev/null 2>&1; then
        echo "   ✅ PDF signature verified!"
    else
        echo "   ❌ PDF signature verification failed!"
        exit 1
    fi
    echo ""
fi

echo "================================================"
echo "✅ All verification checks passed!"
echo ""
echo "SLSA Build Level: 3"
echo "Trust chain: GitHub OIDC → Fulcio → Rekor"
echo ""
echo "For more details, see SECURITY.md"
