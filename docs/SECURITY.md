# Security and Build Provenance

This document describes the security measures, build provenance, and verification procedures for the Coordination Trilemma project.

## SLSA Build Level

This project achieves **SLSA Build Level 3** with the following guarantees:

### SLSA Level 3 Requirements ✅

- **✅ Source integrity**: All source code is version-controlled in Git
- **✅ Build service**: GitHub Actions provides isolated build environments
- **✅ Build as code**: All builds defined in version-controlled workflows
- **✅ Provenance: Authenticated**: Cryptographically signed provenance attestations
- **✅ Provenance: Unforgeable**: Sigstore keyless signing with transparency logs
- **✅ Provenance: Complete**: Full build parameters and materials captured
- **✅ Hermetic**: Builds use containerized environments with pinned dependencies

## Artifacts and Signatures

### Docker Image: `ghcr.io/realnedsanders/coordination-trilemma/latex`

**Security Features:**
- ✅ Signed with Cosign (Sigstore keyless signing)
- ✅ SLSA Provenance attestation
- ✅ SBOM (Software Bill of Materials) attestation
- ✅ Trivy vulnerability scanning
- ✅ OCI labels with build metadata

**Verify the image signature:**
```bash
# Install cosign
brew install cosign  # macOS
# or
go install github.com/sigstore/cosign/v2/cmd/cosign@latest

# Verify signature
cosign verify \
  --certificate-identity-regexp="^https://github.com/realnedsanders/Coordination-Trilemma" \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
  ghcr.io/realnedsanders/coordination-trilemma/latex:latest
```

**Inspect provenance attestation:**
```bash
cosign verify-attestation \
  --certificate-identity-regexp="^https://github.com/realnedsanders/Coordination-Trilemma" \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
  --type slsaprovenance \
  ghcr.io/realnedsanders/coordination-trilemma/latex:latest
```

**View SBOM:**
```bash
cosign verify-attestation \
  --certificate-identity-regexp="^https://github.com/realnedsanders/Coordination-Trilemma" \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
  --type spdx \
  ghcr.io/realnedsanders/coordination-trilemma/latex:latest
```

**Inspect image metadata:**
```bash
docker inspect ghcr.io/realnedsanders/coordination-trilemma/latex:latest
```

### PDF Document: `main.pdf`

**Security Features:**
- ✅ Signed with Cosign (keyless signing)
- ✅ SLSA Provenance attestation from GitHub
- ✅ Build metadata embedded in PDF
- ✅ Git commit hash in PDF metadata
- ✅ **Deployed PDF is cryptographically signed** - https://enlightenment.dev serves the signed version

**Verify the published PDF:**
```bash
# Download from enlightenment.dev
curl -O https://enlightenment.dev/main.pdf
curl -O https://enlightenment.dev/main.pdf.cosign.bundle

# Verify signature
cosign verify-blob --bundle main.pdf.cosign.bundle \
  --certificate-identity-regexp="^https://github.com/realnedsanders/Coordination-Trilemma" \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
  main.pdf
```

**Or download from GitHub Actions artifacts:**
```bash
# The signed PDF is also available in GitHub Actions artifacts
# under the name "coordination-trilemma-pdf-signed"
```

**Inspect PDF metadata:**
```bash
# Install pdfinfo (part of poppler-utils)
pdfinfo main.pdf

# Or use exiftool for more detail
exiftool main.pdf | grep -E "(Creator|Producer|Subject|Keywords)"
```

The PDF metadata includes:
- Git commit hash
- Git branch
- Build timestamp
- Build platform (GitHub Actions or local)
- Link to CI build run (for CI-built PDFs)

## Build Provenance Details

### Docker Image Provenance

Each image includes:
1. **OCI Labels** following the OCI Image Spec:
   - `org.opencontainers.image.created` - Build timestamp
   - `org.opencontainers.image.revision` - Git commit SHA
   - `org.opencontainers.image.source` - Repository URL
   - `org.opencontainers.image.version` - Version/tag
   - `io.github.build.url` - Link to GitHub Actions build

2. **SLSA Provenance Attestation** with:
   - Build type
   - Builder identity (GitHub Actions)
   - Build materials (source code, Dockerfile)
   - Build invocation (workflow, parameters)
   - Build metadata (start/end time, reproducibility)

3. **SBOM** listing all installed packages

### PDF Provenance

Embedded in PDF metadata and first page:
- **Full commit hash** in PDF Subject field
- **Git branch** in PDF Keywords
- **Build timestamp** (UTC) in PDF Keywords
- **Build platform** (GitHub Actions or local)
- **CI build URL** (when built in CI)
- **Visible build info** in document footer

## Security Scanning

### Container Vulnerability Scanning

All Docker images are scanned with Trivy for:
- OS package vulnerabilities
- Known CVEs
- Misconfigurations
- Exposed secrets

Results are uploaded to GitHub Security tab.

**Scan locally:**
```bash
docker pull ghcr.io/realnedsanders/coordination-trilemma/latex:latest
trivy image ghcr.io/realnedsanders/coordination-trilemma/latex:latest
```

## Reproducible Builds

### Current Status: Partially Reproducible

**Reproducible:**
- ✅ Source code (git commit hash)
- ✅ Build scripts (versioned in git)
- ✅ Docker image layers (cached and deterministic)

**Non-reproducible (known sources of variation):**
- ⚠️ Build timestamps in PDF
- ⚠️ Font generation timestamps in LaTeX
- ⚠️ Alpine package versions (edge is rolling)

### Improving Reproducibility

To improve reproducibility:
1. Pin Alpine base image to specific digest
2. Pin Alpine package versions
3. Use SOURCE_DATE_EPOCH for timestamps
4. Normalize PDF metadata generation

## Trust Model

### Sigstore Keyless Signing

This project uses **Sigstore's keyless signing** which provides:

1. **No long-lived keys**: No secrets to manage or rotate
2. **OIDC-based**: Uses GitHub's OIDC token for identity
3. **Transparency log**: All signatures recorded in Rekor
4. **Certificate transparency**: Fulcio issues short-lived certificates
5. **Verifiable**: Anyone can verify signatures without contacting us

**Trust chain:**
```
GitHub (OIDC Identity Provider)
    ↓
Fulcio (Certificate Authority)
    ↓
Sign artifact with short-lived certificate
    ↓
Record in Rekor (Transparency Log)
    ↓
Verifiable by anyone
```

### What This Protects Against

✅ **Tampered artifacts**: Signature verification will fail
✅ **Supply chain attacks**: Provenance shows exact build process
✅ **Compromised builds**: Build service identity is cryptographically verified
✅ **Artifact substitution**: Digest verification ensures integrity

## Security Advisories

For security issues, please see our [Security Policy](https://github.com/realnedsanders/Coordination-Trilemma/security/policy).

## Further Reading

- [SLSA Framework](https://slsa.dev/)
- [Sigstore Documentation](https://docs.sigstore.dev/)
- [Cosign](https://github.com/sigstore/cosign)
- [OCI Image Spec](https://github.com/opencontainers/image-spec)
- [GitHub Actions Security](https://docs.github.com/en/actions/security-guides)
