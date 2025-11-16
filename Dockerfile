# Minimal Alpine-based LaTeX image for Coordination Trilemma
# Optimized for size and security
# Using edge for access to granular TeXLive packages
#
# Note: For maximum security, pin to a specific digest:
# FROM alpine:edge@sha256:xxxxx
# However, Alpine edge is a rolling release, so digests change frequently.
# The image is signed with Cosign and has SLSA provenance attestations.
FROM alpine:edge

# Build arguments for provenance metadata
ARG BUILD_DATE
ARG VCS_REF
ARG VCS_URL
ARG VERSION
ARG BUILD_URL

# OCI labels for build provenance (SLSA-inspired)
LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.authors="B. Escalera, A. Escalera" \
      org.opencontainers.image.url="https://github.com/realnedsanders/Coordination-Trilemma" \
      org.opencontainers.image.documentation="https://github.com/realnedsanders/Coordination-Trilemma/blob/main/README.md" \
      org.opencontainers.image.source="${VCS_URL}" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.vendor="Coordination Trilemma Project" \
      org.opencontainers.image.title="LaTeX Build Environment" \
      org.opencontainers.image.description="Minimal Alpine-based TeXLive image for Coordination Trilemma document" \
      org.opencontainers.image.base.name="alpine:edge" \
      io.github.build.url="${BUILD_URL}"

# Install only the TeXLive packages we actually need
RUN apk add --no-cache \
    # Core LaTeX
    texlive \
    # For amsart document class and ams packages (amsmath, amssymb, amsthm)
    texlive-latexextra \
    # For BibTeX support
    texlive-bibtexextra \
    # Additional packages needed:
    # - geometry, hyperref, url, graphicx, enumitem, booktabs, array, xcolor
    texlive-latexrecommended \
    texlive-pictures \
    # Perl for BibTeX (required by bibtex)
    perl

# Set working directory
WORKDIR /workdir

# Default command
CMD ["/bin/sh"]
