# Minimal Alpine-based LaTeX image for Coordination Trilemma
# Optimized for size and security
FROM alpine:3.19

# Install only the TeXLive packages we actually need
RUN apk add --no-cache \
    # Core LaTeX
    texlive \
    # For amsart document class and ams packages (amsmath, amssymb, amsthm)
    texmf-dist-latexextra \
    # For BibTeX support
    texmf-dist-bibtexextra \
    # For fonts (T1 encoding)
    texmf-dist-fontsextra \
    # Additional packages needed:
    # - geometry, hyperref, url, graphicx, enumitem, booktabs, array, xcolor
    texmf-dist-latexrecommended \
    texmf-dist-pictures \
    # Perl for BibTeX (required by bibtex)
    perl

# Set working directory
WORKDIR /workdir

# Default command
CMD ["/bin/sh"]
