# Coordination Trilemma

A LaTeX document exploring the coordination trilemma.

## 🔐 Security & Provenance

This project achieves **SLSA Build Level 3** with cryptographically signed artifacts:
- ✅ **Docker images** signed with Cosign (keyless)
- ✅ **PDF artifacts** signed with Cosign
- ✅ **SLSA provenance** attestations
- ✅ **SBOM** (Software Bill of Materials)
- ✅ **Build metadata** embedded in artifacts

**Verify artifacts:**
```bash
./verify-signatures.sh
```

For complete security documentation, see **[SECURITY.md](SECURITY.md)**.

## Building Locally

### Using Docker (Recommended)

No local LaTeX installation required:

```bash
# First time setup
make docker-pull

# Build PDF
make

# Quick build (no bibliography update)
make quick

# View PDF
make view
```

### Using Local LaTeX

If you have LaTeX installed locally:

```bash
make local
```

### Cleaning

```bash
# Remove auxiliary files
make clean

# Remove all generated files including PDF
make cleanall
```

## Docker Images

This project uses a custom minimal Alpine-based LaTeX image by default for fast, lightweight builds.

### Custom Alpine Image (Default)
- **Size**: ~500MB-1GB (much smaller than full TeXLive!)
- **Pros**: Alpine edge-based, faster downloads, secure, includes only packages needed for this document
- **Location**: `ghcr.io/realnedsanders/coordination-trilemma/latex:latest`
- **Auto-built**: CI automatically rebuilds when `Dockerfile` changes
- **Usage**: Default when running `make`

### Full TeXLive Image (Alternative)
- **Size**: ~4-5GB
- **Pros**: Includes all LaTeX packages
- **When to use**: If you add packages not included in the custom image

To use the full TeXLive image:

```bash
DOCKER_IMAGE=texlive/texlive:latest make
```

## Continuous Integration

This repository uses GitHub Actions to automatically:
- **Build custom Docker image**: Rebuilds minimal Alpine-based image when Dockerfile changes
- **Lint LaTeX files**: Checks all .tex files using ChkTeX
- **Build the PDF**: Compiles using the custom minimal image
- **Deploy to GitHub Pages**: Publishes the latest PDF with embedded viewer

## GitHub Pages Setup

The CI automatically deploys the latest PDF to GitHub Pages. To enable this:

1. Go to your repository on GitHub
2. Navigate to **Settings** � **Pages**
3. Under **Build and deployment**:
   - **Source**: Select "GitHub Actions"
4. Save the settings

After the next push to `main`, your PDF will be available at:
- **Landing page**: `https://yourusername.github.io/Coordination-Trilemma/`
- **Direct PDF link**: `https://yourusername.github.io/Coordination-Trilemma/main.pdf`

### Customizing the Landing Page

The landing page is defined in `index.html` in the repository root. You can edit this file to customize the appearance, add additional content, or change the styling.

## Project Structure

```
.
├── main.tex                   # Main document file
├── main-article.tex           # Article content
├── appendix-*.tex             # Appendices
├── glossary.tex               # Glossary definitions
├── references.bib             # Bibliography
├── index.html                 # GitHub Pages landing page
├── Dockerfile                 # Custom minimal LaTeX image definition
├── Makefile                   # Build automation
├── generate-build-info.sh     # Build provenance script
├── verify-signatures.sh       # Security verification script
├── SECURITY.md                # Security documentation
└── .github/
    └── workflows/
        ├── ci.yml             # Main CI/CD pipeline (lint, build, deploy)
        ├── docker-build.yml   # Docker image build with signing
        └── sign-pdf.yml       # PDF signing workflow
```

## Requirements

- Docker (for containerized builds)
- OR a local LaTeX installation with pdflatex and bibtex

## Contributing

Changes pushed to `main` will automatically trigger a new build and update the published PDF.
