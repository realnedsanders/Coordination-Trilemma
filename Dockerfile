# Minimal Alpine-based LaTeX image for Coordination Trilemma
# Optimized for size and security
# Using edge for access to granular TeXLive packages
FROM alpine:edge

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
